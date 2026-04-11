from rest_framework import serializers
from django.contrib.auth.models import User
from .models import *


class UserSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    email = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email')


class AdminSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Administrador
        fields = '__all__'


class MedicoSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Medico
        fields = '__all__'


class PacienteSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Paciente
        fields = '__all__'


class EspecialidadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Especialidad
        fields = '__all__'


class CitaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cita
        fields = '__all__'

class ConsultorioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consultorio
        fields = '__all__'

class ExpedienteClinicoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpedienteClinico
        fields = '__all__'

