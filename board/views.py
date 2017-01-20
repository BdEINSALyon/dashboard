from django.shortcuts import render

# Create your views here.
from django.views.generic import ListView

from board.models import Computer


class ComputerListView(ListView):
    template_name = 'board/computer.html'
    context_object_name = 'computer_list'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # computers = self.get_queryset()
        # context['ram'] = {}
        # context['disk'] = {}
        #
        # for computer in computers:
        #     context['ram'][computer] = computer.get_ram_percentage()
        #     context['disk'][computer] = computer.get_disk_percentage()

        return context

    def get_queryset(self):
        return Computer.objects.all()
