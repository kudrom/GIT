from django.shortcuts import render, redirect

from django.contrib.auth.models import Group, User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from base.models import Incidencia, CambioEstado, Comentario
from base.forms import SupervisorIncidencia, NuevaIncidencia, ComentarioForm


def get_notificaciones(usuario):
    grupos = usuario.groups.all()
    supervisores = Group.objects.get(name='supervisores')
    tecnicos = Group.objects.get(name='tecnicos')

    if supervisores in grupos:
        incidencias = Incidencia.objects.filter(supervisor=usuario)
        notificaciones = CambioEstado.objects.filter(estado_final__startswith="CT")
        notificaciones = notificaciones.filter(incidencia__in=incidencias).filter(nuevo=True)
    elif tecnicos in grupos:
        incidencias = Incidencia.objects.filter(tecnico_asignado=usuario)
        notificaciones = CambioEstado.objects.filter(estado_final="CP")
        notificaciones = notificaciones.filter(incidencia__in=incidencias).filter(nuevo=True)
    else:
        notificaciones = []
    return notificaciones

def error(request, tipo):
    """
        Muestra un mensaje de error en la pantalla
    """
    context = {}
    if tipo == 'login-inactivo':
        context['mensaje'] = 'El usuario está deshabilitado.'
    elif tipo == 'login-invalido':
        context['mensaje'] = 'El usuario no existe.'
    elif tipo.startswith('login'):
        context['mensaje'] = 'Ha habido un error en el login.'
    elif tipo == "incidencia-invalida":
        context['mensaje'] = 'La incidencia no existe.'
    elif tipo == "sin-permisos":
        context['mensaje'] = 'No tienes permisos.'
    elif tipo == "cerrar-invalido":
        context['mensaje'] = 'No puedes cerrar esta incidencia.'
    else:
        context['mensaje'] = 'Algo misterioso ha ocurrido.'
    return render(request, 'error.html', context)


def home(request):
    """
        Home de la página web, depende de si el usuario está autenticado o no
    """
    if request.user.is_authenticated():
        grupos = [g.name for g in request.user.groups.all()]
        context = {'grupos': grupos}
        context['notificaciones_badge'] = len(get_notificaciones(request.user))
        return render(request, 'listado.html', context)
    else:
        return render(request, 'login.html', {})


def login_procesar(request):
    """
        View para login llamado cuando se envía el formulario de login
    """
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
    """
        View para logout
    """
    logout(request)
    return redirect('/')

@login_required
def perfil(request):
    """
        Página para el perfil
    """
    grupos = [g.name for g in request.user.groups.all()]
    context = {'peticion': 'perfil', 'grupos': grupos}
    context['notificaciones_badge'] = len(get_notificaciones(request.user))

    return render(request, 'perfil.html', context)

@login_required
def ayuda(request):
    """
        Página para la ayuda
    """
    grupos = [g.name for g in request.user.groups.all()]
    context = {'peticion': 'ayuda', 'grupos': grupos}
    context['notificaciones_badge'] = len(get_notificaciones(request.user))

    return render(request, 'ayuda.html', context)

@login_required
def incidencia(request, id_incidencia):
    """
        View para mostrar las incidencias con el formulario para el supervisor
    """
    grupos = request.user.groups.all()
    supervisores = Group.objects.get(name='supervisores')
    context = {'grupos': [g.name for g in grupos]}
    context['notificaciones_badge'] = len(get_notificaciones(request.user))
    try:
        incidencia = Incidencia.objects.get(id=id_incidencia)
        context['incidencia'] = incidencia
        context['comentarios'] = Comentario.objects.filter(incidencia=incidencia)
    except Incidencia.DoesNotExist:
        return redirect('/error/incidencia-invalida')

    # Si el supervisor ha enviado el formulario para completar la incidencia
    if request.method == 'POST':
        # Un supervisor solo puede modificar incidencias que estén en estado AC
        if supervisores in grupos and incidencia.estado == 'AC':
            form = SupervisorIncidencia(request.POST, instance=incidencia)
            form.fields['tecnico_asignado'].queryset = User.objects.filter(groups__name="tecnicos")
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
            # Si algún campo del formulario del supervisor es inválido
            else:
                request.POST = None
                context['form'] = form

    context['form_comentario'] = ComentarioForm()
    # Mostrar la página de incidencia
    if 'form' not in context and incidencia.estado == 'AC':
        form = SupervisorIncidencia(instance=incidencia)
        form.fields['tecnico_asignado'].queryset = User.objects.filter(groups__name="tecnicos")
        context['form'] = form
    return render(request, 'resumen-incidencia.html', context)


