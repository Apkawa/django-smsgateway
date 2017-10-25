import logging
import datetime
import re

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import get_callable

from smsgateway.compat import urllib2
from smsgateway.models import SMS, STATUS
from smsgateway.utils import get_random_string

logger = logging.getLogger(__name__)

try:
    all_hooks = settings.SMSGATEWAY_HOOK
except:
    raise ImproperlyConfigured('No SMSGATEWAY_HOOK defined.')


class SMSBackend(object):
    def send(self, sms_request, account_dict):
        """
        Send an SMS message to one or more recipients, and create entries in the
        SMS table for each successful attempt.
        """
        capacity = self.get_url_capacity()
        sender = u'[%s]' % self.get_slug() if not sms_request.signature else sms_request.signature

        # Split SMSes into batches depending on the capacity
        requests = []
        while len(sms_request.to) > 0:
            sms = SMS(
                sender=sender,
                content=sms_request.msg,
                to=sms_request.to[:capacity],
                backend=self.get_slug(),
            )
            sms.gateway_ref = self.build_gateway_ref(sms)
            requests.append(sms)
            del sms_request.to[:capacity]

        # Send each batch
        responses = []
        for request in requests:
            res_data = {'request': request, 'objects': None}

            url = self.get_send_url(request, account_dict)
            if not url:
                continue

            logger.debug('Sending SMS using: %s' % url)

            # Make request to provider
            response = status = None
            message = exception_type = ''
            try:
                try:
                    sock = urllib2.urlopen(url)
                    response = sock.read()
                    sms.status = status = STATUS.sent
                    message = response

                    sock.close()
                except Exception as e:
                    logger.exception("Send fail")

                    sms.status = status = STATUS.failed
                    message = str(e)
                    exception_type = type(e).__name__

                logger.debug('Result: %s' % response)
                parsed_response = self.parse_result(response)

                if not self.validate_send_result(parsed_response):
                    status = STATUS.failed
                self.process_response(sms, parsed_response)

                res_data['result'] = parsed_response
                res_data['object'] = sms
                responses.append(res_data)
            finally:
                sms.save()
                sms.logs.create(
                    status=status,
                    message=message,
                    exception_type=exception_type
                )

        return responses

    def build_gateway_ref(self, sms):
        sms_to = u''.join(sms.to)
        now_str = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        return ('%s%s%s' % (sms_to, now_str, get_random_string(length=4)))[:32]

    def get_send_url(self, sms_request, account_dict):
        """
        Returns the url to call to send text messages.
        """
        raise NotImplementedError

    def validate_send_result(self, result):
        """
        Returns whether sending an sms was successful.
        """
        raise NotImplementedError

    def get_cost(self, sms, parsed_result):
        return None

    def get_cost_currency(self, sms, parsed_result):
        return None

    def process_response(self, sms, parsed_result):
        sms.cost = self.get_cost(sms, parsed_result)
        sms.cost_currency_code = self.get_cost_currency(sms, parsed_result)
        return None

    def parse_result(self, result):
        return result

    def handle_incoming(self, request, reply_using=None):
        """
        Django view to receive incoming SMSes
        """
        raise NotImplementedError

    def handle_callback(self, request):
        """
        Django view to receive callback for sended SMSes
        """
        raise NotImplementedError

    def handle_cron(self, account_dict, **kwargs):
        """
        For crontab tasks, update sms statuses, and more
        :param kwargs: 
        :return: 
        """
        raise NotImplementedError

    def get_url_capacity(self):
        """
        Returns the number of text messages one call to the url can handle at once.
        """
        raise NotImplementedError

    def get_slug(self):
        """
        A unique short identifier for the SMS gateway provider.
        """
        raise NotImplementedError

    def _find_callable(self, content, hooks):
        """
        Parse the content of an sms according, and try to match it with a callable function defined in the settings.

        This function calls itself to dig through the hooks, because they can have an arbitrary depth.

        :param str content: the content of the sms to parse
        :param dict hooks: the hooks to match
        :returns str or None: the name of the function to call, or None if no function was matched
        """
        # Go throught the different hooks
        matched = False
        for keyword, hook in hooks.iteritems():
            # If the keyword of this hook matches
            if content.startswith(keyword + ' ') or content == keyword:
                matched = True
                break

        # If nothing matched, see whether there is a wildcard
        if not matched and '*' in hooks:
            hook = hooks['*']
            matched = True

        if matched:
            # Take off the first word
            remaining_content = content.split(' ', 1)[1] if ' ' in content else ''

            # There are multiple subkeywords, recurse
            if isinstance(hook, dict):
                return self._find_callable(remaining_content, hook)
            # This is the callable
            else:
                return hook

    def process_incoming(self, request, sms):
        """
        Process an incoming SMS message and call the correct hook.

        :param Request request: the request we're handling. Passed to the handler
        :param SMS sms: the sms we're processing
        :returns: the result of the callable function, or None if nothing was called
        """
        sms.save()

        # work with uppercase and single spaces
        content = sms.content.upper().strip()
        content = re.sub('\s+', " ", content)

        # Try to find the correct hook
        callable_name = self._find_callable(content, all_hooks)

        # If no hook matched, check for a fallback
        if not callable_name and hasattr(settings, 'SMSGATEWAY_FALLBACK_HOOK'):
            callable_name = settings.SMSGATEWAY_FALLBACK_HOOK

        if not callable_name:
            return

        callable_function = get_callable(callable_name)
        return callable_function(request, sms)
