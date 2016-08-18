# coding: utf-8
from __future__ import unicode_literals
from django.http import HttpResponse
from django.utils.encoding import smart_str
from django.utils.http import urlencode

import string

from smsgateway.backends.base import SMSBackend


class SMSCHTTPBackend(SMSBackend):
    """
    smsc.ru api
    """
    def get_send_url(self, sms_request, account_dict):
        # Encode message

        sender = account_dict.get('sender') or ''
        sender = ''.join(c for c in sender if c in string.ascii_letters + string.digits + " _")

        msg = sms_request.msg
        try:
            msg = smart_str(msg)
        except:
            pass

        querystring = urlencode({
            'login': account_dict['username'],
            'psw': account_dict['password'],
            'phones': ';'.join(sms_request.to),
            'charset': 'utf-8',
            'mes': msg,
            'sender': sender,
        })
        return 'https://smsc.ru/sys/send.php?%s' % querystring

    def validate_send_result(self, result):
        #TODO parse result
        return 'OK' in result

    def handle_incoming(self, request, reply_using=None):
        """
        Обработка входящих. Пока никак.
        :param request:
        :param reply_using:
        :return:
        """
        return HttpResponse('')

    def get_slug(self):
        return 'smsc_http'

    def get_url_capacity(self):
        return 20