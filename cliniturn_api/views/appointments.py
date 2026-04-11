from django.db import transaction
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count
from django.db.models import Count

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from django.contrib.auth.models import Group

from cliniturn_api.models import *
from cliniturn_api.serializers import *


class AppointmentsView(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        cita_id = request.GET.get("id")

        base_qs = Cita.objects.select_related(
            "paciente__user",
            "medico__user",
            "medico__especialidad"
        ).all().order_by("-fecha", "-hora")

        user = request.user
        medico_actual = Medico.objects.filter(user=user, activo=True).first()
        paciente_actual = Paciente.objects.filter(user=user, activo=True).first()

        if cita_id:
            qs = base_qs

            if medico_actual and not user.is_superuser:
                qs = qs.filter(medico=medico_actual)
            elif paciente_actual and not user.is_superuser:
                qs = qs.filter(paciente=paciente_actual)

            cita = get_object_or_404(qs, id=cita_id)
            data = CitaSerializer(cita, many=False).data
            return Response(data, 200)

        citas = base_qs

        if medico_actual and not user.is_superuser:
            citas = citas.filter(medico=medico_actual)
        elif paciente_actual and not user.is_superuser:
            citas = citas.filter(paciente=paciente_actual)

        paciente_id = request.GET.get("paciente_id")
        medico_id = request.GET.get("medico_id")
        estado = request.GET.get("estado")
        fecha = request.GET.get("fecha")

        if paciente_id:
            citas = citas.filter(paciente_id=paciente_id)
        if medico_id:
            citas = citas.filter(medico_id=medico_id)
        if estado:
            citas = citas.filter(estado=estado)
        if fecha:
            citas = citas.filter(fecha=fecha)

        data = CitaSerializer(citas, many=True).data
        return Response(data, 200)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        try:
            paciente_id = request.data.get("paciente_id") or request.data.get("paciente")
            medico_id = request.data.get("medico_id") or request.data.get("medico")
            consultorio_id = request.data.get("consultorio_id") or request.data.get("consultorio")
            especialidad_id = request.data.get("especialidad_id") or request.data.get("especialidad")

            paciente = get_object_or_404(Paciente, id=paciente_id)
            medico = get_object_or_404(Medico, id=medico_id)

            fecha = request.data.get("fecha")
            hora = request.data.get("hora")
            motivo = request.data.get("motivo", "")
            estado = request.data.get("estado", "Pendiente")

            cita = Cita.objects.create(
                paciente=paciente,
                medico=medico,
                fecha=fecha,
                hora=hora,
                motivo=motivo,
                estado=estado,
                consultorio_id=consultorio_id,
                especialidad_id=especialidad_id
            )

            return Response({"appointment_created_id": cita.id}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {"details": f"Ocurrió un error al crear la cita: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

    @transaction.atomic
    def put(self, request, *args, **kwargs):
        cita = get_object_or_404(Cita, id=request.data.get("id"))

        paciente_id = request.data.get("paciente_id") or request.data.get("paciente")
        medico_id = request.data.get("medico_id") or request.data.get("medico")
        consultorio_id = request.data.get("consultorio_id") or request.data.get("consultorio")
        especialidad_id = request.data.get("especialidad_id") or request.data.get("especialidad")

        if paciente_id:
            paciente = get_object_or_404(Paciente, id=paciente_id)
            cita.paciente = paciente

        if medico_id:
            medico = get_object_or_404(Medico, id=medico_id)
            cita.medico = medico

        if consultorio_id is not None:
            cita.consultorio_id = consultorio_id

        if especialidad_id is not None:
            cita.especialidad_id = especialidad_id

        if "fecha" in request.data:
            cita.fecha = request.data.get("fecha")

        if "hora" in request.data:
            cita.hora = request.data.get("hora")

        if "motivo" in request.data:
            cita.motivo = request.data.get("motivo")

        if "estado" in request.data:
            cita.estado = request.data.get("estado")

        cita.save()
        data = CitaSerializer(cita, many=False).data
        return Response(data, 200)

    @transaction.atomic
    def delete(self, request, *args, **kwargs):
        cita_id = request.GET.get("id") or request.data.get("id")

        if not cita_id:
            return Response(
                {"detail": "El parámetro 'id' es obligatorio para eliminar la cita."},
                status=status.HTTP_400_BAD_REQUEST
            )

        cita = get_object_or_404(Cita, id=cita_id)
        cita.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AppointmentConfirmView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        cita_id = request.data.get("id") or request.query_params.get("id")
        if not cita_id:
            return Response(
                {"detail": "El campo 'id' es obligatorio."},
                status=status.HTTP_400_BAD_REQUEST
            )

        cita = get_object_or_404(Cita, id=cita_id)

        user = request.user
        medico_actual = Medico.objects.filter(user=user, activo=True).first()

        # Admin por superuser o grupo
        es_admin = (
            user.is_superuser or
            user.groups.filter(name__in=['admin', 'administrador', 'administradora']).exists()
        )

        # Admin → puede todo; Médico → solo sus citas
        if not (es_admin or (medico_actual and cita.medico_id == medico_actual.id)):
            return Response(
                {"detail": "No tienes permiso para confirmar esta cita."},
                status=status.HTTP_403_FORBIDDEN
            )

        cita.estado = "Confirmada"
        cita.save()
        data = CitaSerializer(cita, many=False).data
        return Response(data, 200)


class AppointmentCancelView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        cita_id = request.data.get("id") or request.query_params.get("id")

        if not cita_id:
            return Response(
                {"detail": "El campo 'id' es obligatorio para cancelar la cita."},
                status=status.HTTP_400_BAD_REQUEST
            )

        cita = get_object_or_404(Cita, id=cita_id)

        user = request.user
        medico_actual = Medico.objects.filter(user=user, activo=True).first()
        paciente_actual = Paciente.objects.filter(user=user, activo=True).first()

        es_admin = (
            user.is_superuser or
            user.groups.filter(name__in=['admin', 'administrador', 'administradora']).exists()
        )

        autorizado = False

        # Admin: puede todo
        if es_admin:
            autorizado = True
        # Médico: solo sus citas
        elif medico_actual and cita.medico_id == medico_actual.id:
            autorizado = True
        # Paciente: solo sus citas
        elif paciente_actual and cita.paciente_id == paciente_actual.id:
            autorizado = True

        if not autorizado:
            return Response(
                {"detail": "No tienes permiso para cancelar esta cita."},
                status=status.HTTP_403_FORBIDDEN
            )

        cita.estado = "Cancelada"
        cita.save()

        data = CitaSerializer(cita, many=False).data
        return Response(data, status=status.HTTP_200_OK)

class AppointmentsBySpecialtyView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        # Traemos las citas con join a especialidad y a medico.especialidad
        qs = (
            Cita.objects
            .select_related('especialidad', 'medico__especialidad')
            .all()
        )

        conteo = {}

        for c in qs:
            nombre = None

            # 1) Si la cita tiene especialidad directa, usamos esa
            if c.especialidad and c.especialidad.nombre:
                nombre = c.especialidad.nombre
            # 2) Si no, intentamos con la especialidad del médico
            elif getattr(c.medico, 'especialidad', None) and c.medico.especialidad.nombre:
                nombre = c.medico.especialidad.nombre
            # 3) Si de plano no hay nada, agrupamos como "Sin especialidad"
            else:
                nombre = 'Sin especialidad'

            if nombre in conteo:
                conteo[nombre] += 1
            else:
                conteo[nombre] = 1

        # Ordenamos por nombre solo para que salga bonito
        labels = sorted(conteo.keys())
        data = [conteo[n] for n in labels]

        return Response(
            {
                "labels": labels,
                "data": data
            },
            status=status.HTTP_200_OK
        )
