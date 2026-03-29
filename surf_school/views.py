
from rest_framework import viewsets, filters
from .models import Clase, Alumno, Reserva, SolicitudCancelacion
from .serializers import ClaseSerializer, AlumnoSerializer, ReservaSerializer
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from rest_framework.permissions import IsAdminUser, AllowAny
from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required
from datetime import datetime, time
from django.contrib.auth.forms import PasswordChangeForm
from django.utils import timezone



class ClaseViewSet(viewsets.ReadOnlyModelViewSet):#Permite solo lectura de las rutas /clases/
    queryset = Clase.objects.all() #selecciona todos los objetos de clase
    serializer_class = ClaseSerializer #llama al serializer
    permission_classes = [AllowAny] #cualquiera puede ver las clases, hasta sin login


class AlumnoViewSet(viewsets.ModelViewSet):#Permite crud completo de la ruta de /alumnos
    queryset = Alumno.objects.all() #selecciona todos los objetos del alumno
    serializer_class = AlumnoSerializer #llama al serializer
    permission_classes = [IsAdminUser] #solo puede ser modificado por el Admin


class ReservaViewSet(viewsets.ModelViewSet):#Permite crud completo  de reservas
    queryset = Reserva.objects.all()#selecciona todos los objetos de Reserva
    serializer_class = ReservaSerializer#define el serializador
    permission_classes = [IsAdminUser] #solo permite acceso completo al administrador
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]#habilita busqueda y ordenamiento
    search_fields = ['alumno__nombre', 'clase__nivel']#permite filtar por nombre y nivel
    ordering_fields = ['clase__fecha', 'clase__turno']#permite ordenar por fechas y turnos


def login_view(request):#vista para manejar login de usuario
    if request.method == 'POST':#En caso de que el usuario envie un formulario 
        username = request.POST.get('username')#el objeto username toma el envio del usuario de username
        password = request.POST.get('password')#el objeto password toma el envio del usuario de password

        user = authenticate(request, username=username, password=password)#verifica las credenciales

        if user is not None:#en caso de que las credenciales sean correctas
            login(request, user)#inicia sesion
            return redirect('clases')#este lo envia a la vista clases
        else:
            return render(request, 'login.html', {'error': 'Usuario o contraseña incorrecto'})#en caso que no coincida, va a continuar en el mismo archivo html y da un mensaje de error

    return render(request, 'login.html')#si es metodo get va al archivo login.html


def register_view(request):#vista para manejar el registro de usuario
    if request.method == 'POST':#En caso que se complete y envie el formulario
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        password2 = request.POST.get('password2', '').strip()
        nombre = request.POST.get('nombre', '').strip()
        edad = request.POST.get('edad', '').strip()
        nivel = request.POST.get('nivel', 'P')
        telefono = request.POST.get('telefono', '').strip()
        email_contacto = request.POST.get('email_contacto', '').strip()
        #se crean los datos del usuario al ingresarlos al formulario, y a traves del metodo strip()se elimninan los espacios y saltos de lineas.
        form_data = {#se cargan las credenciales al diccionario del formulario
            'username': username,
            'nombre': nombre,
            'edad': edad,
            'nivel': nivel,
            'telefono': telefono,
            'email_contacto': email_contacto,
        }

        if not username or not password or not password2 or not nombre or not edad or not telefono or not email_contacto:
            return render(request, 'register.html', {
                'error': 'Todos los campos son obligatorios.',
                'form_data': form_data
            })#en caso que algunos de los objetos mencionados en el if not no sean completados va a redirigir al register.html dando un mensaje de error sin eliminar lo escrito por el usuario

        if password != password2:
            return render(request, 'register.html', {
                'error': 'Las contraseñas no coinciden.',
                'form_data': form_data
            })#en caso que las contraseñas no coincidan redirige a register.html y da un mensaje de error sin eliminar lo escrito por el usuario

        if User.objects.filter(username=username).exists():
            return render(request, 'register.html', {
                'error': 'Ese nombre de usuario ya existe.',
                'form_data': form_data
            })#en caso de que el username ya exista en la base de datos va a redirigir a register.html y da un mensaje de error sin eliminar lo escrito por el usuario

        try:
            edad = int(edad)
            if edad <= 0:
                raise ValueError#da error en caso que la edad sea menor o igual a 0
        except ValueError:
            return render(request, 'register.html', {
                'error': 'La edad debe ser un número válido.',
                'form_data': form_data
            })#da un mensaje de error en caso que la edad no sea valida.

        try:
            user = User.objects.create_user(
                username=username,
                password=password,
                email=email_contacto,
            )

            Alumno.objects.create(
                user=user,
                nombre=nombre,
                edad=edad,
                nivel=nivel,
                telefono=telefono,
                email_contacto=email_contacto,
            )

            messages.success(request, 'Usuario creado correctamente. Ya puedes iniciar sesión.')
            return redirect('login')
            #en caso de que los campos hayan sido completados correctamente, redirige a la pagina de login con un mensaje de suceso
        except Exception as e:
            return render(request, 'register.html', {
                'error': f'Hubo un error al registrarte: {str(e)}',
                'form_data': form_data
            })#en caso de algun error inesperado redirige al register.html, manteniendo los datos en los campos del formulario y dando un mensaje de error

    return render(request, 'register.html')#si el metodo es get dirige a la pagina de register.html


