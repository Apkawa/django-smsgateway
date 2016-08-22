# coding: utf-8
from __future__ import unicode_literals

import json
from six import text_type

from django.http import Http404
from django.http import HttpResponse, HttpResponseBadRequest
from django.utils.encoding import smart_str
from django.utils.http import urlencode

import string

from smsgateway.models import SMS, STATUS

from smsgateway.backends.base import SMSBackend


class SMSCHTTPBackend(SMSBackend):
    """
    smsc.ru api
    """

    def get_send_url(self, sms, account_dict):
        # Encode message
        sender = sms.sender
        sender = ''.join(c for c in sender if c in string.ascii_letters + string.digits + " _")

        msg = sms.content
        try:
            msg = smart_str(msg)
        except:
            pass

        querystring = urlencode({
            'login': account_dict['username'],
            'psw': account_dict['password'],
            'phones': ';'.join(sms.to),
            'charset': 'utf-8',
            'mes': msg,
            'sender': sender,
            "fmt": 3,
            "cost": 2,
            "id": sms.gateway_ref,
        })
        return 'https://smsc.ru/sys/send.php?%s' % querystring

    def parse_result(self, result):
        return json.loads(result)

    def validate_send_result(self, parsed_result):
        return parsed_result.get('id')

    def get_cost(self, sms, parsed_result):
        return parsed_result.get('cost')

    def get_cost_currency(self, sms, parsed_result):
        return 'RUB'

    def handle_callback(self, request):
        """
        Обработка входящих. Пока никак.
        :param request:
        :param reply_using:
        :return:
        """
        data = request.POST

        if data.get('mes'):
            # Входящая смс
            return HttpResponse('')

        if not data:
            return HttpResponseBadRequest("Empty post")

        # статус смс
        try:
            sms = SMS.objects.get(gateway_ref=data['id'])
        except SMS.DoesNotExist:
            raise Http404("Not found sms")

        message = json.dumps(data)
        if data.get('err') is None or text_type(data['err']) == '0':
            status = STATUS.delivered
        else:
            status = STATUS.rejected

        sms.logs.create(status=status, message=message)
        sms.status = status
        sms.save()

        return HttpResponse('OK')

    def get_slug(self):
        return 'smsc_http'

    def get_url_capacity(self):
        return 1
