# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-21 14:43
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('board', '0003_computer_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Verif',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tag', models.CharField(max_length=100)),
                ('display_name', models.CharField(max_length=200)),
                ('mandatory', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='VerifType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='VerifValue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(max_length=500)),
                ('verif', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='board.Verif')),
            ],
        ),
        migrations.AddField(
            model_name='verif',
            name='type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='board.VerifType'),
        ),
    ]
