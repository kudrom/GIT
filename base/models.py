from django.db import models
from django.contrib.auth.models import User

ESTADOS = (
        ('SO', 'Solicitada'),
        ('AC', 'Aceptada'),
        ('AS', 'Asignada'),
        ('CP', 'Cerrada prematuramente'),
        ('CE', 'Cerrada con solución'),
        ('CF', 'Cerrada sin solución')
    )

class ElementoInventario(models.Model):
    precio_compra = models.FloatField()
    fecha_compra = models.DateField()
    tipo = models.CharField(max_length=8)
    caracteristicas = models.CharField(max_length=200)

class Incidencia(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=300)
    prioridad = models.IntegerField()
    categoria = models.CharField(max_length=80)
    estado = models.CharField(max_length=2, choices=ESTADOS, default='SO')
    inventario = models.ForeignKey(ElementoInventario)

    fecha_apertura = models.DateField()
    fecha_cierre = models.DateField()
    resuelta_exito = models.BooleanField(default=False)

    tecnico_asignado = models.ForeignKey(User, null=True, related_name="tecnico_asignado")
    supervisor = models.ForeignKey(User, null=True, related_name="supervisor")
    cliente = models.ForeignKey(User, null=True, related_name="cliente")

class CambioEstado(models.Model):
    incidencia = models.ForeignKey(Incidencia)
    usuario = models.ForeignKey(User)
    fecha_cambio = models.DateField()
    estado_inicial = models.CharField(max_length=2, choices=ESTADOS, default='SO')
    estado_final = models.CharField(max_length=2, choices=ESTADOS, default='AC')
    nuevo = models.BooleanField(default=True)
