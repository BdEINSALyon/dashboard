from django.conf.urls import url

from board.views import ComputerListView, update_computer, ComputerIssuesListView

urlpatterns = [
    url(r'^$', ComputerListView.as_view(), name='computers'),
    url(r'^issues', ComputerIssuesListView.as_view(), name='computers_issues'),
    url(r'^update$', update_computer, name='computer-update'),
]
