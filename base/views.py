from django.shortcuts import render, redirect

from django.contrib.auth.models import Group
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


def error(request, tipo):
    context = {}
    if tipo == 'login-inactivo':
        context['mensaje'] = 'El usuario está deshabilitado.'
    elif tipo == 'login-invalido':
        context['mensaje'] = 'El usuario no existe.'
    elif tipo.startswith('login'):
        context['mensaje'] = 'Ha habido un error en el login.'
    else:
        context['mensaje'] = 'Algo misterioso ha ocurrido.'
    return render(request, 'error.html', context)


def home(request):
    if request.user.is_authenticated():
        return render(request, 'listado.html', {})
    else:
        return render(request, 'login.html', {})

def login_procesar(request):
    if 'usuario' in request.POST and 'password' in request.POST:
        username = request.POST['usuario']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('/')
            else:
                return redirect('/error/login-inactivo')
        else:
            return redirect('/error/login-invalido')
    else:
        return redirect('/error/login')

def logout_procesar(request):
    logout(request)
    return redirect('/')

@login_required
def perfil(request):
    return render(request, 'perfil.html', {})

@login_required
def ayuda(request):
    return render(request, 'ayuda.html', {})

@login_required
def incidencia(request, id_incidencia):
    context = {'identidad': id_incidencia}
    return render(request, 'resumen-incidencia.html', context)


@login_required
def nueva_incidencia(request):
    clientes = Group.objects.get(name='clientes')
    if clientes in request.user.groups.all():
        return render(request, 'abrir-incidencia.html', {})
    else:
        return redirect('/')


@login_required
def estadisticas(request):
    supervisores = Group.objects.get(name='supervisores')
    if supervisores in request.user.groups.all():
        return render(request, 'estadisticas.html', {})
    else:
        return redirect('/')


@login_required
def notificaciones(request):
    supervisores = Group.objects.get(name='supervisores')
    tecnicos = Group.objects.get(name='tecnicos')
    if supervisores in request.user.groups.all() or tecnicos in request.user.groups.all():
        return render(request, 'notificaciones.html', {})
    else:
        return redirect('/')
