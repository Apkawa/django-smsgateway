import logging
from optparse import make_option

from django.conf import settings
from django.core.management.base import AppCommand

from smsgateway.tasks import send_smses

LOCK_WAIT_TIMEOUT = getattr(settings, "SMSES_LOCK_WAIT_TIMEOUT", -1)

logger = logging.getLogger(__name__)


class Command(AppCommand):
    help = 'Send SMSes in the queue. Defer the failed ones. Pass --send-deferred to retry those.'

    def add_arguments(self, parser):
        parser.add_command(
            '--send-deferred',
            dest='send_deferred',
            action='store_true',
            help='Whether to send the deferred smses. Default is all non-deferred.'
        )
        parser.add_command(
            '--backend',
            dest='backend',
            action='store',
            help='Whether to use a certain backend.'
        )
        parser.add_command(
            '--limit',
            dest='limit',
            action='store',
            help='Limit the number of smses. Default is unlimited.'
        )

    def handle(self, *args, **options):
        send_smses(options['send_deferred'], options['backend'], options['limit'])
