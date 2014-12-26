from django.shortcuts import render


def home(request):
    return render(request, 'home.html', {})

def nueva_incidencia(request):
    return render(request, 'abrir-incidencia.html', {})

def incidencia(request, id_incidencia):
    context = {'identidad': id_incidencia}
    return render(request, 'resumen-incidencia.html', context)

def listado(request):
    return render(request, 'listado.html', {})

def notificaciones(request):
    return render(request, 'notificaciones.html', {})

def perfil(request):
    return render(request, 'perfil.html', {})

def estadisticas(request):
    return render(request, 'estadisticas.html', {})

def ayuda(request):
    return render(request, 'ayuda.html', {})
