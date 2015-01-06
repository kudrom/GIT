from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'GIT.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^error/([\w-]+)$', 'base.views.error'),

    url(r'^$', 'base.views.home'),
    url(r'^login$', 'base.views.login_procesar'),
    url(r'^logout$', 'base.views.logout_procesar'),

    url(r'^incidencia$', 'base.views.nueva_incidencia'),
    url(r'^incidencia/([\d]+)$', 'base.views.incidencia'),
    url(r'^cerrar$', 'base.views.cerrar'),

    url(r'^notificaciones$', 'base.views.notificaciones'),
    url(r'^notificaciones/([\d]+)$', 'base.views.ver_notificacion'),

    url(r'^estadisticas$', 'base.views.estadisticas'),

    url(r'^ayuda$', 'base.views.ayuda'),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^perfil$', 'base.views.perfil'),
)
