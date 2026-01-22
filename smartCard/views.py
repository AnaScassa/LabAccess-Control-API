from wsgiref import headers
from xml.parsers.expat import model
from django.shortcuts import get_object_or_404
import requests
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.utils import timezone

import pandas as pd

from smartCard.models import Acesso, Usuario
from users.models import User
from .serializers import UserApiSerializer
from rest_framework_api_key.permissions import HasAPIKey
from .models import Usuario
from fuzzywuzzy import fuzz


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

    if 'file' not in request.FILES:
        return Response(
            {"erro": "Nenhum arquivo enviado. Use 'file' no form-data."},
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

    #separa em dict por matriculas no index  acessos[matricula] = [lista de acessos]

    novos = 0
    duplicados = 0

    try:
        start = timezone.localtime()
        response = requests.get(
            "http://localhost:8000/api/users/user-profile/",
            headers={
                "X-Api-Key": "pbkdf2_sha256$1200000$aonByYw2GbwuyDvrGd1z9w$4x5BO477iAMn69G1gs3W1C3n1ZmLwxHpBZoKFII+QV0=",
                "Authorization": "Api-Key xb8vL1sU.wnTtzS31MbyyKeRICGTxTfvHKuxTSBt0",
            },
            timeout=5
        )
        response.raise_for_status()
        profiles = response.json()
        end = timezone.localtime()
        print(f"Tempo de resposta perfis: {(end - start).total_seconds()} segundos")
    except requests.RequestException:
        return Response(
            {"erro": "Não foi possível obter perfis de usuário."},
        )
    try:
        start = timezone.localtime()
        response = requests.get(
            "http://localhost:8000/api/users/user/",
            headers={
                "X-Api-Key": "pbkdf2_sha256$1200000$aonByYw2GbwuyDvrGd1z9w$4x5BO477iAMn69G1gs3W1C3n1ZmLwxHpBZoKFII+QV0=",
                "Authorization": "Api-Key xb8vL1sU.wnTtzS31MbyyKeRICGTxTfvHKuxTSBt0",
            },
            timeout=5
        )
        response.raise_for_status()
        users = response.json()
        end = timezone.localtime()
        print(f"Tempo de resposta usuários: {(end - start).total_seconds()} segundos")
    except requests.RequestException:
        return Response(
            {"erro": "Não foi possível obter usuários."},
        )
    start = timezone.localtime()

    # for no dict acesso
    for _, row in df.iterrows():
        matricula = str(row.get("MATRICULA", "")).strip()
        categoria = matricula[:3]

        usuario, _ = Usuario.objects.get_or_create(
            matricula=matricula,
            defaults={
                "nome_usuario": row.get("NOME_ALUNO", "Desconhecido"),
                "categoriaUsuario": categoria
            }
        )
        if usuario.user_auth == None:
            start_vinculo = timezone.localtime()
            tentar_vincular_user_auth(usuario, users, profiles)
            end_vinculo = timezone.localtime()
            #print(f"Tempo de vinculação usuário {usuario.matricula}: {(end_vinculo - start_vinculo).total_seconds()} segundos")

        data = row.get("DATA")
        if data and timezone.is_naive(data):
            data = timezone.make_aware(data)

        #trocar Acesso.get_or_create para bulk create depois

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
    end = timezone.localtime()
    print(f"Tempo de processamento registros: {(end - start).total_seconds()} segundos")
    return Response(
        {
            "novos_registros": novos,
            "registros_duplicados": duplicados,
            "total_linhas": len(df)
        },
        status=status.HTTP_201_CREATED
    )  

def tentar_vincular_user_auth(usuario, users, profiles):
    matricula = str(usuario.matricula).strip()
    if len(matricula) <= 3:
        return

    matriculaId = str(usuario.matricula).strip()[3:]

    for profile in profiles:
        academic_id = profile.get("academic_id")
        academic_id_norm = ''.join(filter(str.isdigit, str(academic_id)))

        if academic_id_norm == matriculaId:
            user_id = profile.get("user")
            if user_id:
                usuario.user_auth = int(user_id)
                usuario.save(update_fields=["user_auth"])
                return

    if not usuario.nome_usuario:
        return

    nome_usuario = usuario.nome_usuario.lower().strip()
    melhor = None
    score_max = 0

    for user in users:
        nome_api = user.get("full_name", "").lower().strip()

        score = fuzz.token_sort_ratio(nome_usuario, nome_api)
        if score > score_max:
            score_max = score
            melhor = user

    if melhor and score_max >= 80:
        user_id = melhor.get("id")
        if user_id:
            usuario.user_auth = int(user_id)
            usuario.save(update_fields=["user_auth"])
