from django.shortcuts import render
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
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse
from rest_framework import viewsets
from django.shortcuts import get_object_or_404
from django.core import serializers
from django.utils.html import strip_tags
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import Group, User
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as filters
from datetime import datetime
from django.conf import settings
from django.template.loader import render_to_string
import string
import random
import json


class AdminAll(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        admin = Administrador.objects.filter(user__is_active=1).order_by("id")
        lista = AdminSerializer(admin, many=True).data

        return Response(lista, 200)


class AdminView(generics.CreateAPIView):
    # Obtener usuario por ID
    # permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, *args, **kwargs):
        admin = get_object_or_404(Administrador, id=request.GET.get("id"))
        admin = AdminSerializer(admin, many=False).data

        return Response(admin, 200)

    # Registrar nuevo usuario
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
            user.set_password(password)  # Cifrar contraseña
            user.save()

            group, created = Group.objects.get_or_create(name=role)
            group.user_set.add(user)
            user.save()

            admin = Administrador.objects.create(
                user=user,
                clave_admin=request.data["clave_admin"],
                telefono=request.data["telefono"],
                rfc=request.data["rfc"].upper(),
                edad=request.data["edad"],
                ocupacion=request.data["ocupacion"]
            )
            admin.save()

            return Response({"admin_created_id": admin.id}, 201)

        return Response(user.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminsViewEdit(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    # Contar el total de cada tipo de usuarios
    def get(self, request, *args, **kwargs):
        # Total de admins
        admin = Administrador.objects.filter(user__is_active=1).order_by("id")
        lista_admins = AdminSerializer(admin, many=True).data
        total_admins = len(lista_admins)

        # Total de médicos
        medicos = Medico.objects.filter(user__is_active=1).order_by("id")
        lista_medicos = MedicoSerializer(medicos, many=True).data
        total_medicos = len(lista_medicos)

        # Total de pacientes
        pacientes = Paciente.objects.filter(user__is_active=1).order_by("id")
        lista_pacientes = PacienteSerializer(pacientes, many=True).data
        total_pacientes = len(lista_pacientes)

        return Response(
            {
                'admins': total_admins,
                'doctors': total_medicos,
                'patients': total_pacientes
            },
            200
        )

    # Editar administrador
    def put(self, request, *args, **kwargs):
        admin = get_object_or_404(Administrador, id=request.data["id"])
        admin.clave_admin = request.data["clave_admin"]
        admin.telefono = request.data["telefono"]
        admin.rfc = request.data["rfc"]
        admin.edad = request.data["edad"]
        admin.ocupacion = request.data["ocupacion"]
        admin.save()

        temp = admin.user
        temp.first_name = request.data["first_name"]
        temp.last_name = request.data["last_name"]
        temp.save()

        user = AdminSerializer(admin, many=False).data

        return Response(user, 200)

    # Eliminar administrador
    def delete(self, request, *args, **kwargs):
        admin = get_object_or_404(Administrador, id=request.GET.get("id"))
        try:
            admin.user.delete()
            return Response({"details": "Administrador eliminado"}, 200)
        except Exception as e:
            return Response({"details": "Algo pasó al eliminar"}, 400)


class ProfileView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def _detectar_rol(self, user, paciente=None, medico=None):
        """
        Devuelve un string con el rol principal del usuario:
        'administrador', 'medico', 'paciente' o 'usuario'
        """
        # Si no vienen, los buscamos sin filtrar por activo
        if paciente is None:
            paciente = Paciente.objects.filter(user=user).first()
        if medico is None:
            medico = Medico.objects.filter(user=user).first()

        grupos = user.groups.values_list('name', flat=True)

        # Admin: superuser o grupo admin/administrador
        if user.is_superuser or any(
            g.lower() in ['admin', 'administrador', 'administradora'] for g in grupos
        ):
            return 'administrador'

        # Médico: si tiene registro o grupo médico/doctor
        if medico or any(
            g.lower() in ['medico', 'médico', 'doctor', 'doctora'] for g in grupos
        ):
            return 'medico'

        # Paciente/alumno
        if paciente or any(
            g.lower() in ['paciente', 'alumno', 'estudiante'] for g in grupos
        ):
            return 'paciente'

        # Por defecto
        return 'usuario'

    def get(self, request, *args, **kwargs):
        user = request.user

        # Buscamos perfil (sin filtrar por activo para no excluir registros)
        paciente = Paciente.objects.filter(user=user).first()
        medico = Medico.objects.filter(user=user).first()

        telefono = ""
        if paciente and hasattr(paciente, "telefono"):
            telefono = paciente.telefono or ""
        elif medico and hasattr(medico, "telefono"):
            telefono = medico.telefono or ""

        rol = self._detectar_rol(user, paciente=paciente, medico=medico)

        data = {
            "id": user.id,
            "first_name": user.first_name or "",
            "last_name": user.last_name or "",
            "email": user.email or "",
            "telefono": telefono,
            "rol": rol
        }

        return Response(data, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        """
        Actualiza nombre, email, teléfono del usuario logueado.
        - User: first_name, last_name, email, username (si el email cambia)
        - Paciente / Médico: telefono (si existe el campo)
        """
        user = request.user

        first_name = (request.data.get("first_name") or "").strip()
        last_name = (request.data.get("last_name") or "").strip()
        nuevo_email = (request.data.get("email") or "").strip()
        telefono = (request.data.get("telefono") or "").strip()

        # Actualizar nombre
        if first_name:
            user.first_name = first_name
        if last_name:
            user.last_name = last_name

        if nuevo_email and nuevo_email != user.email:
            if User.objects.exclude(pk=user.pk).filter(username=nuevo_email).exists():
                return Response(
                    {"detail": "Ya existe un usuario con ese correo."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            user.username = nuevo_email
            user.email = nuevo_email

        user.save()

        # Actualizamos perfil (paciente o médico) si existe
        paciente = Paciente.objects.filter(user=user).first()
        medico = Medico.objects.filter(user=user).first()

        if paciente and hasattr(paciente, "telefono"):
            paciente.telefono = telefono
            paciente.save()
        elif medico and hasattr(medico, "telefono"):
            medico.telefono = telefono
            medico.save()

        rol = self._detectar_rol(user, paciente=paciente, medico=medico)

        data = {
            "id": user.id,
            "first_name": user.first_name or "",
            "last_name": user.last_name or "",
            "email": user.email or "",
            "telefono": telefono,
            "rol": rol
        }

        return Response(data, status=status.HTTP_200_OK)