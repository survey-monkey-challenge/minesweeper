# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-05-29 23:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0009_auto_20160529_2025'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='creation_datetime',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]