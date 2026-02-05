from celery import shared_task
import pandas as pd
import requests
from .models import Usuario, Acesso
from .services import tentar_vincular_user_auth

@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=5, retry_kwargs={"max_retries": 3})
def processar_xls(self, caminho_arquivo):
    print("PROCESSANDO:", caminho_arquivo)

    df = pd.read_excel(caminho_arquivo)

    headers = {
        "X-Api-Key": "pbkdf2_sha256$1200000$aonByYw2GbwuyDvrGd1z9w4x5BO477iAMn69G1gs3W1C3n1ZmLwxHpBZoKFIIQV0=",        
        "Authorization": "Api-Key xb8vL1sU.wnTtzS31MbyyKeRICGTxTfvHKuxTSBt0",
    }

    users = requests.get(
        "http://localhost:8000/api/users/user/",
        headers=headers,
        timeout=10
    ).json()

    profiles = requests.get(
        "http://localhost:8000/api/users/user-profile/",
        headers=headers,
        timeout=10
    ).json()

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

        data = row.get("DATA")
        Acesso.objects.get_or_create(
            usuario=usuario,
            data_acesso=data,
            desc_evento=row.get("DESC_EVENTO", ""),
            desc_area=row.get("DESC_AREA", ""),
            ent_sai=row.get("ENT_SAI", ""),
            defaults={
                "desc_leitor": row.get("DESC_LEITOR", "")
            }
        )

        tentar_vincular_user_auth(usuario, users, profiles)


    print("PROCESSAMENTO FINALIZADO")
