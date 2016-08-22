# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
import smsgateway.fields


class Migration(migrations.Migration):

    dependencies = [
        ('smsgateway', '0002_auto_20160822_1442'),
    ]

    operations = [
        migrations.CreateModel(
            name='InboundSMS',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cost', models.DecimalField(null=True, max_digits=6, decimal_places=2, blank=True)),
                ('cost_currency_code', models.CharField(max_length=4, null=True, blank=True)),
                ('created', models.DateTimeField(default=datetime.datetime.now, verbose_name='created')),
                ('content', models.TextField(help_text='SMS content', verbose_name='content')),
                ('sender', models.CharField(max_length=32, verbose_name='sender', db_index=True)),
                ('to', smsgateway.fields.SeparatedField(db_index=True, max_length=32, verbose_name='receiver', blank=True)),
                ('operator', models.IntegerField(default=0, verbose_name='Originating operator', choices=[(0, 'Unknown'), (1, 'Proximus'), (2, 'Mobistar'), (3, 'Base'), (999, 'Other')])),
                ('backend', models.CharField(default='unknown', max_length=32, verbose_name='backend', db_index=True)),
                ('gateway_ref', models.CharField(help_text='A reference id for the gateway', max_length=32, verbose_name='gateway reference', blank=True)),
                ('status', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Status', db_index=True, choices=[(0, 'sent'), (1, 'failed'), (2, 'delivered')])),
                ('priority', models.CharField(default=b'2', max_length=1, choices=[(b'1', b'high'), (b'2', b'medium'), (b'3', b'low'), (b'9', b'deferred')])),
            ],
            options={
                'verbose_name': 'Inbound SMS',
                'verbose_name_plural': 'Inbound SMSes',
            },
        ),
        migrations.AlterField(
            model_name='sms',
            name='to',
            field=smsgateway.fields.SeparatedField(db_index=True, max_length=32, verbose_name='receiver', blank=True),
        ),
    ]