@login_required#para realizar la siguiente funcion precisa estar logueado
def mis_reservas(request):
    try:
        alumno = request.user.alumno
        reservas = list(
            Reserva.objects.filter(alumno=alumno)
            .select_related('clase')
            .order_by('clase__fecha', 'clase__turno')#nos filtra las reserva y ordena por fecha y turno
        )
    except Alumno.DoesNotExist:
        reservas = []
        messages.error(request, 'Tu usuario no tiene un perfil de alumno asociado.')
        return render(request, 'reservas.html', {'reservas': reservas})#solo toma usuario valido con aluno registrado

    ahora = timezone.localtime()#fecha y hora actual
    hoy = ahora.date()#solo fecha
    hora_actual = ahora.time()#solo hora

    horas_turno = {
        '1': time(7, 0),
        '2': time(8, 30),
        '3': time(10, 0),
        '4': time(11, 30),
        '5': time(13, 0),
        '6': time(14, 30),
        '7': time(16, 30),
    }#horarios de clases

    for reserva in reservas:
        hora_clase = horas_turno.get(reserva.clase.turno)
        ya_paso = False#funcion para filtrar aulas por horas

        if reserva.clase.fecha < hoy:
            ya_paso = True
        elif reserva.clase.fecha == hoy and hora_clase and hora_clase < hora_actual:
            ya_paso = True#solo nos devuelve las aulas que no sucedieron todavia

        reserva.ya_paso = ya_paso
        reserva.apagada = ya_paso or reserva.estado == 'X'

    return render(request, 'reservas.html', {'reservas': reservas})


def clases_view(request):
    clases = Clase.objects.all().order_by('fecha', 'turno')#selecciona los elementos de la clase

    fecha_desde = request.GET.get('fecha_desde', '').strip()
    fecha_hasta = request.GET.get('fecha_hasta', '').strip()
    nivel = request.GET.get('nivel', '').strip()
    turno = request.GET.get('turno', '').strip()
    #toma los datos ingresados por el usuario para filtrar clases
    
    ahora = timezone.localtime()#obtiene hora y fecha actual
    hoy = ahora.date()#solo fecha
    hora_actual = ahora.time()#solo hora

    horas_turno = {
        '1': time(7, 0),
        '2': time(8, 30),
        '3': time(10, 0),
        '4': time(11, 30),
        '5': time(13, 0),
        '6': time(14, 30),
        '7': time(16, 30),
    }#horarios de clases

    clases_visibles = []

    for clase in clases:
        hora_clase = horas_turno.get(clase.turno)#toma la hora de la clase

        if clase.fecha > hoy:
            clases_visibles.append(clase)
        elif clase.fecha == hoy and hora_clase and hora_clase > hora_actual:
            clases_visibles.append(clase)#agrega a clases_visibles solo las clases que todavia no fueron realizadas

    if fecha_desde:
        clases_visibles = [c for c in clases_visibles if str(c.fecha) >= fecha_desde]

    if fecha_hasta:
        clases_visibles = [c for c in clases_visibles if str(c.fecha) <= fecha_hasta]

    if nivel:
        clases_visibles = [c for c in clases_visibles if c.nivel == nivel]

    if turno:
        clases_visibles = [c for c in clases_visibles if c.turno == turno]

    contexto = {
        'clases': clases_visibles,
        'filtros': {
            'fecha_desde': fecha_desde,
            'fecha_hasta': fecha_hasta,
            'nivel': nivel,
            'turno': turno,
        },#Solo se agregan a contexto las clases que todavia no sucedieron para mostrarlas mas adelante
        'niveles': Alumno.NIVEL,
        'turnos': Clase.TURNO_OPCIONES,
    }

    return render(request, 'clases.html', contexto)


