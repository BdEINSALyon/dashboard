from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from board.views import ComputerListView, update_computer

urlpatterns = [
    url(r'^$', ComputerListView.as_view(), name='computers'),
    url(r'^update$', login_required(update_computer), name='computer-update'),
]
