from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from cliniturn_api.models import Consultorio
from cliniturn_api.serializers import ConsultorioSerializer
from django.db import transaction


class ConsultoriosAll(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        consultorios = Consultorio.objects.all().order_by("id")
        data = ConsultorioSerializer(consultorios, many=True).data
        return Response(data, 200)


class ConsultoriosView(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    # Obtener consultorio por ID (GET /consultorios/?id=1)
    def get(self, request, *args, **kwargs):
        consultorio = get_object_or_404(Consultorio, id=request.GET.get("id"))
        data = ConsultorioSerializer(consultorio, many=False).data
        return Response(data, 200)

    # Registrar nuevo consultorio (POST /consultorios/)
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        serializer = ConsultorioSerializer(data=request.data)
        if serializer.is_valid():
            consultorio = serializer.save()
            return Response({"consultorio_created_id": consultorio.id}, 201)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ConsultoriosViewEdit(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    # Editar consultorio (PUT /consultorios/edit/)
    def put(self, request, *args, **kwargs):
        consultorio = get_object_or_404(Consultorio, id=request.data["id"])
        serializer = ConsultorioSerializer(consultorio, data=request.data, partial=True)
        if serializer.is_valid():
            consultorio = serializer.save()
            data = ConsultorioSerializer(consultorio, many=False).data
            return Response(data, 200)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ConsultoriosChangeStatusView(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    # PUT /consultorios/change-status/?id=1
    def put(self, request, *args, **kwargs):
        consultorio = get_object_or_404(Consultorio, id=request.GET.get("id"))
        consultorio.disponible = not consultorio.disponible
        consultorio.save()
        data = ConsultorioSerializer(consultorio, many=False).data
        return Response(data, 200)
