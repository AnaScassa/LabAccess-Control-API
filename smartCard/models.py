from django.db import models
import requests
from thefuzz import fuzz
from django.db import models
from thefuzz import fuzz
from users.models import User, UserProfile

from django.db import models

class Usuario(models.Model):
    matricula = models.CharField(max_length=20, unique=True)
    nome_usuario = models.CharField(max_length=100)
    categoriaUsuario = models.CharField(max_length=50, blank=True, null=True)

    user_auth = models.BigIntegerField(
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.nome_usuario} ({self.matricula})"

class Acesso(models.Model):
    usuario = models.ForeignKey(
        Usuario,
        to_field = 'matricula',
        related_name ='acessos',
        on_delete=models.CASCADE
    ) 
    data_acesso = models.DateTimeField(null=True, blank=True)
    desc_evento = models.CharField(max_length=100) 
    desc_area = models.CharField(max_length=100) 
    desc_leitor = models.CharField(max_length=100) 
    ent_sai = models.CharField(max_length=10) 

    class Meta: 
        unique_together = ('usuario', 'data_acesso', 'desc_evento', 'desc_area', 'ent_sai') 

    def __str__(self): 
        return f"Acesso de {self.usuario.nome_usuario} em {self.data_acesso}" 
