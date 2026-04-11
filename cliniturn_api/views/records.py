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


class RecordsListView(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        expedientes = []

        # ¿Es médico?
        medico_actual = Medico.objects.filter(user=request.user, activo=True).first()

        # Base de pacientes activos
        pacientes_qs = Paciente.objects.all()
        #if medico_actual and not request.user.is_superuser:
        #    pacientes_ids = (
        #        Cita.objects.filter(medico=medico_actual)
        #        .values_list("paciente_id", flat=True)
        #        .distinct()
        #    )
        #    pacientes_qs = pacientes_qs.filter(id__in=pacientes_ids)

        for paciente in pacientes_qs:
            citas = Cita.objects.select_related(
                "medico__user",
                "medico__especialidad"
            ).filter(paciente=paciente).order_by("-fecha", "-hora")

            if not citas.exists():
                continue

            ultima_cita = citas.first()
            total_citas = citas.count()

            medico = ultima_cita.medico
            medico_nombre = ""
            especialidad_nombre = ""

            if medico and medico.user:
                medico_nombre = f"{medico.user.first_name} {medico.user.last_name}"
            if medico and medico.especialidad:
                especialidad_nombre = medico.especialidad.nombre

            expedientes.append({
                "id": paciente.id,  # ID del PACIENTE
                "paciente": f"{paciente.user.first_name} {paciente.user.last_name}",
                "matricula": paciente.matricula,
                "medico": medico_nombre,
                "especialidad": especialidad_nombre,
                "ultima_cita": f"{ultima_cita.fecha} {ultima_cita.hora}",
                "total_citas": total_citas
            })

        return Response(expedientes, status=status.HTTP_200_OK)


class RecordDetailView(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        paciente_id = request.GET.get("id")

        # ¿Es médico?
        medico_actual = Medico.objects.filter(user=request.user, activo=True).first()

        pacientes_qs = Paciente.objects.select_related("user").filter(activo=True)

        if medico_actual and not request.user.is_superuser:
            pacientes_ids = (
                Cita.objects.filter(medico=medico_actual)
                .values_list("paciente_id", flat=True)
                .distinct()
            )
            pacientes_qs = pacientes_qs.filter(id__in=pacientes_ids)

        paciente = get_object_or_404(pacientes_qs, id=paciente_id)

        citas_qs = Cita.objects.select_related(
            "medico__user",
            "medico__especialidad"
        ).filter(paciente=paciente).order_by("-fecha", "-hora")

        ultima_cita = citas_qs.first()
        total_citas = citas_qs.count()

        medico_principal = ultima_cita.medico if ultima_cita else None

        medico_nombre = ""
        especialidad_nombre = ""
        if medico_principal and medico_principal.user:
            medico_nombre = f"{medico_principal.user.first_name} {medico_principal.user.last_name}"
        if medico_principal and medico_principal.especialidad:
            especialidad_nombre = medico_principal.especialidad.nombre

        citas_list = []
        for c in citas_qs:
            m = c.medico
            m_nombre = ""
            esp_nombre = ""
            if m and m.user:
                m_nombre = f"{m.user.first_name} {m.user.last_name}"
            if m and m.especialidad:
                esp_nombre = m.especialidad.nombre

            citas_list.append({
                "id": c.id,
                "fecha": c.fecha,
                "hora": c.hora,
                "motivo": c.motivo,
                "estado": c.estado,
                "medico": m_nombre,
                "especialidad": esp_nombre,
            })

        data = {
            "id": paciente.id,
            "paciente": f"{paciente.user.first_name} {paciente.user.last_name}",
            "matricula": paciente.matricula,
            "medico": medico_nombre,
            "especialidad": especialidad_nombre,
            "ultima_cita": f"{ultima_cita.fecha} {ultima_cita.hora}" if ultima_cita else None,
            "total_citas": total_citas,
            "citas": citas_list
        }

        return Response(data, status=status.HTTP_200_OK)


class RecordDownloadView(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        paciente_id = request.GET.get("id")

        # ¿Es médico?
        medico_actual = Medico.objects.filter(user=request.user, activo=True).first()

        pacientes_qs = Paciente.objects.select_related("user").filter(activo=True)

        if medico_actual and not request.user.is_superuser:
            pacientes_ids = (
                Cita.objects.filter(medico=medico_actual)
                .values_list("paciente_id", flat=True)
                .distinct()
            )
            pacientes_qs = pacientes_qs.filter(id__in=pacientes_ids)

        paciente = get_object_or_404(pacientes_qs, id=paciente_id)

        citas_qs = Cita.objects.select_related(
            "medico__user",
            "medico__especialidad"
        ).filter(paciente=paciente).order_by("-fecha", "-hora")

        ultima_cita = citas_qs.first()
        total_citas = citas_qs.count()

        medico_principal = ultima_cita.medico if ultima_cita else None

        medico_nombre = ""
        especialidad_nombre = ""
        if medico_principal and medico_principal.user:
            medico_nombre = f"{medico_principal.user.first_name} {medico_principal.user.last_name}"
        if medico_principal and medico_principal.especialidad:
            especialidad_nombre = medico_principal.especialidad.nombre

        citas_list = []
        for c in citas_qs:
            m = c.medico
            m_nombre = ""
            esp_nombre = ""
            if m and m.user:
                m_nombre = f"{m.user.first_name} {m.user.last_name}"
            if m and m.especialidad:
                esp_nombre = m.especialidad.nombre

            citas_list.append({
                "id": c.id,
                "fecha": c.fecha,
                "hora": c.hora,
                "motivo": c.motivo,
                "estado": c.estado,
                "medico": m_nombre,
                "especialidad": esp_nombre,
            })

        data = {
            "id": paciente.id,
            "paciente": f"{paciente.user.first_name} {paciente.user.last_name}",
            "matricula": paciente.matricula,
            "medico": medico_nombre,
            "especialidad": especialidad_nombre,
            "ultima_cita": f"{ultima_cita.fecha} {ultima_cita.hora}" if ultima_cita else None,
            "total_citas": total_citas,
            "citas": citas_list,
            "detalle": "Datos del expediente para generación de PDF en el frontend."
        }

        return Response(data, status=status.HTTP_200_OK)
