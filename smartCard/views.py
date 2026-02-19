from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .tasks import processar_xls
from .services import salvar_arquivo_temporario
from django.urls import reverse
from django_celery_results.models import TaskResult
import uuid

from smartcard.models import Acesso, Usuario
from users.models import User
from .serializers import UserApiSerializer
from rest_framework_api_key.permissions import HasAPIKey
from .models import Usuario, Processamento

class UserViewSetApi(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = UserApiSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def lista_acessos(request):
    acessos = Acesso.objects.values(
        'id',
        'usuario_id',
        'data_acesso',
        'desc_evento',
        'desc_area',
        'desc_leitor',
        'ent_sai'
    )
    return Response(list(acessos), status=status.HTTP_200_OK)

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([HasAPIKey])
def lista_usuarios(request):
    usuarios = Usuario.objects.values(
        'id',
        'nome_usuario'
    )
    return Response(list(usuarios), status=status.HTTP_200_OK)

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated | HasAPIKey])
def carregar_acesso(request):

    arquivo = request.FILES.get("file")

    if not arquivo:
        return Response(
            {"erro": "Nenhum arquivo enviado."},
            status=status.HTTP_400_BAD_REQUEST
        )

    if not arquivo.name.endswith(".xls"):
        return Response(
            {"erro": "Apenas arquivos .xls são permitidos."},
            status=status.HTTP_400_BAD_REQUEST
        )

    caminho = salvar_arquivo_temporario(arquivo)

    task = processar_xls.delay(caminho)

    return Response(
        {
            "message": "Arquivo enviado para processamento.",
            "task_id": task.id,
            "status": "PENDING"
        },
        status=status.HTTP_202_ACCEPTED
    )

def agora_por_fila():
    return {
        "fila_rapida": TaskResult.objects.filter(
            status="STARTED",
            task_name__icontains="tentar_vincular_user_auth"
        ).count(),

        "fila_media": TaskResult.objects.filter(
            status="STARTED",
            task_name__icontains="tentar_vincular_por_nome"
        ).count(),

        "fila_pesada": TaskResult.objects.filter(
            status="STARTED",
            task_name__icontains="processar_xls"
        ).count(),
    }

@api_view(['GET'])
def status_task(request, task_id):
    processamento = Processamento.objects.filter(task_id=task_id).first()

    if not processamento:
        return Response({"erro": "Task não encontrada"}, status=404)

    return Response({
        "task_id": processamento.task_id,
        "status": processamento.status
    })
 
#user da sessão, task_id_parent
#primeiro as tasks, depois os signals e depois a view
#como passar o id, como guardar os ids, como recuperar os ids na view