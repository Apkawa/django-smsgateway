# coding: utf-8
from __future__ import unicode_literals

import django.dispatch

send_queued_sms = django.dispatch.Signal(providing_args=["responses", "queued_sms"])