@login_required
def cerrar(request):
    """
        View para cerrar incidencias ya sean prematuras, exitosas o fracasadas.
    """
    grupos = request.user.groups.all()
    context = {'grupos': [g.name for g in grupos]}
    clientes = Group.objects.get(name='clientes')
    tecnicos = Group.objects.get(name='tecnicos')

    # Si la petición es correcta
    if 'tipo' in request.GET and 'incidencia' in request.GET:
        id_incidencia = request.GET['incidencia']
        try:
            incidencia = Incidencia.objects.get(id=id_incidencia)
        # Si la incidencia es inválida
        except Incidencia.DoesNotExist:
            return redirect('/error/incidencia-invalida')

        print(grupos)
        if tecnicos in grupos and incidencia.tecnico_asignado == request.user:
            # Si el estado de la incidencia es consistente
            if incidencia.estado == 'AS' or incidencia.estado == 'CP':
                cambio_estado = CambioEstado(incidencia=incidencia,
                                             usuario=request.user,
                                             estado_inicial=incidencia.estado,
                                             nuevo=True)
                if 'exito' == request.GET['tipo']:
                    incidencia.estado = 'CTE'
                    cambio_estado.estado_final = 'CTE'
                elif 'fracaso' == request.GET['tipo']:
                    incidencia.estado = 'CTF'
                    cambio_estado.estado_final = 'CTF'
                else:
                    return redirect('/')
            else:
                return redirect('/error/cerrar-invalido')
        elif clientes in grupos and incidencia.autor == request.user:
            if 'prematuro' == request.GET['tipo'] and incidencia.estado == 'AS':
                incidencia.estado = 'CP'
                cambio_estado = CambioEstado(incidencia=incidencia,
                                             usuario=request.user,
                                             estado_inicial='AS',
                                             estado_final='CP',
                                             nuevo=True)
            else:
                return redirect('/error/cerrar-invalido')
        else:
            return redirect('/error/sin-permisos')
        incidencia.save()
        cambio_estado.save()
    return redirect('/')


@login_required
def comentario(request, incidencia_id):
    """
        Crea un comentario en la base de datos
    """
    grupos = request.user.groups.all()
    context = {'grupos': [g.name for g in grupos]}
    context['notificaciones_badge'] = len(get_notificaciones(request.user))
    tecnicos = Group.objects.get(name='tecnicos')

    if tecnicos in grupos:
        if request.method == 'POST':
            form = ComentarioForm(request.POST)
            comentario = form.save()
            comentario.usuario = request.user
            comentario.incidencia = Incidencia.objects.get(id=incidencia_id)
            comentario.save()
            return redirect('/incidencia/' + str(incidencia_id))
        else:
            return redirect('/')
    else:
        return redirect('/error/sin-permisos')

@login_required
def nueva_incidencia(request):
    """
        Página para crear una nueva incidencia
    """
    grupos = request.user.groups.all()
    context = {'peticion': 'nueva_incidencia', 'grupos': [g.name for g in grupos]}
    context['notificaciones_badge'] = len(get_notificaciones(request.user))
    clientes = Group.objects.get(name='clientes')

    # Si el usuario es un cliente
    if clientes in grupos:
        # Si el cliente ha rellenado el formulario y lo ha enviado
        if request.method == 'POST':
            form = NuevaIncidencia(request.POST)
            # Si todos los campos del formulario enviado son válidos
            if form.is_valid():
                incidencia = form.save()
                incidencia.autor = request.user
                # Si la incidencia se ha podido guardar es inmediatamente aceptada
                incidencia.estado = 'AC'
                incidencia.save()
                cambio_estado = CambioEstado(incidencia=incidencia,
                                             usuario=incidencia.autor,
                                             nuevo=True)
                cambio_estado.save()
                return redirect('/incidencia/' + str(incidencia.id))
            # Si algún campo del formulario es inválido
            else:
                context['form'] = form
        # Si el cliente quiere rellenar una nueva incidencia 
        else:
            form = NuevaIncidencia()
            context['form'] = form
        return render(request, 'abrir-incidencia.html', context)
    # Si el usuario no es un cliente
    else:
        return redirect('/')


@login_required
def estadisticas(request):
    """
        Página para mostrar las estadísticas
    """
    grupos = request.user.groups.all()
    context = {'peticion': 'estadisticas', 'grupos': [g.name for g in grupos]}
    context['notificaciones_badge'] = len(get_notificaciones(request.user))
    supervisores = Group.objects.get(name='supervisores')

    if supervisores in grupos:
        return render(request, 'estadisticas.html', context)
    else:
        return redirect('/')


@login_required
def notificaciones(request):
    """
        Página para mostrar las notificaciones
    """
    grupos = request.user.groups.all()
    context = {'peticion': 'notificaciones', 'grupos': [g.name for g in grupos]}
    context['notificaciones_badge'] = len(get_notificaciones(request.user))
    supervisores = Group.objects.get(name='supervisores')
    tecnicos = Group.objects.get(name='tecnicos')

    if supervisores in grupos or tecnicos in grupos:
        context["notificaciones"] = get_notificaciones(request.user)
        return render(request, 'notificaciones.html', context)
    else:
        return redirect('/')

@login_required
def ver_notificacion(request, id_notificacion):
    """
        View para ver una notificación
    """
    notificacion = CambioEstado.objects.get(id=id_notificacion)
    notificacion.nuevo = False
    notificacion.save()
    return redirect("/incidencia/" + str(notificacion.incidencia.id))
