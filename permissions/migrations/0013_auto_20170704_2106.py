# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-07-04 21:06
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('permissions', '0012_auto_20170704_1345'),
    ]

    operations = [
        migrations.AlterField(
            model_name='azuregroup',
            name='group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='azure_groups', to='auth.Group'),
        ),
    ]
