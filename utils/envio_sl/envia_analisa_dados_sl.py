import os
from math import ceil
import datetime
import json
import requests
import time
from sqlalchemy.sql import text
# from utils.conexao.conectaBanco import PostgresConnection
# from utils.functions.functions import (
#     atualizar_lote_status_para_analisado,
#     atualizar_id_gerado_tabela_controle,
# )


def insere_id_lote_tabela(registro, conexao):
    """
    Insere dados na tabela com base nos campos fornecidos: idLote, status, end_point.
    """
    query = text(
        """
        INSERT INTO controle_lote (
            idlote, status, end_point, data_hora_envio
        )
        VALUES (
            :idLote, :status, :end_point, :data_hora_envio
        )
        ON CONFLICT (idlote) DO NOTHING;
    """
    )

    try:
        if registro:
            conexao.execute(query, registro)
            conexao.commit()
            print(" ---- Tabela de controle atualizada com sucesso!\n")
    except Exception as e:
        conexao.rollback()
        print(f'* Erro ao executar função "insere_id_lote_tabela". {e}')


def envia_lote(operacao, bearer, payload, sistema, api, log):
    if operacao not in ("POST", "PUT", "PATCH", "DELETE"):
        print("Tipo de operação incorreto! Utilize POST, PUT, PATCH ou DELETE")
        return None

    sistemas_validos = {
        "Educacao": "https://educacao.betha.cloud/service-layer/v2/api/",
        "Folha": "https://pessoal.betha.cloud/service-layer/v1/api/",
        "Tributos": "https://tributos.betha.cloud/service-layer-tributos/api/",
        "Protocolo": "https://api.protocolo.betha.cloud/protocolo/service-layer/v1/api/",
        "eNota Cloud": "https://nota-eletronica.betha.cloud/service-layer/api/",
    }

    if sistema not in sistemas_validos:
        print(
            "Sistema inválido, utilize Educacao, Folha, Tributos, Protocolo ou eNota Cloud"
        )
        return None

    urlPost = f"{sistemas_validos[sistema]}{api}"
    headers = {"Authorization": f"Bearer {bearer}", "Content-Type": "application/json"}

    for attempt in range(3):
        try:
            response = requests.request(
                operacao, urlPost, headers=headers, data=payload
            )
            print(response.json())
            response.raise_for_status()
            post = response.json()
            mensagem = "-" * 25 + "IdLote" + "-" * 25
            print(mensagem)
            log.write(mensagem + "\n")
            print(post)
            log.write(str(post) + "\n")
            return post
        except requests.exceptions.RequestException as e:
            mensagem = f"  -----Erro ao enviar a requisição: {e}. | Tentando novamente... ({attempt + 1}/3)"
            print(mensagem)
            log.write(mensagem + "\n")

    mensagem = "  ----Máximo de tentativas excedido."
    print(mensagem)
    log.write(mensagem + "\n")
    return None


