# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('smsgateway', '0004_auto_20160823_1942'),
    ]

    operations = [
        migrations.AddField(
            model_name='queuedsms',
            name='meta',
            field=jsonfield.fields.JSONField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='queuedsms',
            name='scheduled',
            field=models.DateTimeField(db_index=True, null=True, verbose_name='The scheduled sending time', blank=True),
        ),
        migrations.AddField(
            model_name='queuedsms',
            name='tag',
            field=models.CharField(max_length=64, null=True, blank=True),
        ),
    ]
