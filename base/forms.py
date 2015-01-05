from django.contrib.auth.models import User
from django import forms
from django.forms import extras
from base.models import Incidencia, ElementoInventario


class NuevaIncidencia(forms.ModelForm):
    class Meta:
        model = Incidencia
        fields = ['nombre', 'descripcion', 'fecha_apertura', 'categoria']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
            'fecha_apertura': extras.SelectDateWidget(attrs={'class': 'form-control fecha_apertura'}),
            'categoria': forms.Select(),
        }

class SupervisorIncidencia(forms.Form):
    prioridad = forms.IntegerField()
    inventario = forms.ModelChoiceField(ElementoInventario.objects.all())
    tecnico = forms.ModelChoiceField(User.objects.filter(groups__name="tecnicos"))

    def save(self, id_incidencia):
        incidencia = Incidencia.objects.get(id=id_incidencia)
        incidencia.prioridad = self.cleaned_data['prioridad']
        incidencia.inventario = self.cleaned_data['inventario']
        incidencia.tecnico = self.cleaned_data['tecnico']
        incidencia.save()
