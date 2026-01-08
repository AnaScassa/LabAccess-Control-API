from rest_framework.decorators import api_view
from rest_framework.response import Response
from smartCard.models import Acesso, Usuario
from .models import User
from .serializers import UserApiSerializer
from rest_framework import viewsets
from django.utils import timezone
from rest_framework import status
import pandas as pd

@api_view(['GET'])
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
    return Response(list(acessos), status=200)

@api_view(['GET'])
def lista_usuarios(request):
   
    usuarios = Usuario.objects.values(
        'id',
        'nome_usuario'
    )
    return Response(list(usuarios), status=200)

class UserViewSetApi(viewsets.ModelViewSet):
    
    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = UserApiSerializer

@api_view(['POST'])
def carregar_acesso(request):

    if 'file' not in request.FILES:
        return Response(
            {"erro": "Nenhum arquivo enviado. Use 'arquivo' no form-data."},
            status=status.HTTP_400_BAD_REQUEST
        )

    arquivo = request.FILES['file']

    if not arquivo.name.endswith(".xls"):
        return Response(
            {"erro": "Apenas arquivos .xls são permitidos."},
            status=status.HTTP_400_BAD_REQUEST 
        )

    try:
        df = pd.read_excel(arquivo, engine="xlrd")
    except Exception as e:
        return Response(
            {"erro": f"Erro ao processar planilha: {e}"},
            status=status.HTTP_400_BAD_REQUEST
        )

    novos = 0
    duplicados = 0

    for _, row in df.iterrows():
        categoria = str(row.get("MATRICULA", ""))[:3]

        usuario, _ = Usuario.objects.get_or_create(
            matricula=row.get("MATRICULA", ""),
            defaults={
                "nome_usuario": row.get("NOME_ALUNO", "Desconhecido"),
                "categoriaUsuario": categoria
            }
        )

        data = timezone.make_aware(row.get("DATA"))

        _, created = Acesso.objects.get_or_create(
            usuario=usuario,
            data_acesso=data,
            desc_evento=row.get("DESC_EVENTO", ""),
            desc_area=row.get("DESC_AREA", ""),
            desc_leitor=row.get("DESC_LEITOR", ""),
            ent_sai=row.get("ENT_SAI", "")
        )

        if created:
            novos += 1
        else:
            duplicados += 1

    return Response({
        "novos_registros": novos,
        "registros_duplicados": duplicados,
        "total_linhas": len(df)
    }, status=status.HTTP_201_CREATED)