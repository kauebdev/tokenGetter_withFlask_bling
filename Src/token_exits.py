import json
import os

CAMINHO = "data/tokens.json"

def salvar_token_novo(token_data):
    # 1. Tenta carregar o conteúdo atual
    if os.path.exists(CAMINHO):
        with open(CAMINHO, "r") as f:
            dados_existentes = json.load(f)
    else:
        dados_existentes = []

    # 2. Garante que seja uma lista
    if not isinstance(dados_existentes, list):
        dados_existentes = [dados_existentes]

    # 3. Adiciona o novo token ao histórico
    dados_existentes.append(token_data)

    # 4. Salva tudo novamente
    with open(CAMINHO, "w") as f:
        json.dump(dados_existentes, f, indent=2)

    print("✅ Novo token salvo sem apagar os anteriores.")
