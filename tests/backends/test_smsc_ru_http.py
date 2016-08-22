# coding: utf-8
from __future__ import unicode_literals

from unittest import TestCase

from smsgateway.models import SMS
from smsgateway.backends.smsc_ru_http import SMSCHTTPBackend


class SMSCallbackStateTestCase(TestCase):
    def setUp(self):
        self.backend = SMSCHTTPBackend()
        self.sms = SMS.objects.create(to=['79995554433'], content='test', backend=self.backend.get_slug())

    def test_callback(self):
        pass
