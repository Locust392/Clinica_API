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
from datetime import datetime
from django.conf import settings
from django.template.loader import render_to_string
import string
import random
import json


class SpecialtiesAll(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        especialidades = Especialidad.objects.all().order_by("id")
        lista = EspecialidadSerializer(especialidades, many=True).data
        return Response(lista, 200)


class SpecialtiesView(generics.CreateAPIView):
    def get(self, request, *args, **kwargs):
        especialidad = get_object_or_404(Especialidad, id=request.GET.get("id"))
        especialidad = EspecialidadSerializer(especialidad, many=False).data
        return Response(especialidad, 200)

    # POST: registrar nueva especialidad
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        clave = request.data.get("clave", "")
        nombre = request.data.get("nombre", "")
        descripcion = request.data.get("descripcion", "")
        activa = request.data.get("activa", True)

        if Especialidad.objects.filter(nombre=nombre).exists():
            return Response({"message": f"La especialidad '{nombre}' ya está registrada"}, 400)

        especialidad = Especialidad.objects.create(
            nombre=nombre,
            descripcion=descripcion,
            activa=activa
        )
        especialidad.save()

        return Response({"especialidad_created_id": especialidad.id}, 201)


class SpecialtiesViewEdit(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def put(self, request, *args, **kwargs):
        especialidad = get_object_or_404(Especialidad, id=request.data["id"])
        especialidad.nombre = request.data["nombre"]
        especialidad.descripcion = request.data.get("descripcion", "")
        especialidad.activa = request.data.get("activa", True)
        especialidad.save()

        data = EspecialidadSerializer(especialidad, many=False).data
        return Response(data, 200)


class SpecialtyChangeStatusView(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def put(self, request, *args, **kwargs):
        especialidad = get_object_or_404(Especialidad, id=request.GET.get("id"))
        especialidad.activa = not especialidad.activa
        especialidad.save()
        data = EspecialidadSerializer(especialidad, many=False).data
        return Response(data, 200)
