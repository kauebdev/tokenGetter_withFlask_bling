from flask import Flask, request, redirect
import json
import requests
import secrets
import os

app = Flask(__name__)

CLIENT_ID = 'SUA_CLIENT_ID'
CLIENT_SECRET = 'SEU_CLIENT_SECRET'
REDIRECT_URI = 'http://localhost:5000/callback'
STATE_FILE = 'bling_state.json'
CODE_FILE = 'bling_auth_code.json'
TOKEN_FILE = 'bling_access_token.json'

def save_json(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

def load_json(filename):
    if not os.path.exists(filename):
        return {}
    with open(filename) as f:
        return json.load(f)

@app.route('/')
def home():
    # Gera token state aleatório
    state = secrets.token_urlsafe(16)

    # Salva para validar depois
    save_json({'state': state}, STATE_FILE)

    # Monta link de autorização com o state
    auth_url = (
        f'https://www.bling.com.br/Api/v3/oauth/authorize'
        f'?response_type=code'
        f'&client_id={CLIENT_ID}'
        f'&redirect_uri={REDIRECT_URI}'
        f'&state={state}'
    )

    return f'''
        <h2>1️⃣ Clique abaixo para autorizar o app no Bling:</h2>
        <a href="{auth_url}" target="_blank">Autorizar App</a><br><br>
        <p>Depois de autorizar, você será redirecionado e o token será salvo localmente.</p>
    '''

@app.route('/callback')
def callback():
    code = request.args.get('code')
    state_received = request.args.get('state')

    if not code or not state_received:
        return 'Erro: Código ou state não encontrados na URL.'

    # Verifica se o state recebido é válido
    state_saved = load_json(STATE_FILE).get('state')
    if state_received != state_saved:
        return 'Erro: state inválido. Possível tentativa de CSRF ou expiração.'

    # Salva o código
    save_json({'code': code}, CODE_FILE)

    # Troca o code pelo token
    token_url = 'https://www.bling.com.br/Api/v3/oauth/token'
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }

    response = requests.post(token_url, headers=headers, data=data)

    if response.status_code == 200:
        token_info = response.json()
        save_json(token_info, TOKEN_FILE)
        return '✅ Token de acesso obtido e salvo com sucesso.'
    else:
        return f'❌ Erro ao obter token: {response.status_code}<br>{response.text}'

if __name__ == '__main__':
    app.run(debug=True)
