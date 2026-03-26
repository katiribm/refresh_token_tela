import os
import json
from dotenv import load_dotenv

# Importação dos seus módulos isolados
from auth_handler import Autorizacao
from api_service import BethaGetService

# 1. Carrega as configurações do arquivo .env
load_dotenv()

def iniciar_extracao_completa():
    print("🚀 --- INICIANDO PROCESSO DE EXTRAÇÃO (GET) ---")

    auth = Autorizacao(
        client_id=os.getenv("CLIENT_ID"),
        redirect_uri=os.getenv("REDIRECT_URI"),
        token=os.getenv("TOKEN_TELA"),
        user_access=os.getenv("USER_ACCESS")
    )

    service = BethaGetService(auth)

    #base_url = "https://livroeletronico.betha.cloud/livro-eletronico/service-layer/api/v1/listas-servicos-leis"
    base_url = "https://livroeletronico.betha.cloud/livro-eletronico/service-layer/api/v1/pessoas/juridicas"
    
    print(f"📡 Alvo: {base_url}")

    try:
       
        print("📥 Coletando dados (aguarde paginação)...")
        lista_completa = service.get_all_pages(base_url, limit=50)

        if lista_completa:
            total = len(lista_completa)
            print(f"\n✅ SUCESSO! Total de registros extraídos: {total}")
            
            # 6. Exemplo de inspeção do primeiro registro
            print("\n--- Estrutura do Primeiro Registro ---")
            print(json.dumps(lista_completa[0], indent=2, ensure_ascii=False))

            # nome_arquivo = "extracao_listas_servicos.json"
            # with open(nome_arquivo, "w", encoding="utf-8") as f:
            #     json.dump(lista_completa, f, indent=4, ensure_ascii=False)
            
            # print(f"\n💾 Arquivo salvo com sucesso: {nome_arquivo}")
        else:
            print("\n⚠️  Nenhum registro foi retornado pela API.")

    except Exception as e:
        print(f"\n❌ Ocorreu um erro inesperado durante a extração: {e}")

if __name__ == "__main__":
    iniciar_extracao_completa()