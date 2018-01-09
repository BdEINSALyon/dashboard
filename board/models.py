import datetime
from collections import OrderedDict

from django.utils import timezone
from django.db import models
from django.contrib.postgres.fields import JSONField

DISK_GB_DANGER = 20
DISK_GB_WARNING = 50
RAM_MB_DANGER = 512
RAM_MB_WARNING = 1024
TEMP_PROFILES_DANGER = 3
TEMP_PROFILES_WARNING = 1


class Computer(models.Model):
    status = JSONField()
    name = models.CharField(max_length=100)
    last_update = models.DateTimeField(auto_now=True)
    error_mail_sent = models.BooleanField(default=False)
    not_ok_since = models.DateTimeField(default=None, null=True, blank=True)

    def __str__(self):
        return self.name

    def get_sorted_apps(self):
        return self.get_sorted('apps')

    def get_sorted_tasks(self):
        return self.get_sorted('tasks')

    def get_sorted_registry(self):
        return self.get_sorted('registry')

    def get_sorted(self, tag):
        """
        From the status, returns a dictionary sorted by keys.
        """
        reg = self.status.get(tag)

        if not reg:
            return []

        first = next(iter(reg.values()))
        if isinstance(first, dict):
            return OrderedDict(sorted(reg.items(), key=lambda r: r[1].get('name'))).items()
        else:
            return sorted(reg.items())

    def get_os_available(self, tag):
        return self.status.get('os').get(tag).get('available')

    def get_os_percentage(self, tag):
        """
        Get a percentage from the OS sub-section of the status.
        For the moment, either 'disk' or 'ram'.
        The subdictionary needs to have the following keys :
        - total
        - available
        And the values must be integers and in the same unit.
        :param tag: 'disk' or 'ram'
        :return: the percentage of used over total.
        """
        value = self.status.get('os').get(tag)
        total = int(value.get('total'))
        available = int(value.get('available'))
        return int(((total - available) / total) * 100)

    def get_ram_percentage(self):
        return self.get_os_percentage('ram')

    def get_ram_color(self):
        available = self.get_os_available('ram') / 1024

        if available <= RAM_MB_DANGER:
            return 'danger'
        elif available <= RAM_MB_WARNING:
            return 'warning'
        else:
            return 'success'

    @property
    def total_ram(self):
        """
        :return: The total size of RAM, in GB. 
        """
        return int(int(self.status.get('os').get('ram').get('total')) / 1024 / 1024)

    def get_disk_percentage(self):
        return self.get_os_percentage('disk')

    def get_disk_color(self):
        available = round(int(self.get_os_available('disk')) / 1000 / 1000 / 1000)

        if available <= DISK_GB_DANGER:
            return 'danger'
        elif available <= DISK_GB_WARNING:
            return 'warning'
        else:
            return 'success'

    def get_temp_color(self):
        temp = self.status.get('os').get('temp_profiles')
        if temp is None:
            return ''
        if temp >= TEMP_PROFILES_DANGER:
            return 'danger'
        elif temp >= TEMP_PROFILES_WARNING:
            return 'warning'
        else:
            return 'success'

    @property
    def total_disk(self):
        """
        :return: The total size of disk, in GB. 
        """
        return round(int(self.status.get('os').get('disk').get('total')) / 1000 / 1000 / 1000)

    def is_offline(self):
        return self.last_update + datetime.timedelta(minutes=10) < timezone.now()

    def is_ok(self):
        return len(self.issues) == 0

    @property
    def full_name(self):
        full_name = self.name
        description = self.status.get('description')
        if description:
            full_name = ' '.join([full_name, description])

        return full_name

    @property
    def issues(self):
        """
        List all the issues for the computer.
        
        :return: A list of dicts containing all the issues. The dicts always have the key "name" and may have a 
        "reason". 
        """
        issues = []
        if self.get_ram_color() == 'danger':
            issues.append({'name': 'RAM overload'})

        if self.get_disk_color() == 'danger':
            issues.append({'name': 'Disk overload'})

        status = self.status
        printer = status.get('imprimante_ma')
        activated = status.get('windows_activation')
        apps = status.get('apps')
        tasks = status.get('tasks')
        registry = status.get('registry')
        network = status.get('network')
        temp = status.get('os').get('temp_profiles')
        office = status.get('office_activation')

        if not printer:
            issues.append({'name': 'Printer missing'})

        if not activated:
            issues.append({'name': 'Windows not activated'})

        if apps:
            apps_not_ok = missing_mandatory(apps)
            if len(apps_not_ok) > 0:
                for app in apps_not_ok:
                    issues.append({'name': app['name'], 'reason': 'not installed'})
        else:
            issues.append({'name': 'Apps missing'})

        if tasks:
            tasks_not_ok = missing_mandatory(tasks)
            if len(tasks_not_ok) > 0:
                for task in tasks_not_ok:
                    issues.append({'name': task['name'], 'reason': 'missing or disabled'})
        else:
            issues.append({'name': 'Tasks missing'})

        if registry:
            registry_not_ok = missing_mandatory(registry)
            if len(registry_not_ok) > 0:
                for reg in registry_not_ok:
                    issues.append({'name': reg['name'], 'reason': "doesn't have the right value"})
        else:
            issues.append({'name': 'Registry missing'})

        if not network:
            issues.append({'name': 'Network missing'})

        if temp is None:
            issues.append({'name': 'Temporary profiles missing'})

        if not network.get('dhcp'):
            issues.append({'name': 'DHCP not enabled'})

        if temp >= TEMP_PROFILES_DANGER:
            issues.append({'name': 'Too many temporary profiles'})

        # We want to pop an error ONLY if not activated, no error if not reported yet.
        if office == False:
            issues.append({'name': 'Office is not activated'})

        return issues

    def get_color(self):
        return 'success' if self.is_ok() else 'danger'

    @property
    def install_date(self):
        date = self.status['os'].get('install_date')
        if date:
            return datetime.datetime(year=date['year'], month=date['month'], day=date['day'],
                                     hour=date['hour'], minute=date['minute'], second=date['second'])
        else:
            return None


def missing_mandatory(lst):
    mandatory = []
    not_ok = []

    for name, item in lst.items():
        if item.get('mandatory'):
            mandatory.append(item)

    for item in mandatory:
        if not item.get('installed'):
            not_ok.append(item)

    return not_ok


def mandatory_is_ok(lst):
    return len(missing_mandatory(lst)) == 0


class VerifType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Verif(models.Model):
    tag = models.CharField(max_length=100, unique=True)
    display_name = models.CharField(max_length=200)
    mandatory = models.BooleanField(default=True)
    icon = models.CharField(max_length=50, blank=True)

    ICON_TYPE_SOLID = 's'
    ICON_TYPE_REGULAR = 'r'
    ICON_TYPE_BRAND = 'b'

    ICON_TYPES = (
        (ICON_TYPE_SOLID, 'Solid (fas)'),
        (ICON_TYPE_REGULAR, 'Regular (far)'),
        (ICON_TYPE_BRAND, 'Brand (fab)'),
    )
    icon_type = models.CharField(max_length=2, choices=ICON_TYPES, default=ICON_TYPE_SOLID)

    type = models.ForeignKey(
        to=VerifType,
        on_delete=models.CASCADE,
        related_name='verifs'
    )

    def __str__(self):
        return '{0}'.format(
            self.display_name
        )


class ExceptionRule(models.Model):
    value = models.CharField(max_length=100)
    verif = models.ForeignKey(
        to=Verif,
        on_delete=models.CASCADE,
        related_name='exceptionRules'
    )
    reason = models.CharField(max_length=200, blank=True)


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