@login_required#login necesario
def reservar_clase(request, clase_id):#trabajamos con una clase seleccionada por id
    if request.method != 'POST':
        return redirect('clases')#solo podemos reservar por formulario POST, por seguridad, (no permitiendo entrar por urls)

    clase = get_object_or_404(Clase, id=clase_id)#busca la clase, en caso que no exista nos da error

    try:
        alumno = request.user.alumno #obtiene perfil del usuario
        reserva = Reserva.objects.create(alumno=alumno, clase=clase)#selecciona al alumno y clase
        messages.success(request, 'Reserva creada con éxito. Estado: pendiente.')#mensaje de reserva realizada
        return redirect('instrucciones_pago', reserva_id=reserva.id)#nos redirecciona a las instrucciones de pagamento de la clase
    except Alumno.DoesNotExist:#error en caso que no exista el usuario
        messages.error(request, 'Tu usuario no tiene un perfil de alumno asociado.')
    except Exception as e:#error en caso que no se pueda concluir la solicitud
        messages.error(request, str(e))

    return redirect('clases')#volvemos a clases


@staff_member_required#solo para administrador
def crear_clase_view(request):#funcion para crear una clase
    if request.method == 'POST':#en caso de solicitud post
        fecha = request.POST.get('fecha', '').strip()#nos toma los datos del formulario eliminando espacios y, en caso de que no haya nos devuelve una cadena vacia
        turno = request.POST.get('turno', '').strip()
        cupo_maximo = request.POST.get('cupo_maximo', '').strip()
        nivel = request.POST.get('nivel', '').strip()

        form_data = {
            'fecha': fecha,
            'turno': turno,
            'cupo_maximo': cupo_maximo,
            'nivel': nivel,
        }#completa los datos del formulario

        if not fecha or not turno or not cupo_maximo or not nivel:
            return render(request, 'crear_clase.html', {
                'error': 'Todos los campos son obligatorios.',
                'form_data': form_data,
                'turnos': Clase.TURNO_OPCIONES,
                'niveles': Alumno.NIVEL,
            })#Nos obliga a completar todos los campos sin borrar los campos que lleno el usuario antes

        try:
            fecha_obj = datetime.strptime(fecha, '%Y-%m-%d').date()#nos toma el texto de la fecha convirtiendola en una fecha valida
        except ValueError:
            return render(request, 'crear_clase.html', {#La fecha debe ser valida
                'error': 'La fecha no es válida.',
                'form_data': form_data,
                'turnos': Clase.TURNO_OPCIONES,
                'niveles': Alumno.NIVEL,
            })

        try:
            cupo_maximo = int(cupo_maximo)
            if cupo_maximo <= 0:
                raise ValueError
        except ValueError:
            return render(request, 'crear_clase.html', {
                'error': 'El cupo máximo debe ser un número mayor que 0.',
                'form_data': form_data,
                'turnos': Clase.TURNO_OPCIONES,
                'niveles': Alumno.NIVEL,
            })#de nuevo, tiene que ser el cupo un numero valido y mayor a 0

        if Clase.objects.filter(fecha=fecha_obj, turno=turno, nivel=nivel).exists():
            return render(request, 'crear_clase.html', {#Evita que se cree otra clase totalmente igual en el mismo turno
                'error': 'Ya existe una clase con esa fecha, turno y nivel.',
                'form_data': form_data,
                'turnos': Clase.TURNO_OPCIONES,
                'niveles': Alumno.NIVEL,
            })

        Clase.objects.create(
            fecha=fecha_obj,
            turno=turno,
            cupo_maximo=cupo_maximo,
            nivel=nivel
        )#Nos crea y guarda la nueva clase en la base de datos

        messages.success(request, 'Clase creada correctamente.')
        return redirect('clases')#nos devuelve a la interfaz de clases

    return render(request, 'crear_clase.html', {
        'turnos': Clase.TURNO_OPCIONES,
        'niveles': Alumno.NIVEL,
    })#Si es una solicitud get nos muestra el formulario para crear la Clase 
    
    
