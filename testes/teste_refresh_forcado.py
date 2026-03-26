import os
from dotenv import load_dotenv
from auth_handler import Autorizacao

load_dotenv()

def teste_refresh_isolado():
    auth = Autorizacao(
        client_id=os.getenv("CLIENT_ID"),
        redirect_uri=os.getenv("REDIRECT_URI"),
        token=os.getenv("TOKEN_TELA"),
        user_access=os.getenv("USER_ACCESS")
    )

    token_antigo = auth.token
    print(f"🔑 Token atual no .env: {token_antigo[:15]}...")

    print("🔄 Forçando renovação (Refresh)...")
    novo_token = auth.refresh()

    if novo_token:
        print("✅ Sucesso! O servidor da Betha gerou um novo token.")
        print(f"🔑 Novo Token: {novo_token[:15]}...")
        
        if novo_token == token_antigo:
            print("⚠️ Atenção: O token retornado é igual ao anterior. Isso pode ocorrer se o anterior ainda for muito recente.")
        else:
            print("✨ Token renovado com sucesso e atualizado na instância.")
    else:
        print("❌ Falha crítica: O refresh retornou None.")
        print("👉 Verifique se o TOKEN_TELA inicial não expirou totalmente ou se a REDIRECT_URI está correta.")

if __name__ == "__main__":
    teste_refresh_isolado()