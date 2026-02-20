from celery.signals import (
    task_prerun,
    task_success,
    task_failure
)

from .models import Processamento

@task_prerun.connect(weak=False)
def task_iniciada(sender=None, task_id=None, **kwargs):

    if sender.name != "smartcard.tasks.processar_xls":
        return

    Processamento.objects.filter(
        task_id=task_id
    ).update(status="PROCESSANDO")


@task_success.connect(weak=False)
def task_finalizada(sender=None, result=None, **kwargs):

    if sender.name != "smartcard.tasks.processar_xls":
        return

    task_id = sender.request.id

    Processamento.objects.filter(
        task_id=task_id
    ).update(status="SUCCESS")


@task_failure.connect(weak=False)
def task_erro(sender=None, task_id=None, exception=None, **kwargs):

    if sender.name != "smartcard.tasks.processar_xls":
        return

    Processamento.objects.filter(
        task_id=task_id
    ).update(status="ERRO")