@staff_member_required#solo admins
def editar_clase_view(request, clase_id):#funcion para editar una clase seleccionada por di
    clase = get_object_or_404(Clase, id=clase_id)#Toma el objeto clase en caso de que exista

    if request.method == 'POST':
        fecha = request.POST.get('fecha', '').strip()
        turno = request.POST.get('turno', '').strip()
        cupo_maximo = request.POST.get('cupo_maximo', '').strip()
        nivel = request.POST.get('nivel', '').strip()

        form_data = {
            'fecha': fecha,
            'turno': turno,
            'cupo_maximo': cupo_maximo,
            'nivel': nivel,
        }#la clase es reemplazada por los nuevos valores recibidos a traves de un formulario post

        if not fecha or not turno or not cupo_maximo or not nivel:
            return render(request, 'editar_clase.html', {
                'error': 'Todos los campos son obligatorios.',
                'form_data': form_data,
                'turnos': Clase.TURNO_OPCIONES,
                'niveles': Alumno.NIVEL,
                'clase': clase,
            })#evita que algun campo quede vacio

        try:
            fecha_obj = datetime.strptime(fecha, '%Y-%m-%d').date()#mantiene un formato de fecha valido
        except ValueError:
            return render(request, 'editar_clase.html', {
                'error': 'La fecha no es válida.',
                'form_data': form_data,
                'turnos': Clase.TURNO_OPCIONES,
                'niveles': Alumno.NIVEL,
                'clase': clase,
            })#en caso de error nos devuelve a editar clase manteniendo los campos completos

        try:
            cupo_maximo = int(cupo_maximo)
            if cupo_maximo <= 0:
                raise ValueError
        except ValueError:
            return render(request, 'editar_clase.html', {
                'error': 'El cupo máximo debe ser un número mayor que 0.',
                'form_data': form_data,
                'turnos': Clase.TURNO_OPCIONES,
                'niveles': Alumno.NIVEL,
                'clase': clase,
            })#El cupo maximo debe ser unnumero valido y mayor que 0

        if Clase.objects.exclude(id=clase.id).filter(fecha=fecha_obj, turno=turno, nivel=nivel).exists():
            return render(request, 'editar_clase.html', {#no permite que se repita una clase igual con los mismos datos
                'error': 'Ya existe otra clase con esa fecha, turno y nivel.',
                'form_data': form_data,
                'turnos': Clase.TURNO_OPCIONES,
                'niveles': Alumno.NIVEL,
                'clase': clase,
            })

        clase.fecha = fecha_obj
        clase.turno = turno
        clase.cupo_maximo = cupo_maximo
        clase.nivel = nivel
        clase.save()#carga los datos recibidos por el formulario con exito y los guarda

        messages.success(request, 'Clase editada correctamente.')
        return redirect('clases')

    form_data = {
        'fecha': clase.fecha.strftime('%Y-%m-%d'),
        'turno': clase.turno,
        'cupo_maximo': clase.cupo_maximo,
        'nivel': clase.nivel,
    }

    return render(request, 'editar_clase.html', {
        'form_data': form_data,
        'turnos': Clase.TURNO_OPCIONES,
        'niveles': Alumno.NIVEL,
        'clase': clase,
    })


@staff_member_required
def gestionar_reservas_view(request):#funcion para gestion de reservas, solo para admin
    reservas = Reserva.objects.select_related('alumno', 'clase').order_by('clase__fecha', 'clase__turno', 'alumno__nombre')#ordena todas las reservas y sus relaciones entre reservas, alumno y clase por fecha ,turno y nombre
    return render(request, 'gestionar_reservas.html', {'reservas': reservas})#envia las reservas al template


@staff_member_required
def cambiar_estado_reserva_view(request, reserva_id, nuevo_estado):#solo para admin, seleccionando una reserva especifica y actualizando su estado
    if request.method != 'POST':
        return redirect('gestionar_reservas')#en caso de metodo distinto de post, nos direcciona a gestionar_reservas

    reserva = get_object_or_404(Reserva, id=reserva_id)#la variable reserva recibe los objetos de la reserva seleccionada en caso de que esta exista

    if nuevo_estado not in ['P','C', 'X']:#el nuevo estado debe ser Confirmada, Cancelada o Pendiente
        messages.error(request, 'Estado no válido.')
        return redirect('gestionar_reservas')#si es Pendiente nos da mensaje de error y nos lleva a gestionar_reservas

    reserva.estado = nuevo_estado
    reserva.save()#se guarda la nueva reserva en la base de datos   

    if nuevo_estado == 'P':
        messages.success(request, 'Reserva marcada como pendiente.')
    elif nuevo_estado == 'C':
        messages.success(request, 'Reserva confirmada correctamente.')
    elif nuevo_estado == 'X':
        messages.success(request, 'Reserva cancelada correctamente.')
        #mensaje despues de editar  el estado de la reserva segun su estado
    return redirect('gestionar_reservas')

