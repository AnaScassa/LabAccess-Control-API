from django.urls import include, path
from rest_framework import routers
from smartCard.api import UserViewSet
from smartCard.views import UserViewSetApi
from smartCard.api import AcessoViewSet, GroupViewSet, UsuarioViewSet


router = routers.DefaultRouter()
router.register(r"userAuth", UserViewSetApi) 
router.register(r"groups", GroupViewSet)
router.register(r"acessos", AcessoViewSet)
router.register(r'usuarios', UsuarioViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path("userAuth2/", UserViewSetApi.as_view({'get': 'list'})),
]