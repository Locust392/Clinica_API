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
from django.contrib.auth.models import Group, User   
from datetime import datetime
from django.conf import settings
from django.template.loader import render_to_string
import string
import random
import json


class DoctorsAll(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        medicos = Medico.objects.filter(user__is_active=1).order_by("id")
        lista = MedicoSerializer(medicos, many=True).data
        return Response(lista, 200)


class DoctorsView(generics.CreateAPIView):
    # Obtener médico por ID
    # permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, *args, **kwargs):
        medico = get_object_or_404(Medico, id=request.GET.get("id"))
        medico = MedicoSerializer(medico, many=False).data
        return Response(medico, 200)

    # Registrar nuevo médico
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        # Para debug (puedes verlo en la consola de Django)
        print("POST /doctors/ DATA:", request.data)

        # Rol por defecto = 'medico' si no te lo mandan
        role = request.data.get('rol', 'medico')

        # Serializador de usuario (solo valida first_name, last_name, email)
        user_serializer = UserSerializer(data=request.data)
        if user_serializer.is_valid():
            first_name = request.data.get('first_name', '')
            last_name = request.data.get('last_name', '')
            email = request.data.get('email', '')
            password = request.data.get('password', '')

            if not email or not password:
                return Response(
                    {"detail": "Email y contraseña son obligatorios"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Valida si existe el usuario / email registrado
            existing_user = User.objects.filter(email=email).first()
            if existing_user:
                return Response(
                    {"message": "Username " + email + ", is already taken"},
                    400
                )

            # Crear usuario de Django
            user = User.objects.create(
                username=email,
                email=email,
                first_name=first_name,
                last_name=last_name,
                is_active=1
            )
            user.set_password(password)
            user.save()

            # Asignar grupo
            group, created = Group.objects.get_or_create(name=role)
            group.user_set.add(user)
            user.save()

            # Resolver especialidad (si viene algo) – puede venir como id o dejarse vacío
            especialidad = None
            esp_val = request.data.get("especialidad")
            if esp_val:
                try:
                    esp_id = int(esp_val)
                    especialidad = Especialidad.objects.get(id=esp_id)
                except (ValueError, Especialidad.DoesNotExist):
                    # Si no es un id válido, simplemente se deja en None
                    especialidad = None

            # Crear perfil de médico
            medico = Medico.objects.create(
                user=user,
                cedula=request.data.get("cedula", ""),
                telefono=request.data.get("telefono", ""),
                especialidad=especialidad,
                activo=True
            )
            medico.save()

            return Response({"doctor_created_id": medico.id}, 201)

        # Si falló la validación de UserSerializer
        return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DoctorsViewEdit(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def put(self, request, *args, **kwargs):
        medico = get_object_or_404(Medico, id=request.data["id"])
        medico.cedula = request.data.get("cedula", medico.cedula)
        medico.telefono = request.data.get("telefono", medico.telefono)

        esp_val = request.data.get("especialidad")
        if esp_val:
            try:
                esp_id = int(esp_val)
                especialidad = Especialidad.objects.get(id=esp_id)
                medico.especialidad = especialidad
            except (ValueError, Especialidad.DoesNotExist):
                pass  # Si no existe, no cambiamos nada

        medico.save()

        temp = medico.user
        temp.first_name = request.data.get("first_name", temp.first_name)
        temp.last_name = request.data.get("last_name", temp.last_name)
        temp.save()

        user = MedicoSerializer(medico, many=False).data
        return Response(user, 200)

    def delete(self, request, *args, **kwargs):
        medico = get_object_or_404(Medico, id=request.GET.get("id"))
        try:
            medico.user.delete()
            return Response({"details": "Médico eliminado"}, 200)
        except Exception as e:
            return Response({"details": "Algo pasó al eliminar"}, 400)


class DoctorsChangeStatusView(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def put(self, request, *args, **kwargs):
        medico = get_object_or_404(Medico, id=request.GET.get("id"))
        medico.activo = not medico.activo
        medico.save()
        data = MedicoSerializer(medico, many=False).data
        return Response(data, 200)
