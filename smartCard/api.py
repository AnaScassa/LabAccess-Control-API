from django.contrib.auth.models import Group
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_api_key.permissions import HasAPIKey
from rest_framework.authentication import SessionAuthentication
from smartcard.models import User, Acesso, Usuario
from celery import current_app
from rest_framework.viewsets import ViewSet
from smartcard.serializers import (
    GroupSerializer,
    UserSerializer,
    AcessoSerializer,
    UsuarioSerializer,
    TaskSerializer,
)
from smartcard.views import agora_por_fila


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated | HasAPIKey]
    authentication_classes = [JWTAuthentication, SessionAuthentication]

class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all().order_by("name")
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated | HasAPIKey]
    authentication_classes = [JWTAuthentication, SessionAuthentication]

class AcessoViewSet(viewsets.ModelViewSet):
    queryset = Acesso.objects.all() 
    serializer_class = AcessoSerializer
    permission_classes = [IsAuthenticated | HasAPIKey]
    authentication_classes = [JWTAuthentication, SessionAuthentication]

class UsuarioViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Usuario.objects.all().order_by("nome_usuario")
    serializer_class = UsuarioSerializer 
    permission_classes = [IsAuthenticated | HasAPIKey]
    authentication_classes = [JWTAuthentication, SessionAuthentication]

    def get_queryset(self):
        return super().get_queryset()


class ListTasksApiView(ViewSet):

    def list(self, request):
        i = current_app.control.inspect()
        stats = i.stats() or {}

        total_por_fila = {
            "fila_rapida": 0,
            "fila_media": 0,
            "fila_pesada": 0,
        }

        for worker, info in stats.items():
            total = info.get("total", {})

            for task_name, count in total.items():
                if "tentar_vincular_user_auth" in task_name:
                    total_por_fila["fila_rapida"] += count
                elif "tentar_vincular_por_nome" in task_name:
                    total_por_fila["fila_media"] += count
                elif "processar_xls" in task_name:
                    total_por_fila["fila_pesada"] += count

        return Response({
            "workers_online": len(stats),
            "workers": list(stats.keys()),
            "total_por_fila": total_por_fila,
            "em_execucao_agora": agora_por_fila(),
        })
    
    # pega os workers ativos 
    # em cada worker pegar a quantia da fila
    #-----------------------------------------
    # usar o redis para carregar o json
    # para carregar o json nas tasks 