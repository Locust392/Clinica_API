from django.db import models
from django.contrib.auth.models import User
from rest_framework.authentication import TokenAuthentication


class BearerTokenAuthentication(TokenAuthentication):
    keyword = u"Bearer"


class Administrador(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False, default=None)
    clave_admin = models.CharField(max_length=50, unique=True)
    telefono = models.CharField(max_length=50, null=True, blank=True)
    rfc = models.CharField(max_length=255, null=True, blank=True)
    edad = models.IntegerField(null=True, blank=True)
    ocupacion = models.CharField(max_length=255, null=True, blank=True)
    activo = models.BooleanField(default=True)
    creation = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    update = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return f"Admin {self.user.first_name} {self.user.last_name}"


class Especialidad(models.Model):
    id = models.BigAutoField(primary_key=True)
    nombre = models.CharField(max_length=255, unique=True)
    descripcion = models.TextField(null=True, blank=True)
    activa = models.BooleanField(default=True)
    creation = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    update = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return self.nombre


class Consultorio(models.Model):
    id = models.BigAutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    edificio = models.CharField(max_length=100)
    piso = models.CharField(max_length=50, null=True, blank=True)
    numero = models.CharField(max_length=50)
    disponible = models.BooleanField(default=True)
    creation = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    update = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return f"{self.nombre} - {self.edificio} {self.numero}"


class Medico(models.Model):

    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False, default=None)
    cedula = models.CharField(max_length=50, null=True, blank=True)
    telefono = models.CharField(max_length=50, null=True, blank=True)
    especialidad = models.ForeignKey(Especialidad, on_delete=models.SET_NULL, null=True, blank=True)
    consultorio = models.ForeignKey(Consultorio, on_delete=models.SET_NULL, null=True, blank=True)
    hora_inicio = models.TimeField(null=True, blank=True)
    hora_fin = models.TimeField(null=True, blank=True)
    dias_atencion = models.CharField(max_length=255, null=True, blank=True)
    activo = models.BooleanField(default=True)
    creation = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    update = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return f"Médico {self.user.first_name} {self.user.last_name}"


class Paciente(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False, default=None)
    matricula = models.CharField(max_length=50, unique=True, null=True, blank=True)
    telefono = models.CharField(max_length=50, null=True, blank=True)
    carrera = models.CharField(max_length=255, null=True, blank=True)
    departamento = models.CharField(max_length=255, null=True, blank=True)
    activo = models.BooleanField(default=True)
    creation = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    update = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return f"Paciente {self.user.first_name} {self.user.last_name}"


class Cita(models.Model):
    id = models.BigAutoField(primary_key=True)
    paciente = models.ForeignKey(Paciente,on_delete=models.CASCADE,related_name='citas')
    medico = models.ForeignKey(Medico,on_delete=models.CASCADE,related_name='citas')
    especialidad = models.ForeignKey(Especialidad,on_delete=models.SET_NULL,null=True,blank=True)
    consultorio = models.ForeignKey(Consultorio,on_delete=models.SET_NULL,null=True,blank=True)
    fecha = models.DateField()
    hora = models.TimeField()
    motivo = models.TextField(null=True, blank=True)
    estado = models.CharField( max_length=20,default='Pendiente')
    creation = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    update = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return f"Cita {self.id} - {self.fecha} {self.hora}"


class ExpedienteClinico(models.Model):
    id = models.BigAutoField(primary_key=True)
    paciente = models.OneToOneField(Paciente, on_delete=models.CASCADE, related_name='expediente')
    medico_principal = models.ForeignKey(Medico, on_delete=models.SET_NULL, null=True, blank=True)
    diagnosticos = models.TextField(null=True, blank=True)
    tratamiento = models.TextField(null=True, blank=True)
    notas_generales = models.TextField(null=True, blank=True)
    creation = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    update = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return f"Expediente de {self.paciente.user.first_name} {self.paciente.user.last_name}"
