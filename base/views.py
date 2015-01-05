from django.shortcuts import render, redirect

from django.contrib.auth.models import Group
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from base.models import Incidencia
from base.forms import SupervisorIncidencia, NuevaIncidencia

def error(request, tipo):
    context = {}
    if tipo == 'login-inactivo':
        context['mensaje'] = 'El usuario está deshabilitado.'
    elif tipo == 'login-invalido':
        context['mensaje'] = 'El usuario no existe.'
    elif tipo.startswith('login'):
        context['mensaje'] = 'Ha habido un error en el login.'
    elif tipo == "incidencia-invalida":
        context['mensaje'] = 'La incidencia no existe.'
    else:
        context['mensaje'] = 'Algo misterioso ha ocurrido.'
    return render(request, 'error.html', context)


def home(request):
    if request.user.is_authenticated():
        grupos = [g.name for g in request.user.groups.all()]
        context = {'grupos': grupos}
        return render(request, 'listado.html', context)
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
    grupos = [g.name for g in request.user.groups.all()]
    context = {'peticion': 'perfil', 'grupos': grupos}

    return render(request, 'perfil.html', context)

@login_required
def ayuda(request):
    grupos = [g.name for g in request.user.groups.all()]
    context = {'peticion': 'ayuda', 'grupos': grupos}

    return render(request, 'ayuda.html', context)

@login_required
def incidencia(request, id_incidencia):
    grupos = [g.name for g in request.user.groups.all()]
    context = {'grupos': grupos}
    if request.method == 'POST':
        form = SupervisorIncidencia(request.POST)
        if form.is_valid():
            incidencia = form.save(id_incidencia)
            incidencia.supervisor = request.user
            incidencia.save()
            return redirect('/')
        else:
            request.POST = None
            context['form'] = form
    try:
        incidencia = Incidencia.objects.get(id=id_incidencia)
        if incidencia is not None:
            context['incidencia'] = incidencia
            if 'form' not in context:
                context['form'] = SupervisorIncidencia()
            return render(request, 'resumen-incidencia.html', context)
    except Incidencia.DoesNotExist:
        return redirect('/error/incidencia-invalida')


@login_required
def nueva_incidencia(request):
    grupos = [g.name for g in request.user.groups.all()]
    context = {'peticion': 'nueva_incidencia', 'grupos': grupos}
    clientes = Group.objects.get(name='clientes')

    if clientes in request.user.groups.all():
        if request.method == 'POST':
            form = NuevaIncidencia(request.POST)
            if form.is_valid():
                # TODO: implementar mensajes en listado.html
                incidencia = form.save()
                incidencia.autor = request.user
                incidencia.save()
                return redirect('/')
            else:
                context['form'] = form
        else:
            form = NuevaIncidencia()
            context['form'] = form
        return render(request, 'abrir-incidencia.html', context)
    else:
        return redirect('/')


@login_required
def estadisticas(request):
    grupos = [g.name for g in request.user.groups.all()]
    context = {'peticion': 'estadisticas', 'grupos': grupos}
    supervisores = Group.objects.get(name='supervisores')

    if supervisores in request.user.groups.all():
        return render(request, 'estadisticas.html', context)
    else:
        return redirect('/')


@login_required
def notificaciones(request):
    grupos = [g.name for g in request.user.groups.all()]
    context = {'peticion': 'notificaciones', 'grupos': grupos}
    supervisores = Group.objects.get(name='supervisores')
    tecnicos = Group.objects.get(name='tecnicos')

    if supervisores in request.user.groups.all() or tecnicos in request.user.groups.all():
        return render(request, 'notificaciones.html', context)
    else:
        return redirect('/')
