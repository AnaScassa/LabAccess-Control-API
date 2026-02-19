# accounts/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Usuario

@receiver(post_save, sender=Usuario)
def create_user(sender, instance, created, **kwargs):
    if created:
        print(f"Novo usuário criado: {instance.nome_usuario} ({instance.matricula})")

@receiver(post_save, sender=Usuario)
def verificar_status_task(sender, instance, **kwargs):

    if instance.processamento_status == "PROCESSANDO":
        print(f"Task {instance.task_id} está sendo processada")

    elif instance.processamento_status == "SUCCESS":
        print(f"Task {instance.task_id} finalizada com sucesso")

    elif instance.processamento_status == "ERRO":
        print(f"Task {instance.task_id} deu erro")