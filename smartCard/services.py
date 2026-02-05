from fuzzywuzzy import fuzz
import os
import uuid
from django.conf import settings

def tentar_vincular_user_auth(usuario, users, profiles):
    matricula = str(usuario.matricula).strip()
    if len(matricula) <= 3:
        return

    matricula_id = matricula[3:]

    for profile in profiles:
        academic_id = profile.get("academic_id")
        academic_id_norm = ''.join(filter(str.isdigit, str(academic_id)))

        if academic_id_norm == matricula_id:
            user_id = profile.get("user_id")
            if user_id:
                usuario.user_auth = user_id
                usuario.save(update_fields=["user_auth"])
                return

    if not usuario.nome_usuario:
        return

    nome_usuario = usuario.nome_usuario.lower().strip()
    melhor = None
    score_max = 0

    for user in users:
        nome_db = (user.get("full_name") or "").lower().strip()
        score = fuzz.token_sort_ratio(nome_usuario, nome_db)

        if score > score_max:
            score_max = score
            melhor = user

    if melhor and score_max >= 80:
        usuario.user_auth = melhor["id"]
        usuario.save(update_fields=["user_auth"])

def salvar_arquivo_temporario(arquivo):
    os.makedirs(settings.MEDIA_ROOT, exist_ok=True)

    nome = f"{uuid.uuid4()}_{arquivo.name}"
    caminho = os.path.join(settings.MEDIA_ROOT, nome)

    with open(caminho, "wb") as destino:
        for chunk in arquivo.chunks():
            destino.write(chunk)

    print("ARQUIVO SALVO EM:", caminho)  
    print("EXISTE?", os.path.exists(caminho))

    return caminho
