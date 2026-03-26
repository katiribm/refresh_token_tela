import os
import json
from dotenv import load_dotenv
from auth_handler import Autorizacao
from api_service import BethaGetService

load_dotenv()

def extrair_com_validacao(url_endpoint, forcar_refresh=False):
    print("\n" + "="*60)
    print("🔍 CONFIGURANDO AMBIENTE DE EXTRAÇÃO")
    print("="*60)

    auth = Autorizacao(
        client_id=os.getenv("CLIENT_ID"),
        redirect_uri=os.getenv("REDIRECT_URI"),
        token=os.getenv("TOKEN_TELA"),
        user_access=os.getenv("USER_ACCESS")
    )

    if forcar_refresh:
        print("🔄 OPÇÃO ATIVADA: Forçando renovação do token agora...")
        auth.getToken(force_refresh=True)
    
    # Validação visual do estado do token
    status_token = "✅ OK" if auth.valid() else "❌ EXPIRADO"
    print(f"🔹 Token em uso: {auth.token[:15]}... ({status_token})")

    service = BethaGetService(auth)
    print(f"📡 Alvo: {url_endpoint}")
    print("-" * 60)

    try:
        registros_totais = service.get_all_pages(url_endpoint, limit=20)
        
        print("-" * 60)
        if registros_totais:
            print(f"✅ SUCESSO! Total de registros processados: {len(registros_totais)}")
        else:
            print("⚠️ Finalizado sem registros ou erro de timeout persistente.")
            
    except Exception as e:
        print(f"💥 Erro crítico: {e}")

    print("="*60 + "\n")

if __name__ == "__main__":
    # Opção 1: Livro Cloud
    # url = "https://livroeletronico.betha.cloud/livro-eletronico/service-layer/api/v1/listas-servicos-leis"

    #Opção 2: Tributos Cloud
    #url = "https://tributos.betha.cloud/tributos/dados/api/economicos"
    #url = "https://tributos.betha.cloud/tributos/dados/api/debitos"
    url = "https://tributos.betha.cloud/tributos/dados/api/parcelamentos"
    
    # Altere conforme a necessidade do teste
    OPCAO_FORCAR_REFRESH = False
    
    extrair_com_validacao(url, forcar_refresh=OPCAO_FORCAR_REFRESH)


