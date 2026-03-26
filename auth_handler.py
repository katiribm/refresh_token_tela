import requests
import json

class Autorizacao:
    def __init__(self, client_id:str, redirect_uri:str, token:str, user_access:str): 
        self.client_id = client_id
        self.redirect_uri = redirect_uri
        self.token = token
        self.user_access = user_access
        self.scopes = [
            "campos-adicionais.suite", "contas-usuarios.suite", "dados.suite",
            "gerenciador-configuracoes.suite", "gerenciador-relatorios.suite",
            "gerenciador-scripts.suite", "licenses.suite", "modelo-dados.suite",
            "naturezas.suite", "notifications.suite", "quartz.suite",
            "sistema_interno", "user-accounts.suite"
        ]

    def getToken(self, force_refresh=False):
        if not force_refresh and self.valid():
            return 'Bearer ' + str(self.token)
        else:
            print("[AVISO] Token expirado ou refresh forçado. Tentando atualizar...")
            novo_token = self.refresh()
            if novo_token:
                return 'Bearer ' + str(novo_token)
            return 'Bearer ' + str(self.token)

    def getUserAccess(self):
        return str(self.user_access)

    @property
    def dict_header(self):
        return {
            "Authorization": self.getToken(), 
            "User-Access": self.getUserAccess(),
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    def refresh(self):
        try:
            print(f"Token Antigo (parcial): {self.token[:10]}...")
            novo_token_response = requests.get(
                url="https://plataforma-oauth.betha.cloud/auth/oauth2/authorize",
                params={
                    'client_id': self.client_id,
                    'response_type': 'token',
                    'redirect_uri': self.redirect_uri,
                    'silent': 'true',
                    'callback': '',
                    'bth_ignore_origin': 'true',
                    'previous_access_token': self.token
                },
                timeout=20
            )
            response_text = novo_token_response.text
            if response_text.startswith("(") and response_text.endswith(")"):
                response_text = response_text[1:-1]
            novo_token_data = json.loads(response_text)
            novo_token = novo_token_data.get("accessToken")
            if novo_token:
                print("--- Token Atualizado com Sucesso ---")
                self.token = novo_token
                return novo_token
            return None
        except Exception as e:
            print(f"[ERRO] Exceção no refresh: {e}")
            return None

    @property
    def infos(self):
        try:
            request = requests.get(
                url='https://plataforma-oauth.betha.cloud/auth/oauth2/tokeninfo',
                params={"access_token": self.token},
                timeout=10
            ) 
            return request.json() if request.status_code == 200 else {"expired": True}
        except:
            return {"expired": True}

    def valid(self):
        info = self.infos
        return info and not info.get("expired", True)