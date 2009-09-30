from django.conf.urls.defaults import *

urlpatterns = patterns('matchbox.webapi.views',
    (r'^entity/$', 'entity'),
    (r'^entity/(?P<uid>\w{32})/$', 'entity'),
    (r'^make_merge/$', 'make_merge'),
    (r'^commit_merge/$', 'commit_merge'),
)
