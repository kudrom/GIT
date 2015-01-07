from django.contrib.auth.models import User
from django import forms
from django.forms import extras
from base.models import Incidencia, ElementoInventario, CambioEstado, Comentario, ESTADOS

ESTADOS_CON_EMPTY = [('', '---------')]
ESTADOS_CON_EMPTY.extend(list(ESTADOS))

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

class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ['comentario']

class ListadoForm(forms.Form):
    tecnico_asignado = forms.ModelChoiceField(User.objects.filter(groups__name="tecnicos"), required=False)
    autor = forms.ModelChoiceField(User.objects.filter(groups__name="clientes"), required=False)
    estado = forms.ChoiceField(ESTADOS_CON_EMPTY, required=False)
