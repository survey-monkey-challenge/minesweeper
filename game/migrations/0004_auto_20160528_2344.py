# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-05-28 23:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0003_auto_20160528_2247'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='difficulty',
            field=models.CharField(blank=True, choices=[('0', 'Easy'), ('1', 'Normal'), ('2', 'Hard')], default=0, max_length=2, null=True),
        ),
    ]
