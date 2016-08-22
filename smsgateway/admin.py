from django.contrib import admin

from smsgateway.models import SMS, QueuedSMS, Log


class LogInlineAdmin(admin.StackedInline):
    model = Log
    extra = 0
    can_delete = False


class SMSAdmin(admin.ModelAdmin):
    date_hierarchy = 'created'
    list_display = ('created', 'status', 'sender', 'to', 'content', 'operator', 'backend')
    search_fields = ('sender', 'to', 'content',)
    list_filter = ('backend', 'created', 'created')

    inlines = [LogInlineAdmin]


admin.site.register(SMS, SMSAdmin)


class QueuedSMSAdmin(admin.ModelAdmin):
    list_display = ('to', 'content', 'created', 'using', 'priority')
    search_fields = ('to', 'content')
    list_filter = ('created', 'priority', 'using')


admin.site.register(QueuedSMS, QueuedSMSAdmin)
