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
from rest_framework import viewsets
from datetime import datetime
from django.conf import settings
from django.template.loader import render_to_string
import string
import random
import json


class ReportsSummaryView(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        total_pacientes = Paciente.objects.filter(user__is_active=1).count()
        total_medicos = Medico.objects.filter(user__is_active=1).count()
        total_citas = Cita.objects.all().count()

        citas_pendientes = Cita.objects.filter(estado='Pendiente').count()
        citas_confirmadas = Cita.objects.filter(estado='Confirmada').count()
        citas_canceladas = Cita.objects.filter(estado='Cancelada').count()

        data = {
            "total_pacientes": total_pacientes,
            "total_medicos": total_medicos,
            "total_citas": total_citas,
            "citas_pendientes": citas_pendientes,
            "citas_confirmadas": citas_confirmadas,
            "citas_canceladas": citas_canceladas
        }

        return Response(data, 200)


class ReportsKpisView(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        total_pacientes = Paciente.objects.filter(user__is_active=1).count()
        total_medicos = Medico.objects.filter(user__is_active=1).count()
        total_citas = Cita.objects.all().count()

        citas_pendientes = Cita.objects.filter(estado='Pendiente').count()
        citas_confirmadas = Cita.objects.filter(estado='Confirmada').count()
        citas_canceladas = Cita.objects.filter(estado='Cancelada').count()

        kpi_confirmacion = 0
        if total_citas > 0:
            kpi_confirmacion = round((citas_confirmadas / total_citas) * 100, 2)

        data = {
            "total_pacientes": total_pacientes,
            "total_medicos": total_medicos,
            "total_citas": total_citas,
            "citas_pendientes": citas_pendientes,
            "citas_confirmadas": citas_confirmadas,
            "citas_canceladas": citas_canceladas,
            "kpi_tasa_confirmacion": kpi_confirmacion
        }

        return Response(data, 200)
