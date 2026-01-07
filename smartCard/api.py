from django.contrib.auth.models import Group
from smartCard.models import User
from rest_framework import permissions, viewsets

from smartCard.models import Acesso, Usuario
from smartCard.serializers import GroupSerializer, UserSerializer, AcessoSerializer, UsuarioSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all().order_by("name")
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]

class AcessoViewSet(viewsets.ModelViewSet):
    queryset = Acesso.objects.all() 
    serializer_class = AcessoSerializer

class UsuarioViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Usuario.objects.all().order_by("nome_usuario")
    serializer_class = UsuarioSerializer 
    
    #criar endpoint carregar acessos