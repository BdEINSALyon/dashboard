# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-07-03 17:39
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('permissions', '0004_auto_20170703_1653'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='azure_groups',
        ),
    ]
