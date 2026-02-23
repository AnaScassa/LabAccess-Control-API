from celery.signals import (
    after_task_publish,
    task_prerun,
    task_success,
    task_failure
)
from .models import Processamento

#start transaction
@task_prerun.connect(weak=False)
def task_iniciada(sender=None, task_id=None, task=None, **kwargs):
    processo = Processamento.objects.filter(user__isnull=False).first()
    if processo:
        usuario = processo.user
    Processamento.objects.update_or_create(
        task_id=task_id,
        defaults={
            "task_id_parent": task.request.parent_id,
            "status": "PROCESSANDO",
            "user": usuario
        }
    )

@after_task_publish.connect(weak=False)
def task_enviada(sender=None, headers=None, **kwargs):

    task_id = headers.get("id")

    Processamento.objects.update_or_create(
        task_id=task_id,
        defaults={
            "status": "PENDING"
        }
    )
   
@task_prerun.connect(weak=False)
def task_iniciada(sender=None, task_id=None, **kwargs):

    Processamento.objects.filter(
        task_id=task_id
    ).update(status="PROCESSANDO")


@task_success.connect(weak=False)
def task_finalizada(sender=None, result=None, **kwargs):

    task_id = sender.request.id

    Processamento.objects.filter(
        task_id=task_id
    ).update(status="SUCCESS")


@task_failure.connect(weak=False)
def task_erro(sender=None, task_id=None, exception=None, **kwargs):

    Processamento.objects.filter(
        task_id=task_id
    ).update(status="ERRO")
