from django.db import models
from django.contrib.postgres.fields import JSONField


class Computer(models.Model):
    status = JSONField()
    last_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.status.get('name', 'UNKNOWN')

    def get_ram_percentage(self):
        value = self.status.get('os').get('ram')
        return int((value.get('available') / value.get('total')) * 100)

    def get_disk_percentage(self):
        value = self.status.get('os').get('disk')
        return int((value.get('available') / value.get('total')) * 100)
