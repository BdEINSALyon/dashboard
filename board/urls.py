from django.conf.urls import url

from board.views import ComputerListView, update_computer

urlpatterns = [
    url(r'^$', ComputerListView.as_view(), name='computer-list'),
    url(r'^update$', update_computer, name='computer-update'),
]
