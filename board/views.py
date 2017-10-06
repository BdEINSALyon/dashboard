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
from board.logging import send_mail
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
        client_ip = get_client_ip(request)
        log.debug('Received POST request from %s', client_ip)
        status = json.loads(request.body.decode("utf-8"))
        if not validate_status(status):
            log.warning('Invalid status received')
            return HttpResponse(status=400)

        name = status['name']

        logged = False

        try:
            computer = Computer.objects.get(name=name)
        except Computer.DoesNotExist:
            try:
                computer = Computer.objects.get(status__name=name)
                computer.name = name
            except Computer.DoesNotExist:
                computer = Computer(name=name)
                log.warning('Created new computer %s from %s (%s)', name, client_ip, request.user)
                logged = True
        computer.status = status

        if not logged:
            log.info('Updating %s from %s (%s)', computer.name, client_ip, request.user)

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
        return HttpResponse(status=405)


def get_client_ip(request):
    # Retrieving client ip
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        client_ip = x_forwarded_for.split(',')[0]
    else:
        client_ip = request.META.get('REMOTE_ADDR')
    return client_ip


def validate_status(status):
    required_keys = {'imprimante_ma', 'windows_activation', 'apps', 'tasks', 'registry', 'network', 'os',
                     'office_activation', 'apps', 'description', 'name', 'network', 'tasks'}
    if not required_keys <= status.keys():
        log.warning('missing key(s) in status %s', required_keys - status.keys())
        return False

    required_keys = {'disk', 'ram', 'install_date', 'temp_profiles', 'total_sessions'}
    if not required_keys <= status['os'].keys():
        log.warning('missing key(s) in status.os %s', required_keys - status['os'].keys())
        return False

    required_keys = {'dhcp', 'ip', 'mac'}
    if not required_keys <= status['network'].keys():
        log.warning('missing key(s) in status.network %s', required_keys - status['network'].keys())
        return False

    required_keys = {'icon', 'installed', 'mandatory', 'name', 'verification'}
    for _, app in status['apps'].items():
        if not required_keys <= app.keys():
            log.warning('missing key(s) in status.apps.%s %s', app, required_keys - app.keys())
            return False

    for _, task in status['tasks'].items():
        if not required_keys <= task.keys():
            log.warning('missing key(s) in status.tasks.%s %s', task, required_keys - task.keys())
            return False

    for _, reg in status['registry'].items():
        if not required_keys <= reg.keys():
            log.warning('missing key(s) in status.registry.%s %s', reg, required_keys - reg.keys())
            return False

    return True
