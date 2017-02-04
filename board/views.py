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
    context_object_name = 'computer_list'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context

    def get_queryset(self):
        return Computer.objects.all().order_by('name')

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

