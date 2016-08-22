from django.conf.urls import patterns, url

from smsgateway.views import backend_debug, backend_handle_incoming, backend_handle_callback

urlpatterns = patterns('',
    url(r'^backend/debug/$', backend_debug, name='smsgateway_backend_debug'),
    url(r'^(?P<backend_name>.+)/incoming/$', backend_handle_incoming, name='smsgateway_backend'),
    url(r'^(?P<backend_name>.+)/callback/$', backend_handle_callback, name='smsgateway_callback'),
)