@login_required
def logout_view(request):#Funcion para cerrar sesion despues de haber iniciado una
    logout(request)
    messages.success(request, 'Sesión cerrada correctamente.')
    return redirect('login')

@staff_member_required
def eliminar_clase_view(request, clase_id):#Funcion para eliminar una clase(solo admin)
    clase = get_object_or_404(Clase, id=clase_id)#Nos da un error en caso de que no exista

    if request.method == 'POST':
        clase.delete()#Elimina la clase
        messages.success(request, 'Clase eliminada correctamente.')
        return redirect('clases')#volvemos a la url de clase

    return render(request, 'eliminar_clase.html', {'clase': clase})

@login_required
def cancelar_reserva_view(request, reserva_id):#selecciona reserva por id(login obligatorio)
    reserva = get_object_or_404(Reserva, id=reserva_id, alumno=request.user.alumno)#solo toma reserva si existe el id y el alumno, sino, nos da un error 404

    if request.method != 'POST':
        return redirect('mis_reservas')#solo conseguimo ingresar a la cancelacion a traves de un POST

    if reserva.estado == 'P':
        reserva.delete()
        messages.success(request, 'Reserva cancelada correctamente.')
        return redirect('mis_reservas')#Si la reserva esta pendiente entonces se elimina completamente de la base de datos

    if reserva.estado == 'C':
        return redirect('solicitar_cancelacion', reserva_id=reserva.id)#En caso que la reserva ya haya sido confirmada, nos direcciona a solicitar cancelacion para seguir con los demas pasos

    if reserva.estado == 'X':
        messages.error(request, 'La reserva ya está cancelada.')
        return redirect('mis_reservas')#en caso que ya este cancelada nos da un error.

    return redirect('mis_reservas')

@login_required
def solicitar_cancelacion_view(request, reserva_id):#obtenemos la reserva que se quiere cancelar a traves de un id
    reserva = get_object_or_404(Reserva, id=reserva_id, alumno=request.user.alumno)

    if reserva.estado != 'C':
        messages.error(request, 'Solo puedes solicitar cancelación de reservas confirmadas.')
        return redirect('mis_reservas')#solo se puede usar esta funcion en caso que sea una reserva confirmada

    solicitud_existente = SolicitudCancelacion.objects.filter(reserva=reserva, estado='P').first()
    if solicitud_existente:
        messages.error(request, 'Ya existe una solicitud pendiente para esta reserva.')
        return redirect('mis_reservas')#solo nos permite una solicitud por reserva

    if request.method == 'POST':
        motivo = request.POST.get('motivo', '').strip()#Ingresamos el motivo a traves del POST

        if not motivo:
            return render(request, 'solicitar_cancelacion.html', {
                'reserva': reserva,
                'error': 'Debes escribir un motivo.'
            })#No puede quedar el campo de motivo de cancelamiento vacio

        SolicitudCancelacion.objects.create(
            reserva=reserva,
            motivo=motivo,
            estado='P'
        )#En caso que se realice la solicutd de cancelamiento, la reserva esta pendiente nuevamente

        messages.success(request, 'Solicitud de cancelación enviada correctamente.')
        return redirect('mis_reservas')

    return render(request, 'solicitar_cancelacion.html', {'reserva': reserva})

@staff_member_required
def gestionar_solicitudes_cancelacion_view(request):
    solicitudes = SolicitudCancelacion.objects.select_related('reserva__alumno', 'reserva__clase').order_by('-fecha_solicitud')#recibe la solicitud de la reserva del alumno y su clase relacionada, ordenado por fecha de solicitud
    return render(request, 'gestionar_solicitudes_cancelacion.html', {'solicitudes': solicitudes})

