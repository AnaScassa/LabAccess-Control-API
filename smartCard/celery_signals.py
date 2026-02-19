from celery.signals import (
    after_task_publish,
    task_prerun,
    task_success,
    task_failure
)
from .models import Processamento


@after_task_publish.connect(weak=False)
def task_enviada(sender=None, headers=None, **kwargs):
    task_id = headers.get("id")
    Processamento.objects.create(
        task_id=task_id,
        status="PENDING"
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
