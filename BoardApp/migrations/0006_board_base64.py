# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-11-29 01:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('BoardApp', '0005_auto_20171128_0638'),
    ]

    operations = [
        migrations.AddField(
            model_name='board',
            name='base64',
            field=models.TextField(blank=True),
        ),
    ]
