from django.contrib.auth.models import User
from django import forms
from django.forms import extras
from base.models import Incidencia, ElementoInventario, CambioEstado


class NuevaIncidencia(forms.ModelForm):
    class Meta:
        model = Incidencia
        fields = ['nombre', 'descripcion', 'fecha_apertura', 'categoria']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
            'fecha_apertura': extras.SelectDateWidget(attrs={'class': 'form-control fecha_apertura'}),
            'categoria': forms.Select(),
        }

class SupervisorIncidencia(forms.ModelForm):
    class Meta:
        model = Incidencia
        fields = ['prioridad', 'inventario', 'tecnico_asignado']
