# Create your views here.
import logging
import os

import pytz
import requests
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template.loader import get_template
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from django.views.decorators.csrf import csrf_exempt

import datetime

import json

from board.forms import FiltersForm
from board.models import Computer

log = logging.getLogger('dashboard')


class ComputerListView(ListView):
    template_name = 'board/computer.html'
    context_object_name = 'computers'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        apply_filters = self.request.GET.get('apply', None)

        issues = self.request.GET.get('issues', None)
        status = self.request.GET.get('status', None)

        # Set Form
        if issues or status or apply_filters:
            context['filters_form'] = FiltersForm(self.request.GET)
        else:
            context['filters_form'] = FiltersForm(initial={
                'status': FiltersForm.NONE,
                'issues': FiltersForm.NONE,
                'apply': True
            })

        # Set title
        if apply_filters:
            title = []

            if FiltersForm.ISSUES in issues:
                title.append('Problèmes')
            elif FiltersForm.OK in issues:
                title.append('Ok')

            if FiltersForm.OFFLINE in status:
                title.append('Hors ligne')
            if FiltersForm.ONLINE in status:
                title.append('En ligne')

            title = ' - '.join(title)
        else:
            title = 'Tout'

        context['title'] = title

        return context

    def get_queryset(self):
        computers = Computer.objects.order_by('name')

        apply_filters = self.request.GET.getlist('apply', None)

        if apply_filters:
            issues = self.request.GET.get('issues', None)
            if FiltersForm.ISSUES in issues:
                computers = [computer for computer in computers if not computer.is_ok()]
            elif FiltersForm.OK in issues:
                computers = [computer for computer in computers if computer.is_ok()]

            status = self.request.GET.get('status', None)
            if FiltersForm.OFFLINE in status:
                computers = [computer for computer in computers if computer.is_offline()]
            if FiltersForm.ONLINE in status:
                computers = [computer for computer in computers if not computer.is_offline()]

        return computers

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


@csrf_exempt
def update_computer(request):
    """
    Update a computer from the JSON given.
    This sends mails if needed :
    - If a computer has an issue for more than a hour
    - If a computer is back to normal
    """
    if request.method == 'POST':
        status = json.loads(request.body.decode("utf-8"))
        name = status['name']
        try:
            computer = Computer.objects.get(name=name)
        except Computer.DoesNotExist:
            try:
                computer = Computer.objects.get(status__name=name)
                computer.name = name
            except Computer.DoesNotExist:
                computer = Computer(name=name)
        computer.status = status

        # Retrieving client ip
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            client_ip = x_forwarded_for.split(',')[0]
        else:
            client_ip = request.META.get('REMOTE_ADDR')
        log.info('Updating %s from %s', computer.name, client_ip)

        utc = pytz.utc

        dest = os.getenv('MAIL_DEST', None)

        if computer.is_ok():
            # If it's a "back to normal", then we send a mail.
            if computer.error_mail_sent:
                subject = "{0} back to normal".format(computer.name)
                mail_template = get_template('board/mail/normal.html')
                mail_html = mail_template.render({'computer': computer})

                send_mail(subject, dest, mail_html)

            computer.error_mail_sent = False
            computer.not_ok_since = None

        elif computer.not_ok_since is None:
            computer.not_ok_since = utc.localize(datetime.datetime.now())

        interval = None
        if computer.not_ok_since is not None:
            interval = utc.localize(datetime.datetime.now()) - computer.not_ok_since

        if interval and interval > datetime.timedelta(minutes=59) and dest:
            # Send a mail if not ok for more than a hour.
            mail_template = get_template('board/mail/error.html')
            mail_html = mail_template.render({'computer': computer})
            subject = "{0} not OK".format(computer.name)

            if computer.error_mail_sent:
                subject = "{0} still not OK".format(computer.name)

            send_mail(subject, dest, mail_html)

            computer.error_mail_sent = True
            computer.not_ok_since = None

        computer.save()

        return HttpResponse(status=200)
    else:
        return HttpResponse(status=400)


def send_mail(subject, dest, mail_html):
    domain = os.getenv('MAILGUN_DOMAIN')
    api_key = os.getenv('MAILGUN_API_KEY')

    requests.post(
        "https://api.mailgun.net/v3/{0}/messages".format(domain),
        auth=("api", api_key),
        data={
            "from": "Dashboard <noreply@mg.bde-insa-lyon.fr>",
            "to": dest.split(','),
            "subject": subject,
            "html": mail_html,
            "o:tracking-clicks": "no",
            "o:tracking-opens": "no",
            "o:tracking": "no"
        }
    )
