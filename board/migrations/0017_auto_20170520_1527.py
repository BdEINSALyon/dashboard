# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-05-20 13:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('board', '0016_computer_not_ok_since'),
    ]

    operations = [
        migrations.AlterField(
            model_name='computer',
            name='not_ok_since',
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
    ]
