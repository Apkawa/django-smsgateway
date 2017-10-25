import logging
from optparse import make_option

from django.conf import settings
from django.core.management.base import AppCommand

from smsgateway.tasks import cron_smsces

LOCK_WAIT_TIMEOUT = getattr(settings, "SMSES_LOCK_WAIT_TIMEOUT", -1)

logger = logging.getLogger(__name__)


class Command(AppCommand):
    help = 'Send SMSes in the queue. Defer the failed ones. Pass --send-deferred to retry those.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--using',
            dest='using',
            default=None,
            action='store',
            help='Whether to use a certain backend.'
        )
        
        parser.add_argument(
            '--task',
            dest='task',
            default=None,
            action='store',
            help='task name, read backend documentation. '
            
        )

    def handle(self, *args, **options):
        cron_smsces(**options)
