from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.utils import timezone
import datetime

ESTADOS = (
        ('SO', 'Solicitada'),
        ('AC', 'Aceptada'),
        ('AS', 'Asignada'),
        ('CP', 'Cerrada prematuramente'),
        ('CTE', 'Cerrada con solución'),
        ('CTF', 'Cerrada sin solución')
    )

CATEGORIAS = (
        ('HW', 'Hardware'),
        ('CO', 'Comunicaciones'),
        ('SWB', 'Software básico'),
        ('SWA', 'Software de aplicaciones')
        )

class ElementoInventario(models.Model):
    nombre = models.CharField(max_length=40, default="")
    precio_compra = models.FloatField()
    fecha_compra = models.DateField(default=datetime.datetime.today)
    caracteristicas = models.CharField(max_length=200)

    def __str__(self):
        return self.nombre

class Incidencia(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    prioridad = models.IntegerField(null=True, blank=True)
    categoria = models.CharField(max_length=3, choices=CATEGORIAS)
    estado = models.CharField(max_length=3, choices=ESTADOS, default='SO')
    inventario = models.ForeignKey(ElementoInventario, null=True, blank=True)

    fecha_apertura = models.DateField(default=datetime.date.today)
    fecha_cierre = models.DateField(null=True, blank=True)
    resuelta_exito = models.BooleanField(default=False)

    tecnico_asignado = models.ForeignKey(User, null=True, blank=True, related_name="tecnico_asignado")
    supervisor = models.ForeignKey(User, null=True, blank=True, related_name="supervisor")
    autor = models.ForeignKey(User, null=True, blank=True, related_name="autor")

class CambioEstado(models.Model):
    incidencia = models.ForeignKey(Incidencia)
    usuario = models.ForeignKey(User)
    fecha_cambio = models.DateField(default=datetime.datetime.today)
    estado_inicial = models.CharField(max_length=3, choices=ESTADOS, default='SO')
    estado_final = models.CharField(max_length=3, choices=ESTADOS, default='AC')
    nuevo = models.BooleanField(default=True)

class Comentario(models.Model):
    comentario = models.TextField()
    fecha = models.DateTimeField(default=timezone.now)
    incidencia = models.ForeignKey(Incidencia, null=True, blank=True)
    usuario = models.ForeignKey(User, null=True, blank=True)

@receiver(post_save, sender=Incidencia)
def desencadenar_cambios_estado(sender, instance, created, raw, using, update_fields, **kwargs):
    """
        Handler que registra frente a la base de datos los cambios de estado necesarios
        a medida que se van produciendo.
    """
    cambio_estado = CambioEstado(incidencia=instance,
                                 nuevo=True)
    if instance.estado == 'AC' and len(CambioEstado.objects.filter(incidencia=instance, estado_inicial='SO')) == 0:
        cambio_estado.usuario = instance.autor
    elif instance.estado == 'AS':
        cambio_estado.usuario = instance.supervisor
        cambio_estado.estado_inicial = 'AC'
        cambio_estado.estado_final = 'AS'
    elif instance.estado == 'CP':
        cambio_estado.usuario = instance.autor
        cambio_estado.estado_inicial = 'AS'
        cambio_estado.estado_final = 'CP'
    elif instance.estado.startswith('CT'):
        cambio_estado.usuario = instance.tecnico_asignado
        if len(CambioEstado.objects.filter(incidencia=instance, estado_final='CP')) > 0:
            cambio_estado.estado_inicial = 'CP'
        else:
            cambio_estado.estado_inicial = 'AS'
        if instance.estado == 'CTE':
            cambio_estado.estado_final = 'CTE'
        elif instance.estado == 'CTF':
            cambio_estado.estado_final = 'CTF'
        else:
            return
    else:
        return

    cambio_estado.save()
