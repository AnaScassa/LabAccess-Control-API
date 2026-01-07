from rest_framework.decorators import api_view
from rest_framework.response import Response
from smartCard.models import Acesso, Usuario
from .models import User
from .serializers import UserApiSerializer
from rest_framework import viewsets

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
