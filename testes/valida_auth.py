import os
import requests
from dotenv import load_dotenv
from auth_handler import Autorizacao

def validar_configuracoes():
    load_dotenv()
    
    print("🔍 --- Iniciando Diagnóstico de Autenticação ---")
    
    # 1. Verificar Variáveis de Ambiente
    campos = ["CLIENT_ID", "REDIRECT_URI", "TOKEN_TELA", "USER_ACCESS"]
    erro_env = False
    for campo in campos:
        valor = os.getenv(campo)
        if not valor:
            print(f"❌ Erro: Variável {campo} não encontrada no .env")
            erro_env = True
        else:
            print(f"✅ {campo}: {valor[:5]}...{valor[-5:] if len(valor) > 5 else ''}")
    
    if erro_env:
        return

    # 2. Instanciar Classe
    auth = Autorizacao(
        client_id=os.getenv("CLIENT_ID"),
        redirect_uri=os.getenv("REDIRECT_URI"),
        token=os.getenv("TOKEN_TELA"),
        user_access=os.getenv("USER_ACCESS")
    )

    # 3. Testar validade do Token Atual (Tokeninfo)
    print("\n📡 Testando validade do Token atual via /tokeninfo...")
    info = auth.infos
    if info.get("expired"):
        print("⚠️  Status: O token atual no .env já está EXPIRADO.")
    else:
        print(f"✅ Status: Token ainda é VÁLIDO. Expira em: {info.get('expires_in')} segundos.")

    # 4. Testar o Refresh (Onde deu o erro 400)
    print("\n🔄 Testando solicitação de Refresh (Silent Login)...")
    url_refresh = f"{auth.oauth_url}/authorize"
    params = {
        'client_id': auth.client_id,
        'response_type': 'token',
        'redirect_uri': auth.redirect_uri,
        'silent': 'true',
        'bth_ignore_origin': 'true',
        'previous_access_token': auth.token
    }
    
    try:
        res = requests.get(url_refresh, params=params, timeout=15)
        print(f"📥 Status HTTP da Resposta: {res.status_code}")
        
        if res.status_code == 400:
            print("❌ ERRO 400: A Betha rejeitou os parâmetros.")
            print("👉 Verifique se o REDIRECT_URI é IDÊNTICO ao do console Betha.")
            print("👉 Verifique se o CLIENT_ID pertence a esse ambiente.")
        elif res.status_code == 200:
            if "accessToken" in res.text:
                print("✅ SUCESSO: O servidor aceitou o refresh e devolveu um novo token!")
            else:
                print(f"❓ Resposta inesperada (200 mas sem token): {res.text[:100]}")
        else:
            print(f"❌ Erro Desconhecido: {res.text}")
            
    except Exception as e:
        print(f"💥 Falha crítica na conexão: {e}")

if __name__ == "__main__":
    validar_configuracoes()