@staff_member_required
def responder_solicitud_cancelacion_view(request, solicitud_id, accion):#funcion para responder solicitud de cancelammiento, solo para administrador
    if request.method != 'POST':
        return redirect('gestionar_solicitudes_cancelacion')#solo se ingresa a traves de un POST

    solicitud = get_object_or_404(SolicitudCancelacion, id=solicitud_id)#comprobacion de existencia de solicitud

    if solicitud.estado != 'P':
        messages.error(request, 'Esta solicitud ya fue respondida.')
        return redirect('gestionar_solicitudes_cancelacion')#En caso de que la solicitud no se encuentre pendiente es porque ya fue respondida

    if accion == 'aprobar':
        solicitud.estado = 'A'
        solicitud.save()

        reserva = solicitud.reserva
        reserva.estado = 'X'
        reserva.save()

        messages.success(request, 'Solicitud aprobada y reserva cancelada.')
        return redirect('gestionar_solicitudes_cancelacion')#Se cancela con exito la reserva

    if accion == 'rechazar':
        solicitud.estado = 'R'
        solicitud.save()

        messages.success(request, 'Solicitud rechazada.')
        return redirect('gestionar_solicitudes_cancelacion')#Se rechaza la solicitud de cancelamiento

    messages.error(request, 'Acción no válida.')
    return redirect('gestionar_solicitudes_cancelacion')

@login_required
def instrucciones_pago_view(request, reserva_id):#funcion para usar logueado, pagar una reserva
    reserva = get_object_or_404(Reserva, id=reserva_id, alumno=request.user.alumno)#comprobacion de la existencia de la reserva

    contexto = {
        'reserva': reserva,
        'pix_clave': 'tu-clave-pix-aqui',
        'email_escuela': 'tuemail@escuela.com',
        'telefono_escuela': '5581999999999',
        'telefono_mostrar': '(81) 99999-9999',
    }#diccionaro de contexto con los datos de pagamento de la escuelita

    return render(request, 'instrucciones_pago.html', contexto)#nos envia a instrucciones de pago junto con los datos de contexto

@login_required
def editar_perfil_view(request):#vista para editar datos de perfil
    try:
        alumno = request.user.alumno#alumno recibe todas sus informaciones
    except Alumno.DoesNotExist:
        messages.error(request, 'Tu usuario no tiene un perfil asociado.')#en caso de que no existe da mensjae de error
        return redirect('clases')

    if request.method == 'POST':#solo con formulario post
        nombre = request.POST.get('nombre', '').strip()
        edad = request.POST.get('edad', '').strip()
        nivel = request.POST.get('nivel', '').strip()
        telefono = request.POST.get('telefono', '').strip()
        email_contacto = request.POST.get('email_contacto', '').strip()

        form_data = {
            'nombre': nombre,
            'edad': edad,
            'nivel': nivel,
            'telefono': telefono,
            'email_contacto': email_contacto,
        }#guarda los datos enviados por el usuario para volver a mostrarlos en caso de error

        if not nombre or not edad or not nivel or not telefono or not email_contacto:
            return render(request, 'editar_perfil.html', {#obliga a completar todos los campos
                'error': 'Todos los campos son obligatorios.',
                'form_data': form_data,#mantiene los campos que ya fueron llenos con informacion
                'niveles': Alumno.NIVEL,
            })

        try:
            edad = int(edad)
            if edad <= 0:
                raise ValueError
        except ValueError:
            return render(request, 'editar_perfil.html', {
                'error': 'La edad debe ser un número válido.',
                'form_data': form_data,
                'niveles': Alumno.NIVEL,
            })#la edad debe ser valida y mayor que 0

        alumno.nombre = nombre
        alumno.edad = edad
        alumno.nivel = nivel
        alumno.telefono = telefono
        alumno.email_contacto = email_contacto
        alumno.save()#actualiza los datos en la base de datos

        request.user.email = email_contacto
        request.user.save()#actualiza tambien el email de usuario en django 

        messages.success(request, 'Perfil actualizado correctamente.')
        return redirect('clases')

    form_data = {
        'nombre': alumno.nombre,
        'edad': alumno.edad,
        'nivel': alumno.nivel,
        'telefono': alumno.telefono,
        'email_contacto': alumno.email_contacto,
    }#en caso que no se envie nada, muestra los datos existentes en el formulario

    return render(request, 'editar_perfil.html', {
        'form_data': form_data,
        'niveles': Alumno.NIVEL,
    })#en caso de que no sea un metodo post se mantienen los datos existentes
    
    
@login_required
def cambiar_password_view(request):#funcion para cambiar contraseña
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)#guarda la contraseña enviada por el usuario para despues comprobar si es valida
        if form.is_valid():#compruebe que sea una contraseña valida
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Contraseña actualizada correctamente.')
            return redirect('editar_perfil')
        else:
            return render(request, 'cambiar_password.html', {'form': form})

    form = PasswordChangeForm(request.user)
    return render(request, 'cambiar_password.html', {'form': form})#