# coding: utf-8
from __future__ import unicode_literals
from django.conf import settings

SMSGATEWAY_SENDER = getattr(settings, 'SMSGATEWAY_SENDER', None)
