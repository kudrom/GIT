from django.shortcuts import render, redirect

from django.contrib.auth.models import Group, User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from base.models import Incidencia, CambioEstado
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
    def cambiar_choices(form):
        tecnicos = User.objects.filter(groups__name="tecnicos")
        choices = [('', '---------')]
        i = 1
        for tecnico in tecnicos:
            choices.append((i, tecnico))
            i += 1
        form.fields['tecnico_asignado'].choices = choices

    grupos = [g.name for g in request.user.groups.all()]
    context = {'grupos': grupos}
    try:
        incidencia = Incidencia.objects.get(id=id_incidencia)
        context['incidencia'] = incidencia
    except Incidencia.DoesNotExist:
        return redirect('/error/incidencia-invalida')

    if request.method == 'POST':
        form = SupervisorIncidencia(request.POST, instance=incidencia)
        cambiar_choices(form)
        if form.is_valid():
            incidencia = form.save()
            incidencia.estado = 'AS'
            incidencia.supervisor = request.user
            incidencia.save()
            cambio_estado = CambioEstado(incidencia=incidencia,
                                         usuario=request.user,
                                         estado_inicial='AC',
                                         estado_final='AS',
                                         nuevo=True)
            cambio_estado.save()
            return redirect('/')
        else:
            request.POST = None
            context['form'] = form
    if 'form' not in context:
        form = SupervisorIncidencia(instance=incidencia)
        cambiar_choices(form)
        context['form'] = form
    return render(request, 'resumen-incidencia.html', context)


@login_required
def cerrar(request):
    grupos = [g.name for g in request.user.groups.all()]
    context = {'grupos': grupos}
    clientes = Group.objects.get(name='clientes')
    tecnicos = Group.objects.get(name='tecnicos')

    if 'tipo' in request.GET and 'incidencia' in request.GET:
        id_incidencia = request.GET['incidencia']
        try:
            incidencia = Incidencia.objects.get(id=id_incidencia)
        except Incidencia.DoesNotExist:
            return redirect('/')
        if 'exito' == request.GET['tipo']:
            incidencia.estado = 'CE'
            cambio_estado = CambioEstado(incidencia=incidencia,
                                         usuario=request.user,
                                         estado_inicial='AS',
                                         estado_final='CE',
                                         nuevo=True)
        elif 'fracaso' == request.GET['tipo']:
            incidencia.estado = 'CF'
            cambio_estado = CambioEstado(incidencia=incidencia,
                                         usuario=request.user,
                                         estado_inicial='AS',
                                         estado_final='CF',
                                         nuevo=True)
        elif 'prematuro' == request.GET['tipo']:
            incidencia.estado = 'CP'
            cambio_estado = CambioEstado(incidencia=incidencia,
                                         usuario=request.user,
                                         estado_inicial='AS',
                                         estado_final='CP',
                                         nuevo=True)
        else:
            return redirect('/')
        incidencia.save()
        cambio_estado.save()
    return redirect('/')


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
