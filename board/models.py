import datetime
from collections import OrderedDict

from django.utils import timezone
from django.db import models
from django.contrib.postgres.fields import JSONField


class Computer(models.Model):
    status = JSONField()
    name = models.CharField(max_length=100)
    last_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def get_sorted_apps(self):
        apps = self.status.get('apps')

        if not apps:
            return []

        first = next(iter(apps.values()))
        if isinstance(first, dict):
            return OrderedDict(sorted(apps.items(), key=lambda app: app[1].get('name'))).items()
        else:
            return sorted(apps.items())

    def get_ram_percentage(self):
        value = self.status.get('os').get('ram')
        total = int(value.get('total'))
        available = int(value.get('available'))
        return int(((total - available) / total) * 100)

    def get_ram_color(self):
        percentage = self.get_ram_percentage()
        if percentage >= 90:
            return 'danger'
        elif percentage >= 70:
            return 'warning'
        else:
            return 'success'

    @property
    def total_ram(self):
        return int(int(self.status.get('os').get('ram').get('total')) / 1024 / 1000)

    def get_disk_percentage(self):
        value = self.status.get('os').get('disk')
        total = int(value.get('total'))
        available = int(value.get('available'))
        return int(((total - available) / total) * 100)

    def get_disk_color(self):
        percentage = self.get_disk_percentage()
        if percentage >= 90:
            return 'danger'
        elif percentage >= 70:
            return 'warning'
        else:
            return 'success'

    @property
    def total_disk(self):
        return round(int(self.status.get('os').get('disk').get('total')) / 1000 / 1000 / 1000)

    def is_offline(self):
        return self.last_update + datetime.timedelta(minutes=10) < timezone.now()

    def is_ok(self):
        status = self.status
        printer = status.get('imprimante_ma')
        shutdown = status.get('shutdown')
        activated = status.get('windows_activation')
        apps = status.get('apps')

        if not (printer and shutdown and activated and apps):
            return False

        mandatory_apps = []
        for name, app in apps.items():
            if app.get('mandatory'):
                mandatory_apps.append(app)

        mandatory_apps_ok = True
        for app in mandatory_apps:
            mandatory_apps_ok = mandatory_apps_ok and app.get('installed')

        return mandatory_apps_ok

