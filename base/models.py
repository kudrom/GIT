from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
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
    descripcion = models.CharField(max_length=300)
    prioridad = models.IntegerField(null=True, blank=True)
    categoria = models.CharField(max_length=3, choices=CATEGORIAS)
    estado = models.CharField(max_length=3, choices=ESTADOS, default='SO')
    inventario = models.ForeignKey(ElementoInventario, null=True, blank=True)

    fecha_apertura = models.DateField(default=datetime.datetime.today)
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
