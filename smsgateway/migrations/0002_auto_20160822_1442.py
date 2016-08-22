# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('smsgateway', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Log',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('status', models.PositiveSmallIntegerField(verbose_name='Status', choices=[(0, 'sent'), (1, 'failed')])),
                ('exception_type', models.CharField(max_length=255, verbose_name='Exception type', blank=True)),
                ('message', models.TextField(verbose_name='Message')),
            ],
            options={
                'verbose_name': 'Log',
                'verbose_name_plural': 'Logs',
            },
        ),
        migrations.AlterModelOptions(
            name='sms',
            options={'verbose_name': 'SMS', 'verbose_name_plural': 'SMSes'},
        ),
        migrations.RemoveField(
            model_name='sms',
            name='direction',
        ),
        migrations.RemoveField(
            model_name='sms',
            name='gateway',
        ),
        migrations.RemoveField(
            model_name='sms',
            name='sent',
        ),
        migrations.AddField(
            model_name='sms',
            name='cost',
            field=models.DecimalField(null=True, max_digits=6, decimal_places=2, blank=True),
        ),
        migrations.AddField(
            model_name='sms',
            name='cost_currency_code',
            field=models.CharField(max_length=4, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='sms',
            name='created',
            field=models.DateTimeField(default=datetime.datetime.now, verbose_name='created'),
        ),
        migrations.AddField(
            model_name='sms',
            name='priority',
            field=models.CharField(default=b'2', max_length=1, choices=[(b'1', b'high'), (b'2', b'medium'), (b'3', b'low'), (b'9', b'deferred')]),
        ),
        migrations.AddField(
            model_name='sms',
            name='status',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Status', db_index=True, choices=[(0, 'sent'), (1, 'failed'), (2, 'delivered')]),
        ),
        migrations.AddField(
            model_name='log',
            name='sms',
            field=models.ForeignKey(related_name='logs', editable=False, to='smsgateway.SMS', verbose_name='SMS'),
        ),
    ]
