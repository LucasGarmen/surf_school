from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User


def fecha_default():
    return timezone.localdate() + timedelta(days=1)#esta funcion me devuelve la fecha de mañana por defecto


class Alumno(models.Model):#creo un modelo para alumno
    NIVEL = [#creo las opciones de niveles que puede tener un alumno
        ('P', 'Principiante'),
        ('I', 'Intermedio'),
        ('A', 'Avanzado'),
    ]
    #datos del Alumno:
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)#relacion de 1 a 1 de user con Alumno
    telefono = models.CharField(max_length=20, blank=True)#agrega un telefono
    email_contacto = models.EmailField(blank=True)#un email para el alumno
    nombre = models.CharField(max_length=100)#el nombre puede contener hasta 100 caracteres
    edad = models.IntegerField()#la edad es un numero entero
    nivel = models.CharField(max_length=1, choices=NIVEL, default='P')#Nivel del alumno lo selecciono de NIVEL, por defecto selecciona Principiante

    def __str__(self):
        return f"{self.nombre} - {self.get_nivel_display()}"#nos muestra en el /admin el nombre y nivel del alumno

    def historial(self):
        return self.reserva_set.filter(estado='C')#funcion para ver historial de aulas Confirmadas


class Clase(models.Model):#Modelo para clases
    TURNO_OPCIONES = [#opciones de turnos:
        ('1', '07:00 hs'),
        ('2', '08:30 hs'),
        ('3', '10:00 hs'),
        ('4', '11:30 hs'),
        ('5', '13:00 hs'),
        ('6', '14:30 hs'),
        ('7', '16:30 hs'),
    ]

    fecha = models.DateField(default=fecha_default)#la fecha tine que tener formato de fecha(por defecto selecciona la fecha del dia siguiente)
    turno = models.CharField(max_length=1, choices=TURNO_OPCIONES)#el turno se selecciona de las opciones disponibles en TURNO_OPCIONES
    cupo_maximo = models.IntegerField(default=5)#Numero maximo de alumnos por clase(5 por defecto)
    nivel = models.CharField(max_length=1, choices=Alumno.NIVEL, default='P')#El nivel de la clase se selecciona de las opciones de NIVEL disponibles en el modelo Alumno(por defecto principiante)

    def __str__(self):#selecciona la clase especifica
        return f"{self.fecha} - {self.get_turno_display()} (Cupo: {self.cupo_disponible()}/{self.cupo_maximo}) (Nivel: {self.get_nivel_display()})"#nos retorna esa clase mostrando la fecha, turno,cupos disponibles, cupo maximo y nivel

    def cupo_disponible(self):#cupos restantes
        activas = self.reserva_set.filter(estado__in=['P', 'C']).count()#cuenta las reservas pendiente y confirmadas
        return self.cupo_maximo - activas#muestra las clases disponibles     


class Reserva(models.Model):#Crea el modelo de Reserva
    ESTADO_OPCIONES = [#Opciones de estado de una reserva
        ('P', 'Pendiente'),
        ('C', 'Confirmada'),
        ('X', 'Cancelada'),
    ]

    alumno = models.ForeignKey(Alumno, on_delete=models.CASCADE)#el alumno es la llave foranea, haciendo que la existencia de la reserva dependa de la existencia del alumno en la base de de datos
    clase = models.ForeignKey(Clase, on_delete=models.CASCADE)#la clase es la llave foranea, haciendo que la existencia de la reserva dependa de la existencia de la clase en la base de datos
    estado = models.CharField(max_length=1, choices=ESTADO_OPCIONES, default='P')#El estado por defecto es Pendiente , se selecciona a partir de ESTADO_OPCIONES
    


    def save(self, *args, **kwargs):#funcion para guardar argumentos
        reservas_activas = self.clase.reserva_set.exclude(pk=self.pk).filter(estado__in=['P', 'C']).count()#las reservas activas son la suma de pendiente y concluidas, ignorando la reserva que esta siendo hecha
        if reservas_activas >= self.clase.cupo_maximo:
            raise ValueError("No hay cupo disponible")#en caso de que las reservas activas sean mayores o iguales al cupo maximo muestra un mensaje de error

        if Reserva.objects.exclude(pk=self.pk).filter(
            alumno=self.alumno,
            clase=self.clase,
            estado__in=['P', 'C']
        ).exists():
            raise ValueError("Ya tienes una reserva para esta clase")#el usuario no puede hacer una reserva en la misma clase

        if Reserva.objects.exclude(pk=self.pk).filter(
            alumno=self.alumno,
            clase__turno=self.clase.turno,
            clase__fecha=self.clase.fecha,
            estado__in=['P', 'C']
        ).exists():
            raise ValueError("El alumno ya tiene una clase en este horario")#El alimno no puede estar en dos clases distintas al mismo tiempo

        nivel_order = {'P': 1, 'I': 2, 'A': 3}
        if nivel_order[self.alumno.nivel] < nivel_order[self.clase.nivel]:#el alumno solo puede hacer clases de su nivel o de su nivel inferior, sino nos da un error
            raise ValueError("El alumno no tiene suficiente nivel para esta clase")

        super().save(*args, **kwargs)#se guardan los nuevos argumentos reemplazando los anteriores

    def __str__(self):
        return f"{self.alumno} - {self.clase}"# nos muestra el alumno y la clase reservada
    
class SolicitudCancelacion(models.Model):#Modelo para cancelacion de reserva
    ESTADO_OPCIONES = [
        ('P', 'Pendiente'),
        ('A', 'Aprobada'),
        ('R', 'Rechazada'),
    ]

    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE)#lrelación con la reserva asociada a esta solicitud de cancelación
    motivo = models.TextField()#ingreso de motivo por el cancelamiento
    estado = models.CharField(max_length=1, choices=ESTADO_OPCIONES, default='P')#por defecto es Pendiente, pero puede elejirse otra opcion
    fecha_solicitud = models.DateTimeField(auto_now_add=True)#dia en que se hizo la solicitud(fecha automatica  )
    
    def __str__(self):
        return f"Solicitud {self.get_estado_display()} - {self.reserva}"#Muestra el estado de la solicitud y la reserva asociada
