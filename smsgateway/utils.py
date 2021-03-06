import logging

import itertools
import re

from django.conf import settings

logger = logging.getLogger(__name__)


def strspn(source, allowed):
    newchrs = []
    for c in source:
        if c in allowed:
            newchrs.append(c)
    return u''.join(newchrs)


def check_cell_phone_number(number):
    cleaned_number = strspn(number, u'0123456789')
    msisdn_prefix = getattr(settings, 'SMSGATEWAY_MSISDN_PREFIX', '')
    if msisdn_prefix and not cleaned_number.startswith(msisdn_prefix):
        cleaned_number = msisdn_prefix + cleaned_number
    return str(cleaned_number)


def truncate_sms(text, max_length=160):
    text = text.strip()
    if len(text) <= max_length:
        return text
    else:
        # TODO strip by segments, UCS-2 or ascii
        logger.error("Trying to send an SMS that is too long: %s", text)
        return text[:max_length - 3] + '...'


def _match_keywords(content, hooks):
    """
    Helper function for matching a message to the hooks. Called recursively.

    :param str content: the (remaining) content to parse
    :param dict hooks: the hooks to try
    :returns str: the message without the keywords
    """
    # Go throught the different hooks
    matched = False
    for keyword, hook in hooks.iteritems():
        # If the keyword of this hook matches
        if content.startswith(keyword + ' ') or keyword == content:
            matched = True
            break

    # If nothing matched, see if there is a wildcard
    if not matched and '*' in hooks:
        return content

    # Split off the keyword
    remaining_content = content.split(' ', 1)[1] if ' ' in content else ''

    # There are multiple subkeywords, recurse
    if isinstance(hook, dict):
        return _match_keywords(remaining_content, hook)
    # This is the callable, we're done
    else:
        return remaining_content


def parse_sms(content):
    """
    Parse an sms message according to the hooks defined in the settings.

    :param str content: the message to parse
    :returns list: the message without keywords, split into words
    """
    # work with uppercase and single spaces
    content = content.upper().strip()
    content = re.sub('\s+', " ", content)

    from smsgateway.backends.base import all_hooks
    content = _match_keywords(content, all_hooks)
    return content.split(' ')


def get_random_string(*args, **kwargs):
    from django.utils.crypto import get_random_string as _get_random_string
    return _get_random_string(*args, **kwargs)


def grouper(iterable, chunk_size):
    it = iter(iterable)
    while True:
        chunk = tuple(itertools.islice(it, chunk_size))
        if not chunk:
            return
        yield chunk
