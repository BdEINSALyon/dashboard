from django import forms


class FiltersForm(forms.Form):
    ONLINE = 'online'
    OFFLINE = 'offline'
    ISSUES = 'issues'
    OK = 'ok'
    NONE = 'none'

    ON_OFFLINE_CHOICES = [
        (ONLINE, 'En ligne'),
        (OFFLINE, 'Hors ligne'),
        (NONE, 'Non spécifié'),
    ]

    OK_ISSUES_CHOICES = [
        (ISSUES, 'Problèmes'),
        (OK, 'Ok'),
        (NONE, 'Non spécifié'),
    ]

    status = forms.ChoiceField(choices=ON_OFFLINE_CHOICES, widget=forms.RadioSelect, label='En ligne')
    issues = forms.ChoiceField(choices=OK_ISSUES_CHOICES, widget=forms.RadioSelect, label='Problèmes')
    apply = forms.BooleanField(required=False, label='Appliquer')
