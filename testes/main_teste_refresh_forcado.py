import os
import json
from dotenv import load_dotenv
from auth_handler import Autorizacao

load_dotenv()

def executar_teste_forcado():
    auth = Autorizacao(
        client_id=os.getenv("CLIENT_ID"),
        redirect_uri=os.getenv("REDIRECT_URI"),
        token=os.getenv("TOKEN_TELA"),
        user_access=os.getenv("USER_ACCESS")
    )

    print(f"🔑 Token atual no .env: {auth.token[:15]}...")

    print("🔄 Solicitando refresh forçado ao servidor da Betha...")
    
    # Ao passar force_refresh=True, ele ignora o valid() e chama o refresh()
    novo_token_bearer = auth.getToken(force_refresh=True)
    
    if novo_token_bearer:
        token_limpo = novo_token_bearer.replace('Bearer ', '')
        
        print(f"✅ Resultado: {novo_token_bearer[:22]}...")
        
        if token_limpo != os.getenv("TOKEN_TELA"):
            print("✨ SUCESSO: O token foi renovado e é DIFERENTE do original!")
        else:
            print("⚠️ O servidor retornou o mesmo token (comum se o original ainda for muito recente).")
            
        print("\n📡 Testando acesso com o novo token em Tributos...")
        headers = auth.dict_header # Agora já contém o novo token
        
        import requests
        #url_teste = "https://tributos.betha.cloud/service-layer-tributos/api/economicos?filter=&limit=20&offset=0&sort=codigo+desc"
        url_teste = "https://tributos.betha.cloud/tributos/dados/api/economicos"
        res = requests.get(url_teste, headers=headers, params={"limit": 1})
        
        if res.status_code == 200:
            print("🟢 GET após Refresh: FUNCIONOU (200 OK)")
        else:
            print(f"🔴 GET após Refresh: FALHOU (Status {res.status_code})")
            print(f"Mensagem: {res.text}")

    else:
        print("❌ FALHA: O refresh não retornou um novo token.")

if __name__ == "__main__":
    executar_teste_forcado()