# coding: utf-8
from __future__ import unicode_literals

import requests
import json

from django.utils import timezone
from six import text_type

from django.http import Http404
from django.http import HttpResponse, HttpResponseBadRequest
from django.utils.encoding import smart_str
from django.utils.http import urlencode

import string

from smsgateway.models import SMS, STATUS

from smsgateway.backends.base import SMSBackend
from smsgateway.utils import grouper


# TODO console log

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
        base_url = account_dict.get("base_url", "https://smsc.ru")
        return '%s/sys/send.php?%s' % (base_url, querystring)

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
        Обработка колбэков. Пока никак.
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
        except SMS.MultipleObjectsReturned as e:
            raise Http404("Multiple sms: %s" % e)

        message = json.dumps(data)
        if data.get('err') is None or text_type(data['err']) == '0':
            status = STATUS.delivered
        else:
            status = STATUS.rejected

        sms.logs.create(status=status, message=message)
        sms.status = status
        sms.save()

        return HttpResponse('OK')

    def _cron_update_sms_statuses(self, account_dict, **kwargs):
        """
        https://smsc.ru/api/http/status_messages/check_status/
        :param account_dict:
        :param kwargs:
        :return:
        """
        since = kwargs.get('from_datetime') or timezone.now() - timezone.timedelta(days=2)

        sended_sms = list(SMS.objects.filter(
            backend=account_dict['backend'],
            status=STATUS.sent,
            created__gte=since

        ).order_by('-created'))

        max_chunks = kwargs.get('chunk_size', 10)

        for sms_chunk in grouper(sended_sms, max_chunks):
            sms_ref_map = {s.gateway_ref: s for s in sms_chunk}

            pairs = [(s.gateway_ref, s.to[0]) for s in sms_chunk]

            querystring = urlencode({
                'login': account_dict['username'],
                'psw': account_dict['password'],
                'charset': 'utf-8',
                'all': 1,
                "fmt": 3,
                "id": ','.join([ref for ref, phone in pairs]) + ',',
                "phone": ','.join([phone for ref, phone in pairs]) + ',',
            })
            base_url = account_dict.get("base_url", "https://smsc.ru")
            request_url = '%s/sys/status.php?%s' % (base_url, querystring)
            response = requests.get(request_url)
            data = response.json()

            if isinstance(data, dict) and data.get('status') <= 0 or 'error' in data:
                raise ValueError(data)

            for info in data:

                if info['status'] < 1:
                    #
                    continue

                sms = sms_ref_map[info['id']]
                if info['status'] in [1, 2]:
                    status = STATUS.delivered
                else:
                    status = STATUS.rejected
                message = json.dumps(info)
                sms.logs.create(status=status, message=message)
                sms.status = status
                sms.save(update_fields=['status'])

    def handle_cron(self, account_dict, task=None, **kwargs):
        if task == 'status' or not task:
            self._cron_update_sms_statuses(account_dict, **kwargs)

    def get_slug(self):
        return 'smsc_http'

    def get_url_capacity(self):
        return 1
