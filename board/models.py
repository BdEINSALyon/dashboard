import datetime
from collections import OrderedDict

from django.utils import timezone
from django.db import models
from django.contrib.postgres.fields import JSONField

DISK_DANGER = 90
RAM_DANGER = 90
TEMP_PROFILES_DANGER = 2

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

    def get_sorted_tasks(self):
        tasks = self.status.get('tasks')

        if not tasks:
            return []

        first = next(iter(tasks.values()))
        if isinstance(first, dict):
            return OrderedDict(sorted(tasks.items(), key=lambda app: app[1].get('name'))).items()
        else:
            return sorted(tasks.items())

    def get_ram_percentage(self):
        value = self.status.get('os').get('ram')
        total = int(value.get('total'))
        available = int(value.get('available'))
        return int(((total - available) / total) * 100)

    def get_ram_color(self):
        percentage = self.get_ram_percentage()
        if percentage >= RAM_DANGER:
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
        if percentage >= DISK_DANGER:
            return 'danger'
        elif percentage >= 70:
            return 'warning'
        else:
            return 'success'

    def get_temp_color(self):
        temp = self.status.get('os').get('temp_profiles')
        if temp is None:
            return ''
        if temp >= TEMP_PROFILES_DANGER:
            return 'danger'
        elif temp >= 1:
            return 'warning'
        else:
            return 'success'

    @property
    def total_disk(self):
        return round(int(self.status.get('os').get('disk').get('total')) / 1000 / 1000 / 1000)

    def is_offline(self):
        return self.last_update + datetime.timedelta(minutes=10) < timezone.now()

    def is_ok(self):
        if self.get_ram_percentage() > RAM_DANGER:
            return False

        if self.get_disk_percentage() > DISK_DANGER:
            return False

        status = self.status
        printer = status.get('imprimante_ma')
        activated = status.get('windows_activation')
        apps = status.get('apps')
        tasks = status.get('tasks')
        network = status.get('network')
        temp = status.get('os').get('temp_profiles')

        if not (printer and activated and apps and tasks and network) or temp is None:
            return False

        return network.get('dhcp') and temp < TEMP_PROFILES_DANGER and mandatory_is_ok(apps) and mandatory_is_ok(tasks)


def mandatory_is_ok(lst):
    mandatory = []
    for name, item in lst.items():
        if item.get('mandatory'):
            mandatory.append(item)

    mandatory_ok = True
    for item in mandatory:
        mandatory_ok = mandatory_ok and item.get('installed')

    return mandatory_ok


class VerifType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Verif(models.Model):
    tag = models.CharField(max_length=100)
    display_name = models.CharField(max_length=200)
    mandatory = models.BooleanField(default=True)
    type = models.ForeignKey(
        to=VerifType,
        on_delete=models.CASCADE,
        related_name='verifs'
    )

    def __str__(self):
        return '{0}'.format(
            self.display_name
        )


class VerifValue(models.Model):
    value = models.CharField(max_length=500)
    verif = models.ForeignKey(
        to=Verif,
        on_delete=models.CASCADE,
        related_name='verifValues'
    )

    def __str__(self):
        return '{0} - {1}'.format(
            self.verif,
            self.value
        )
