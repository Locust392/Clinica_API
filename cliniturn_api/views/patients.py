from django.shortcuts import render, get_object_or_404
from django.db.models import *
from django.db import transaction
from cliniturn_api.serializers import *
from cliniturn_api.models import *
from rest_framework.authentication import BasicAuthentication, SessionAuthentication, TokenAuthentication
from rest_framework.generics import CreateAPIView, DestroyAPIView, UpdateAPIView
from rest_framework import permissions
from rest_framework import generics
from rest_framework import status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets
from django.contrib.auth.models import Group
from datetime import datetime
from django.conf import settings
from django.template.loader import render_to_string
import string
import random
import json


class PatientsAll(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        medico_actual = Medico.objects.filter(user=request.user, activo=True).first()
        if medico_actual:
            pacientes_ids = (
                Cita.objects.filter(medico=medico_actual)
                .values_list("paciente_id", flat=True)
                .distinct()
            )

            pacientes = Paciente.objects.select_related("user").filter(
                id__in=pacientes_ids
            )
        else:
            # Admin u otros roles: ven todos
            pacientes = Paciente.objects.select_related("user").all()

        data = PacienteSerializer(pacientes, many=True).data
        return Response(data, 200)



class PatientsView(generics.CreateAPIView):
    # Obtener paciente por ID
    # permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, *args, **kwargs):
        paciente = get_object_or_404(Paciente, id=request.GET.get("id"))
        paciente = PacienteSerializer(paciente, many=False).data
        return Response(paciente, 200)

    # Registrar nuevo paciente
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        user = UserSerializer(data=request.data)
        if user.is_valid():
            role = request.data['rol']
            first_name = request.data['first_name']
            last_name = request.data['last_name']
            email = request.data['email']
            password = request.data['password']

            existing_user = User.objects.filter(email=email).first()
            if existing_user:
                return Response({"message": "Username " + email + ", is already taken"}, 400)

            user = User.objects.create(
                username=email,
                email=email,
                first_name=first_name,
                last_name=last_name,
                is_active=1
            )
            user.save()
            user.set_password(password)
            user.save()

            group, created = Group.objects.get_or_create(name=role)
            group.user_set.add(user)
            user.save()

            paciente = Paciente.objects.create(
                user=user,
                matricula=request.data.get("matricula", ""),
                telefono=request.data.get("telefono", ""),
                carrera=request.data.get("carrera", ""),
                activo=True
            )
            paciente.save()

            return Response({"paciente_created_id": paciente.id}, 201)

        return Response(user.errors, status=status.HTTP_400_BAD_REQUEST)


class PatientsViewEdit(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def put(self, request, *args, **kwargs):
        paciente = get_object_or_404(Paciente, id=request.data["id"])
        paciente.matricula = request.data["matricula"]
        paciente.telefono = request.data["telefono"]
        paciente.carrera = request.data["carrera"]
        paciente.save()

        temp = paciente.user
        temp.first_name = request.data["first_name"]
        temp.last_name = request.data["last_name"]
        temp.save()

        user = PacienteSerializer(paciente, many=False).data
        return Response(user, 200)

    def delete(self, request, *args, **kwargs):
        paciente = get_object_or_404(Paciente, id=request.GET.get("id"))
        try:
            paciente.user.delete()
            return Response({"details": "Paciente eliminado"}, 200)
        except Exception as e:
            return Response({"details": "Algo pasó al eliminar"}, 400)


class PatientsChangeStatusView(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        paciente = get_object_or_404(Paciente, id=request.data["id"])
        paciente.activo = not paciente.activo
        paciente.save()
        data = PacienteSerializer(paciente, many=False).data
        return Response(data, 200)
