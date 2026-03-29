from django.contrib import admin
from .models import Clase, Alumno,Reserva

class AlumnoAdmin(admin.ModelAdmin):
    list_display = ('nombre','nivel','mostrar_historial')
    list_filter = ('nivel',)
    ordering = ('nombre',)
    
    def mostrar_historial(self,obj):
        reservas = obj.historial()
        return ", ".join([f"{r.clase.get_turno_display()} ({r.clase.fecha})" for r in reservas])
    
    mostrar_historial.short_description = 'Clases realizadas'

class ClaseAdmin(admin.ModelAdmin):
    list_display = ('turno','fecha','nivel','cupo_maximo','cupo_disponible')
    list_filter = ('turno','nivel','fecha','cupo_maximo')
    ordering = ('fecha','turno')
    
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('alumno','clase','estado')
    list_filter = ('estado','alumno','clase__nivel','clase__turno')
    ordering = ('clase__fecha','clase__turno')

admin.site.register(Clase, ClaseAdmin)
admin.site.register(Alumno, AlumnoAdmin)
admin.site.register(Reserva, ReservaAdmin)