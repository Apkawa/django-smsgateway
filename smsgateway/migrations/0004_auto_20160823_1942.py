# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('smsgateway', '0003_auto_20160822_1516'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inboundsms',
            name='status',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Status', db_index=True, choices=[(0, 'sent'), (1, 'failed'), (2, 'delivered'), (3, 'rejected')]),
        ),
        migrations.AlterField(
            model_name='log',
            name='status',
            field=models.PositiveSmallIntegerField(verbose_name='Status', choices=[(0, 'sent'), (1, 'failed'), (2, 'delivered'), (3, 'rejected')]),
        ),
        migrations.AlterField(
            model_name='sms',
            name='status',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Status', db_index=True, choices=[(0, 'sent'), (1, 'failed'), (2, 'delivered'), (3, 'rejected')]),
        ),
    ]
