from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'GIT.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', 'base.views.home'),
    url(r'^incidencia$', 'base.views.nueva_incidencia'),
    url(r'^incidencia/([\d]+)$', 'base.views.incidencia'),
    url(r'^listado$', 'base.views.listado'),
    url(r'^notificaciones$', 'base.views.notificaciones'),
    url(r'^perfil$', 'base.views.perfil'),

    url(r'^admin/', include(admin.site.urls)),
)
