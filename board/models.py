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

    def get_disk_percentage(self):
        value = self.status.get('os').get('disk')
        total = int(value.get('total'))
        available = int(value.get('available'))
        return int(((total - available) / total) * 100)

    def is_offline(self):
        return self.last_update + datetime.timedelta(minutes=10) < timezone.now()

    def is_ok(self):
        status = self.status
        printer = status.get('imprimante_ma')
        shutdown = status.get('shutdown')
        apps = status.get('apps')

        if apps:
            office = apps.get('office')
            antivirus = apps.get('antivirus')
            return printer and shutdown and office and antivirus
        else:
            return False

