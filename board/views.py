# Create your views here.
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from django.views.decorators.csrf import csrf_exempt

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
        computer.save()
        return HttpResponse(status=200)
    else:
        return HttpResponse(status=400)

