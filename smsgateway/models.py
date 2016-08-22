from __future__ import unicode_literals

import datetime
from collections import namedtuple

from django.db import models
from django.utils.translation import ugettext_lazy as _
from six import python_2_unicode_compatible, text_type

from smsgateway.enums import (OPERATOR_CHOICES, OPERATOR_UNKNOWN,
                              GATEWAY_CHOICES, PRIORITIES,
                              PRIORITY_MEDIUM, PRIORITY_DEFERRED,
                              )
from .fields import SeparatedField

STATUS = namedtuple('STATUS', 'sent failed delivered queued')._make(range(4))


@python_2_unicode_compatible
class BaseSMS(models.Model):
    STATUS_CHOICES = [(STATUS.sent, _("sent")), (STATUS.failed, _("failed")),
                      (STATUS.delivered, _("delivered"))]

    cost = models.DecimalField(decimal_places=2, max_digits=6, null=True, blank=True)
    cost_currency_code = models.CharField(max_length=4, null=True, blank=True)

    created = models.DateTimeField(default=datetime.datetime.now, verbose_name=_(u'created'))

    content = models.TextField(verbose_name=_(u'content'), help_text=_(u'SMS content'))
    sender = models.CharField(max_length=32, verbose_name=_(u'sender'), db_index=True)
    to = SeparatedField(max_length=32, verbose_name=_(u'receiver'), db_index=True)

    operator = models.IntegerField(choices=OPERATOR_CHOICES, default=OPERATOR_UNKNOWN,
        verbose_name=_(u'Originating operator'))

    backend = models.CharField(max_length=32, db_index=True, default='unknown', verbose_name=_(u'backend'))

    gateway_ref = models.CharField(max_length=32, blank=True, verbose_name=_(u'gateway reference'),
        help_text=_(u'A reference id for the gateway'))

    status = models.PositiveSmallIntegerField(
        _("Status"),
        choices=STATUS_CHOICES, db_index=True,
        blank=True, null=True)

    priority = models.CharField(max_length=1, choices=PRIORITIES, default=PRIORITY_MEDIUM)

    class Meta:
        get_latest_by = 'created'
        ordering = ('created',)
        abstract = True

    def __str__(self):
        return u'SMS: "%s" from "%s"' % (self.content, self.sender)


class SMS(BaseSMS):
    class Meta:
        verbose_name = _(u'SMS')
        verbose_name_plural = _(u'SMSes')


class InboundSMS(BaseSMS):
    class Meta:
        verbose_name = _(u'Inbound SMS')
        verbose_name_plural = _(u'Inbound SMSes')


class QueuedSMS(models.Model):
    to = models.CharField(max_length=32, verbose_name=_(u'receiver'))
    signature = models.CharField(max_length=32, verbose_name=_(u'signature'))
    content = models.TextField(verbose_name=_(u'content'), help_text=_(u'SMS content'))
    created = models.DateTimeField(default=datetime.datetime.now)
    using = models.CharField(blank=True, max_length=100, verbose_name=_(u'gateway'),
        help_text=_(u'Via which provider the SMS will be sent.'))
    priority = models.CharField(max_length=1, choices=PRIORITIES, default=PRIORITY_MEDIUM)
    reliable = models.BooleanField(default=False, blank=True, verbose_name=_(u'is reliable'))

    class Meta:
        get_latest_by = 'created'
        ordering = ('priority', 'created',)
        verbose_name = _(u'Queued SMS')
        verbose_name_plural = _(u'Queued SMSes')

    def defer(self):
        self.priority = PRIORITY_DEFERRED
        self.save()


@python_2_unicode_compatible
class Log(models.Model):
    """
    A model to record sending email sending activities.
    """

    STATUS_CHOICES = [(STATUS.sent, _("sent")), (STATUS.failed, _("failed"))]

    sms = models.ForeignKey(SMS, editable=False, related_name='logs',
        verbose_name=_('SMS'))
    date = models.DateTimeField(auto_now_add=True)
    status = models.PositiveSmallIntegerField(_('Status'), choices=STATUS_CHOICES)

    exception_type = models.CharField(_('Exception type'), max_length=255, blank=True)
    message = models.TextField(_('Message'))

    class Meta:
        verbose_name = _("Log")
        verbose_name_plural = _("Logs")

    def __str__(self):
        return text_type(self.date)
