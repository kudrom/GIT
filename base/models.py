from django.db import models
from django.contrib.auth.models import User
from django import forms
from django.forms import extras
import datetime

ESTADOS = (
        ('SO', 'Solicitada'),
        ('AC', 'Aceptada'),
        ('AS', 'Asignada'),
        ('CP', 'Cerrada prematuramente'),
        ('CE', 'Cerrada con solución'),
        ('CF', 'Cerrada sin solución')
    )

CATEGORIAS = (
        ('HW', 'Hardware'),
        ('CO', 'Comunicaciones'),
        ('SWB', 'Software básico'),
        ('SWA', 'Software de aplicaciones')
        )

class ElementoInventario(models.Model):
    precio_compra = models.FloatField()
    fecha_compra = models.DateField(default=datetime.datetime.today)
    tipo = models.CharField(max_length=8)
    caracteristicas = models.CharField(max_length=200)

class Incidencia(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=300)
    prioridad = models.IntegerField(null=True, blank=True)
    categoria = models.CharField(max_length=3, choices=CATEGORIAS)
    estado = models.CharField(max_length=2, choices=ESTADOS, default='SO')
    inventario = models.ForeignKey(ElementoInventario, null=True, blank=True)

    fecha_apertura = models.DateField(default=datetime.datetime.today)
    fecha_cierre = models.DateField(null=True, blank=True)
    resuelta_exito = models.BooleanField(default=False)

    tecnico_asignado = models.ForeignKey(User, null=True, blank=True, related_name="tecnico_asignado")
    supervisor = models.ForeignKey(User, null=True, blank=True, related_name="supervisor")
    cliente = models.ForeignKey(User, null=True, blank=True, related_name="cliente")

class CambioEstado(models.Model):
    incidencia = models.ForeignKey(Incidencia)
    usuario = models.ForeignKey(User)
    fecha_cambio = models.DateField(default=datetime.datetime.today)
    estado_inicial = models.CharField(max_length=2, choices=ESTADOS, default='SO')
    estado_final = models.CharField(max_length=2, choices=ESTADOS, default='AC')
    nuevo = models.BooleanField(default=True)

class NuevaIncidencia(forms.ModelForm):
    class Meta:
        model = Incidencia
        fields = ['nombre', 'descripcion', 'fecha_apertura', 'categoria']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
            'fecha_apertura': extras.SelectDateWidget(attrs={'class': 'form-control fecha_apertura'}),
            'categoria': forms.Select(),
        }
