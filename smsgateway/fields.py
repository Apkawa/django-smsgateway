# coding: utf-8
from __future__ import unicode_literals

from django.db.models import TextField
from django.utils import six
from django.utils.translation import ugettext_lazy as _


class SeparatedField(TextField):
    delimiter = ';'
    default_validators = []
    description = _("Comma-separated emails")

    def __init__(self, *args, **kwargs):
        kwargs['blank'] = True
        super(SeparatedField, self).__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        defaults = {
            'error_messages': {
                'invalid': _('Only comma separated emails are allowed.'),
            }
        }
        defaults.update(kwargs)
        return super(SeparatedField, self).formfield(**defaults)

    def from_db_value(self, value, expression, connection, context):
        return self.to_python(value)

    def get_prep_value(self, value):
        """
        We need to accomodate queries where a single email,
        or list of email addresses is supplied as arguments. For example:
        - Email.objects.filter(to='mail@example.com')
        - Email.objects.filter(to=['one@example.com', 'two@example.com'])
        """
        if isinstance(value, six.string_types):
            return value
        else:
            return ';'.join(map(lambda s: s.strip(), value))

    def to_python(self, value):
        if isinstance(value, six.string_types):
            if value == '':
                return []
            else:
                return [s.strip() for s in value.split(';')]
        else:
            return value

    def south_field_triple(self):
        """
        Return a suitable description of this field for South.
        Taken from smiley chris' easy_thumbnails
        """
        from south.modelsinspector import introspector
        field_class = 'django.db.models.fields.TextField'
        args, kwargs = introspector(self)
        return (field_class, args, kwargs)