def analisa_lote(post, bearer, sistema, endPoint, log):
    mensagem = f"\n  ----Iniciando analise do lote {post}"
    # print(mensagem)
    if log:
        log.write(mensagem + "\n")

    objetoRetorno = {"sucessoPayload": None, "erroPayload": None}
    listaObjetoRetorno = []
    retry = 0
    contagem_get = 0  # contador de requisições GET feitas

    headers = {"Authorization": f"Bearer {bearer}", "Content-Type": "application/json"}

    sistemas_validos = {
        "Folha": f"https://pessoal.betha.cloud/service-layer/v1/api/lote/lotes/{post.get('id')}",
        "Educacao": f"https://pessoal.betha.cloud/service-layer/v1/api/lotes/{post.get('id')}",
        "Tributos": f"https://tributos.betha.cloud/service-layer-tributos/api/{endPoint}/{post.get('idLote')}",
        "Protocolo": f"https://api.protocolo.betha.cloud/protocolo/service-layer/v1/api/lote/lotes/{post.get('id')}",
        "eNota Cloud": f"https://nota-eletronica.betha.cloud/service-layer/api/consulta/{post.get('idLote')}",
    }

    if sistema not in sistemas_validos:
        print(
            "Sistema inválido, utilize Educacao, Folha ,Tributos, Protocolo ou eNota Cloud"
        )
        return None

    url = sistemas_validos[sistema]

    while retry < 3:
        try:
            while contagem_get < 200:
                contagem_get += 1
                response = requests.request("GET", url, headers=headers)
                response.raise_for_status()
                lote = response.json()

                situacao_lote = (
                    lote.get("situacao")
                    if sistema not in ("Tributos", "eNota Cloud")
                    else lote.get("statusLote")
                )
                print(
                    "\r",
                    f"  ---- Situação do lote {post.get('idLote')}: {situacao_lote} | GET nº {contagem_get}",
                    end="",
                )

                if situacao_lote in (
                    "EXECUTADO",
                    "PROCESSADO",
                    "PROCESSADO_COM_ERRO",
                    "EXECUTADO_OK",
                    "EXECUTADO_PARCIALMENTE_OK",
                ):
                    print("")
                    for item in lote["retorno"]:
                        objetoRetorno = {}
                        idGerado = None
                        mensagemErro = None

                        idIntegracao = item.get("idIntegracao")

                        if item.get("mensagem"):
                            mensagem = f"  ** Erro no payload: {item} | Mensagem de erro: {item.get('mensagem')}"
                            mensagemErro = item.get("mensagem")
                            if log:
                                log.write(mensagem + "\n")
                        else:
                            idGerado = (
                                item.get("idGerado")
                                if sistema not in ("Tributos", "eNota Cloud")
                                else item.get("idGerado").get("id")
                            )

                        objetoRetorno["sucessoPayload"] = {
                            "idGerado": idGerado,
                            "idIntegracao": idIntegracao,
                        }
                        objetoRetorno["erroPayload"] = {
                            "mensagemErro": mensagemErro,
                            "idIntegracao": idIntegracao,
                        }

                        listaObjetoRetorno.append(objetoRetorno)

                    mensagem = "  ----Lote processado\n"
                    print(mensagem)
                    if log:
                        log.write(mensagem + "\n")
                    return listaObjetoRetorno

                time.sleep(1)

            # Se chegou aqui é porque bateu o limite de GETs sem processar
            print(f"\n⚠️ Lote {post} pode estar travado. Limite de 200 GETs atingido.")
            if log:
                log.write(
                    f"Lote {post} pode estar travado. Limite de 200 GETs atingido.\n"
                )
            return []  # retorna lista vazia

        except requests.exceptions.RequestException as e:
            retry += 1
            mensagem = (
                f"\nErro ao verificar o lote: {e}. Tentando novamente... ({retry}/3)"
            )
            print(mensagem)
            if log:
                log.write(mensagem + "\n")
            time.sleep(2)

    return listaObjetoRetorno


def collate(lst, n):
    return [lst[i : i + n] for i in range(0, len(lst), n)]


def post_em_lote(
    sistema,
    registro,
    tamanhoLote,
    bearer=None,
    api=None,
    operacao=None,
    analisaLote=None,
    connPostgres=None,
    tipo_registro_ajuste=None # UTILIZADO PARA OS AJUSTES, POIS ASSIM CONSIGO SABER EXATAMENTE QUAIS SÃO OS LOTES DE CADA AJUSTE
):

    log = open(
        f"Log_{os.path.basename(__file__)}_{datetime.datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}.txt",
        mode="w",
        encoding="iso-8859-1",
    )

    totalLotes = ceil(len(registro) / tamanhoLote)

    listasPayloads = collate(registro, tamanhoLote)

    lista_retornos = []
    retornoLote = None
    idPost = None
    id_lote = None

    for j in range(1, ceil(len(registro) / tamanhoLote) + 1):

        mensagem = f"\n----Enviando lote {j} de {totalLotes}"
        print(mensagem)
        log.write(mensagem + "\n")

        payload = json.dumps(listasPayloads[j - 1])

        idPost = envia_lote(
            operacao=operacao,
            bearer=bearer,
            api=api,
            payload=payload,
            sistema=sistema,
            log=log,
        )
        if idPost:
            id_lote = (
                idPost.get("idLote") if sistema == "eNota Cloud" else idPost.get("id")
            )
            print('id_lote:', id_lote)

            dict_lote = {
                "idLote": id_lote,
                "status": "NAO_ANALISADO",
                "end_point": api if not tipo_registro_ajuste else tipo_registro_ajuste,
                "data_hora_envio": datetime.datetime.now(),
            }

            # if operacao not in ("PATCH"):
            insere_id_lote_tabela(registro=dict_lote, conexao=connPostgres)
            # função que consegue inserir id de lote em uma tabela

        if idPost and analisaLote:
            retornoLote = analisa_lote(
                bearer=bearer, post=idPost, sistema=sistema, endPoint=api, log=log
            )

        lista_retornos.append({"idLote": id_lote, "retornoLote": retornoLote})
        # criado uma lista com os retornos.
        # Para analisar os retornos, basta fazer um for dos dados retornados na função post_em_lote

    return lista_retornos


