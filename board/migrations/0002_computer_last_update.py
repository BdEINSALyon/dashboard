# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-01-19 17:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('board', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='computer',
            name='last_update',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
