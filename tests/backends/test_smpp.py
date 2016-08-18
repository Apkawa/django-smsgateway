# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import subprocess
from unittest import skip

import os
from unittest import TestCase

from django.conf import settings


from smsgateway import send
from smsgateway.backends.smpp import SMPPBackend
from smsgateway.models import SMS
from smsgateway.sms import SMSRequest
from smsgateway.utils import check_cell_phone_number, truncate_sms
from smsgateway.smpplib.client import (SMPP_CLIENT_STATE_CLOSED,
                                       SMPP_CLIENT_STATE_OPEN,
                                       SMPP_CLIENT_STATE_BOUND_TX,
                                       SMPP_CLIENT_STATE_BOUND_RX,
                                       SMPP_CLIENT_STATE_BOUND_TRX)

SMPPSIM_DIR = os.path.join(settings.TEST_ROOT, 'SMPPSim')

req_data = {
    'to': '+32000000004;+32000000002;+32000000003',
    'msg': 'text of the message',
    'signature': 'cropped to 11 chars'
}


class SMPPTestMixin(object):
    @classmethod
    def setUpClass(self):
        print("Launch SMPPSim service for testing... ")
        subprocess.Popen(['/bin/sh', os.path.join(SMPPSIM_DIR, 'do_start.sh')],
            stdout=open('/dev/null', 'w'),
            stderr=subprocess.STDOUT,
            cwd=SMPPSIM_DIR).wait()
        assert os.path.exists(os.path.join(SMPPSIM_DIR, 'service.pid')), "Not run SMPPSim"

    @classmethod
    def tearDown(self):
        print("Stopping SMPPSim service... ")
        subprocess.Popen(['/bin/sh', os.path.join(SMPPSIM_DIR, 'do_stop.sh')],
            cwd=SMPPSIM_DIR).wait()
        assert not os.path.exists(os.path.join(SMPPSIM_DIR, 'service.pid')), "SMPPSim not stoping"


class SMPPBackendTestCase(TestCase):
    def setUp(self):
        super(SMPPBackendTestCase, self).setUp()
        self.backend = SMPPBackend()

    def test_init(self):
        for key in ['client', 'sender', 'sms_data_iter', 'sent_smses']:
            self.assert_(key in self.backend.__dict__.keys())

    def test_initialize_without_sms_request(self):
        self.assert_(self.backend._initialize(None) == False)

    def test_initialize_with_sms_request(self):
        sms_request = SMSRequest(**req_data)
        self.assert_(self.backend._initialize(sms_request) == True)

    def test_get_sms_list(self):
        sms_list = self.backend._get_sms_list(SMSRequest(**req_data))
        self.assert_(len(sms_list) == 3)
        for to, sms in zip(req_data['to'].split(';'), sms_list):
            self.assert_(sms.to[0] == check_cell_phone_number(to))
            self.assert_(sms.msg == truncate_sms(req_data['msg']))
            self.assertEqual(sms.signature,
                req_data['signature'][:len(sms.signature)])

    def test_connect(self):
        self.assert_(self.backend.client == None)
        account_dict = settings.SMSGATEWAY_ACCOUNTS['smpp']
        self.backend._connect(account_dict)
        self.assert_(self.backend.client != None)
        self.assert_(self.backend.client.receiver_mode == True)
        self.assert_(self.backend.client.state == SMPP_CLIENT_STATE_BOUND_TRX)

    def test_connect_when_bind_fails(self):
        from mock import patch
        from smsgateway.smpplib.client import Client
        self.assert_(self.backend.client == None)
        patcher = patch.object(Client, 'bind_transceiver')
        account_dict = settings.SMSGATEWAY_ACCOUNTS['smpp']
        with patcher as raise_exception:
            raise_exception.side_effect = Exception('Meeeck')
            self.backend._connect(account_dict)
        self.assert_(self.backend.client != None)
        self.assert_(self.backend.client.receiver_mode == False)
        self.assert_(self.backend.client.state == SMPP_CLIENT_STATE_CLOSED)

class SMPPSendTestCase(TestCase):

    @skip("TODO FIX")
    def test_send_single_sms(self):
        self.assertEqual(SMS.objects.count(), 0)
        send('+32000000001', 'testing message', 'the signature', using='smpp')
        self.assertEqual(SMS.objects.count(), 1)
        sms = SMS.objects.get()
        self.assertEqual(sms.content, 'testing message')
        self.assertEqual(sms.to, '32000000001')
        self.assertEqual(sms.sender, 'the signature'[:len(sms.sender)])

    @skip("TODO FIX")
    def test_send_multiple_separated_sms(self):
        self.assert_(SMS.objects.count() == 0)
        send(req_data['to'], req_data['msg'], req_data['signature'],
            using='smpp')
        self.assertEqual(SMS.objects.count(), 3)
        smses = SMS.objects.all()
        for to, sms in zip(req_data['to'].split(';'), smses):
            self.assertEqual(sms.to, check_cell_phone_number(to))
            self.assertEqual(sms.content, truncate_sms(req_data['msg']))
            self.assertEqual(sms.sender, req_data['signature'][:len(sms.sender)])
            self.assertEqual(sms.backend, 'smpp')
