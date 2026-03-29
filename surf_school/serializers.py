from rest_framework import serializers
from .models import Alumno,Clase,Reserva

class AlumnoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alumno
        fields = '__all__'#Serializa todos los campos del modelo Alumno
        
class ClaseSerializer(serializers.ModelSerializer):
    cupo_disponible = serializers.SerializerMethodField()

    class Meta:
        model = Clase
        fields = '__all__'#Serializa todos los campos del modelo Clase
        
    def get_cupo_disponible(self, obj):
        return obj.cupo_disponible() #nos retorna el cupo disponible actualizado 
    
class ReservaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reserva
        fields = ['id','alumno','clase']  #Serializa solamente los campos de id, alumno y clase del modelo Reserva