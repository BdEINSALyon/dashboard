import datetime
from django.utils import timezone
from django.db import models
from django.contrib.postgres.fields import JSONField


class Computer(models.Model):
    status = JSONField()
    last_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.status.get('name', 'UNKNOWN')

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
        return self.last_update + datetime.timedelta(minutes=30) < timezone.now()

