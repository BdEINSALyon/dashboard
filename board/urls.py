from django.conf.urls import url

from board.views import ComputerListView

urlpatterns = [
    url(r'^$', ComputerListView.as_view(), name='computer-list'),
]
