from flask import Flask, request, redirect
import requests
import json
import webbrowser
from token_exits import salvar_token_novo

# === CONFIGURAÇÃO ===
with open("data/config.json") as f:
    config = json.load(f)

CLIENT_ID = config["client_id"]
CLIENT_SECRET = config["client_secret"]
REDIRECT_URI = config["redirect_uri"]
STATE = "seguranca123"

app = Flask(__name__)

# === ROTA INICIAL: REDIRECIONA PARA LOGIN DO BLING ===
@app.route("/")
def auth_bling():
    url = (
        "https://www.bling.com.br/Api/v3/oauth/authorize"
        f"?response_type=code&client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}&state={STATE}"
    )
    webbrowser.open(url)
    return "Redirecionando para o Bling..."

# === CALLBACK: BLING VAI REDIRECIONAR PRA CÁ ===
@app.route("/callback")
def callback():
    error = request.args.get("error")
    if error:
        return f"Erro: {error}"

    code = request.args.get("code")
    state = request.args.get("state")

    if state != STATE:
        return "Erro: State inválido."

    # Troca o code pelo access_token
    token_url = "https://www.bling.com.br/Api/v3/oauth/token"
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI
        # Remove client_id and client_secret from here
    }

    # Add client_id and client_secret to the 'auth' parameter for Basic Authentication
    response = requests.post(
        token_url,
        data=data,
        auth=(CLIENT_ID, CLIENT_SECRET) # <-- This is the change
    )
    token_data = response.json()

    salvar_token_novo(token_data)
    return f"Token recebido: {token_data.get('access_token', 'Nenhum token recebido')}"

# === INICIAR SERVIDOR ===
if __name__ == "__main__":
    app.run(debug=True)