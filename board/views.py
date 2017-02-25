# Create your views here.
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from django.views.decorators.csrf import csrf_exempt

import json

from board.models import Computer


class ComputerListView(ListView):
    template_name = 'board/computer.html'
    context_object_name = 'computers'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['issues'] = False
        return context

    def get_queryset(self):
        return Computer.objects.order_by('name')

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class ComputerIssuesListView(ComputerListView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['issues'] = True
        return context

    def get_queryset(self):
        computers = super().get_queryset()
        return [computer for computer in computers if not computer.is_ok()]


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

