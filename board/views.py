# Create your views here.
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

        utc = pytz.utc

        if computer.is_ok():
            computer.not_ok_since = None
        elif computer.not_ok_since is None:
            computer.not_ok_since = utc.localize(datetime.datetime.now())

        dest = os.getenv('MAIL_DEST', None)

        interval = None
        if computer.not_ok_since is not None:
            interval = utc.localize(datetime.datetime.now()) - computer.not_ok_since

        if not computer.is_ok() or (interval and interval > datetime.timedelta(minutes=59) and dest):
            domain = os.getenv('MAILGUN_DOMAIN')
            api_key = os.getenv('MAILGUN_API_KEY')

            mail_template = get_template('board/mail/error.html')
            mail_html = mail_template.render({'computer': computer})

            requests.post(
                "https://api.mailgun.net/v3/{0}/messages".format(domain),
                auth=("api", api_key),
                data={
                    "from": "Dashboard <noreply@mg.bde-insa-lyon.fr>",
                    "to": dest.split(','),
                    "subject": "{0} not OK".format(computer.name),
                    "html": mail_html,
                    "o:tracking-clicks": "no",
                    "o:tracking-opens": "no",
                    "o:tracking": "no"
                }
            )

            computer.not_ok_since = None

        computer.save()

        return HttpResponse(status=200)
    else:
        return HttpResponse(status=400)