def processar_um_lote(lote_do_banco, bearer_token, endpoint_sistema):
    """
    Função que analisa um único lote e retorna o resultado.
    É projetada para ser executada em uma thread separada.
    """
    print(f"  -- Processando lote {lote_do_banco.get('idlote')} em uma thread...")

    # Prepara o formato do lote para a função de análise
    lote_formatado = {
        "idLote": lote_do_banco.get("idlote"),
    }

    # Chama a função de análise que faz as requisições de API
    retorno_analise = analisa_lote(
        bearer=bearer_token,
        post=lote_formatado,
        sistema="eNota Cloud",
        endPoint=endpoint_sistema,
        log=None,
    )

    # Retorna tanto o resultado da análise quanto o lote original
    # para sabermos qual lote foi processado.
    return lote_formatado, retorno_analise


def analisa_lote_paralelo(post, bearer, sistema, endPoint, log):
    # Esta é uma cópia da sua função original, com os prints removidos ou comentados.
    mensagem = f"\n ----Iniciando analise do lote {post}"
    if log:
        log.write(mensagem + "\n")

    objetoRetorno = {"sucessoPayload": None, "erroPayload": None}
    listaObjetoRetorno = []
    retry = 0
    contagem_get = 0

    headers = {"Authorization": f"Bearer {bearer}", "Content-Type": "application/json"}

    sistemas_validos = {
        "Folha": f"https://pessoal.betha.cloud/service-layer/v1/api/lote/lotes/{post.get('id')}",
        "Educacao": f"https://pessoal.betha.cloud/service-layer/v1/api/lotes/{post.get('id')}",
        "Tributos": f"https://tributos.betha.cloud/service-layer-tributos/api/{endPoint}/{post.get('idLote')}",
        "Protocolo": f"https://api.protocolo.betha.cloud/protocolo/service-layer/v1/api/lote/lotes/{post.get('id')}",
        "eNota Cloud": f"https://nota-eletronica.betha.cloud/service-layer/api/consulta/{post.get('idLote')}",
    }

    if sistema not in sistemas_validos:
        # Em um ambiente paralelo, é melhor retornar o erro do que printar.
        return None

    url = sistemas_validos[sistema]

    while retry < 3:
        try:
            while contagem_get < 200:
                contagem_get += 1
                response = requests.request("GET", url, headers=headers)
                response.raise_for_status()
                lote = response.json()

                situacao_lote = (
                    lote.get("situacao")
                    if sistema not in ("Tributos", "eNota Cloud")
                    else lote.get("statusLote")
                )

                # PRINT REMOVIDO DAQUI

                if situacao_lote in (
                    "EXECUTADO",
                    "PROCESSADO",
                    "PROCESSADO_COM_ERRO",
                    "EXECUTADO_OK",
                    "EXECUTADO_PARCIALMENTE_OK",
                ):
                    for item in lote["retorno"]:
                        objetoRetorno = {}
                        idGerado = None
                        mensagemErro = None
                        idIntegracao = item.get("idIntegracao")

                        if item.get("mensagem"):
                            mensagem = f" ** Erro no payload: {item} | Mensagem de erro: {item.get('mensagem')}"
                            mensagemErro = item.get("mensagem")
                            if log:
                                log.write(mensagem + "\n")
                        else:
                            idGerado = (
                                item.get("idGerado")
                                if sistema not in ("Tributos", "eNota Cloud")
                                else item.get("idGerado").get("id")
                            )

                        objetoRetorno["sucessoPayload"] = {
                            "idGerado": idGerado,
                            "idIntegracao": idIntegracao,
                        }
                        objetoRetorno["erroPayload"] = {
                            "mensagemErro": mensagemErro,
                            "idIntegracao": idIntegracao,
                        }
                        listaObjetoRetorno.append(objetoRetorno)

                    if log:
                        log.write(f"Lote {post.get('idLote')} processado.\n")
                    return listaObjetoRetorno

                time.sleep(1)

            # Limite de GETs atingido
            if log:
                log.write(
                    f"Lote {post} pode estar travado. Limite de 200 GETs atingido.\n"
                )
            return []

        except requests.exceptions.RequestException as e:
            retry += 1
            if log:
                log.write(
                    f"\nErro ao verificar o lote: {e}. Tentando novamente... ({retry}/3)\n"
                )
            time.sleep(2)

    return listaObjetoRetorno
