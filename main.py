import os
from dotenv import load_dotenv
import requests
from auth_handler import Autorizacao
from api_service import BethaGetService  # Nome corrigido aqui
from database_handler import salvar_tributos_no_postgres

def executar_integracao():
    load_dotenv()
    
    # 1. Autenticação
    auth = Autorizacao(
        client_id=os.getenv('CLIENT_ID'),
        redirect_uri=os.getenv('REDIRECT_URI'),
        token=os.getenv('TOKEN_TELA'),
        user_access=os.getenv('USER_ACCESS').strip()
    )


    # 2. Instancia o serviço com o nome correto
    servico = BethaGetService(auth)


    url = f"""https://nota-eletronica.betha.cloud/nota-eletronica/notas/api/notas-fiscais?
    fields=id,nroNota,nroVerificacao,nroRps,dhEmissao,dhEmissaoRps,idContribuintes,dadosPrestador.nome,dadosPrestador.inscricao,
    dadosPrestador.tipoPessoa,dadosTomador.nome,dadosTomador.inscricao,dadosTomador.tipoPessoa,vlTotalServicos,vlTotalBaseCalculo,
    vlTotalIss,vlCreditoTributario,vlCreditoTributarioCancelado,situacao,situacaoGuia,dadosXml.status,tipoCertificado,
    competencias.descricao,chaveAcessoNotaNacional,nfEnviadaAdnNotaNacional,nroNotaNacional&filter="""

    # 3. Define o endpoint de Tributos 
    #url_tipos_logradouros = f"https://tributos.betha.cloud/tributos/v1/api/cadastros/bancos"
    #url_contribuintes = f"https://tributos.betha.cloud/tributos/v1/api/cadastros/referentes/contribuintes?filter=(situacao+%3D+%22ATIVO%22+and+tipo+%3D+%22FISICA%22)&sort=codigo+desc"    
    #url_economicos = "https://tributos.betha.cloud/tributos/v1/api/cadastros/referentes/economicos"
    #url_logradouros = "https://tributos.betha.cloud/tributos/v1/api/cadastros/enderecos/logradouros"
    #url_bairros = "https://tributos.betha.cloud/tributos/v1/api/cadastros/enderecos/bairros"
    #url_parcelamentos = "https://tributos.betha.cloud/tributos/v1/api/arrecadacao/parcelamentos/?filter=pessoa.id+in+(71431147)"
    #url_parcelamentos_parcelas = "https://tributos.betha.cloud/tributos/dados/api/parcelamentos/parcelas?filter=parcelamento.idContribuinte+in+(71431147)"
    #url_parcelamentos_composicoes = "https://tributos.betha.cloud/tributos/dados/api/parcelamentos/composicoes?filter=parcelamento.idContribuinte+in+(71431147)"
    #url_pagamentos_parcelamentos = "https://tributos.betha.cloud/tributos/dados/api/pagamentos/parcelamentos?filter=idContribuinte+in+(71431147)"
    

    print("🚀 Iniciando captura total de páginas...")
    
    # 4. Busca TUDO usando sua função de paginação
    lista_completa = servico.get_all_pages(url, limit=100)
    
    if lista_completa:
        print(f"📦 Total de {len(lista_completa)} registros encontrados.")
        # 5. Salva no Postgres (Passamos a lista direto agora)
        salvar_tributos_no_postgres(lista_completa, "stg_notas_fiscais")
    else:
        print("⚠️ Nenhum dado encontrado para processar.")


def executar_teste_reduzido():
    load_dotenv()
    
    # 1. Autenticação
    auth = Autorizacao(
        client_id=os.getenv('CLIENT_ID'),
        redirect_uri=os.getenv('REDIRECT_URI'),
        token=os.getenv('TOKEN_TELA'),
        user_access=os.getenv('USER_ACCESS')
    )

    servico = BethaGetService(auth)
    url_parcelamentos = "https://tributos.betha.cloud/tributos/v1/api/cadastros/referentes/parcelamentos"

    print("🧪 Rodando teste reduzido (limite: 10 registros)...")
    
    # Em vez de get_all_pages, usamos get_data diretamente para 1 página
    params = {"limit": 10, "offset": 0}
    dados_brutos = servico.get_data(url_parcelamentos, params=params)
    
    if dados_brutos:
        # Extraímos a lista usando a lógica que você já tem na classe
        lista_10 = (
            dados_brutos.get('conteudo') or 
            dados_brutos.get('content') or 
            dados_brutos.get('registros') or []
        )
        
        print(f"📦 Amostra de {len(lista_10)} registros capturada.")
        
        # Salvando no Postgres para validar a tabela
        salvar_tributos_no_postgres(lista_10, "teste_stg_tributos_contribuintes_10")
    else:
        print("❌ Não foi possível capturar a amostra.")

if __name__ == "__main__":
    executar_integracao()
    #executar_teste_reduzido()