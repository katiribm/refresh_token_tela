import hashlib
import pandas as pd
import unicodedata
import sys
import datetime
import re
import json
import gc
import ctypes
import platform
from fuzzywuzzy import fuzz
from sqlalchemy import text
from concurrent.futures import ThreadPoolExecutor
from utils.conexao.conectaBanco import PostgresConnection
from utils.envio_sl.envia_analisa_dados_sl import analisa_lote_paralelo
import binascii


def geraHash(*args):
    # print(args)
    stringToHash = ""
    for argumento in args:
        if argumento is not None:
            stringToHash += str(argumento)
    return hashlib.md5(stringToHash.encode("utf-8")).hexdigest()


def inserir_dado_tabela_controle(registro, conexao):

    query_tabela_controle_migracao = text(
        """
            insert into controle_migracao_registro(tipo_registro, id_gerado, i_chave_dsk1, i_chave_dsk2, i_chave_dsk3, i_chave_dsk4, i_chave_dsk5, situacao_registro, mensagem, hash_chave_dsk, json_enviado)
            values (:tipo_registro, :id_gerado, :i_chave_dsk1, :i_chave_dsk2, :i_chave_dsk3, :i_chave_dsk4, :i_chave_dsk5, :situacao_registro, :mensagem, :hash_chave_dsk, :json_enviado)
            ON CONFLICT (hash_chave_dsk) DO NOTHING;
        """
    )

    try:
        if registro:
            conexao.execute(query_tabela_controle_migracao, registro)
            conexao.commit()
            print(f"\n ---- Tabela de controle atualizada com sucesso!\n")
    except Exception as e:
        conexao.rollback()
        print(f'(* Erro ao executar função "inserir_dado_tabela_controle". {e}')
        sys.exit()


def inserir_dado_tabela_controle_alteracao_registro(registro, conexao):

    query_tabela_controle_migracao = text(
        """
            insert into controle_alteracao_registro(tipo_registro, id_gerado, i_chave_dsk1, i_chave_dsk2, i_chave_dsk3, i_chave_dsk4, i_chave_dsk5, situacao_registro, mensagem, hash_chave_dsk, json_enviado)
            values (:tipo_registro, :id_gerado, :i_chave_dsk1, :i_chave_dsk2, :i_chave_dsk3, :i_chave_dsk4, :i_chave_dsk5, :situacao_registro, :mensagem, :hash_chave_dsk, :json_enviado)
            ON CONFLICT (tipo_registro, hash_chave_dsk) DO NOTHING;
        """
    )

    try:
        if registro:
            conexao.execute(query_tabela_controle_migracao, registro)
            conexao.commit()
            print(f"\n ---- Tabela de controle alteracao atualizada com sucesso!\n")
    except Exception as e:
        conexao.rollback()
        print(
            f'(* Erro ao executar função "inserir_dado_tabela_controle_alteracao_registro". {e}'
        )
        sys.exit()


def inserir_dado_tabela_controle_alteracao_registro_chunk(registro, db_pool):

    query_tabela_controle_migracao = text(
        """
            insert into controle_alteracao_registro(tipo_registro, id_gerado, i_chave_dsk1, i_chave_dsk2, i_chave_dsk3, i_chave_dsk4, i_chave_dsk5, situacao_registro, mensagem, hash_chave_dsk, json_enviado)
            values (:tipo_registro, :id_gerado, :i_chave_dsk1, :i_chave_dsk2, :i_chave_dsk3, :i_chave_dsk4, :i_chave_dsk5, :situacao_registro, :mensagem, :hash_chave_dsk, :json_enviado)
            ON CONFLICT (tipo_registro, hash_chave_dsk) DO NOTHING;
        """
    )

    chunk_size = 100000
    list_of_chunks = list(chunks(registro, chunk_size))

    print("\n Total de chunks: ", len(list_of_chunks))

    # Executa em paralelo
    with ThreadPoolExecutor(
        max_workers=6
    ) as executor:  # ajuste o max_workers conforme CPU e DB
        futures = [
            executor.submit(
                insert_chunk, chunk, query_tabela_controle_migracao, db_pool
            )
            for chunk in list_of_chunks
        ]


def inserir_dado_tabela_controle_chunk(registro, db_pool):

    print("\n---- Inserindo dados na tabela de controle")

    query_tabela_controle_migracao = text(
        """
            insert into controle_migracao_registro(tipo_registro, id_gerado, i_chave_dsk1, i_chave_dsk2, i_chave_dsk3, i_chave_dsk4, i_chave_dsk5, situacao_registro, mensagem, hash_chave_dsk, json_enviado)
            values (:tipo_registro, :id_gerado, :i_chave_dsk1, :i_chave_dsk2, :i_chave_dsk3, :i_chave_dsk4, :i_chave_dsk5, :situacao_registro, :mensagem, :hash_chave_dsk, :json_enviado)
            ON CONFLICT (hash_chave_dsk) DO NOTHING;
        """
    )

    chunk_size = 100000
    list_of_chunks = list(chunks(registro, chunk_size))

    print(" Total de chunks: ", len(list_of_chunks))

    # Executa em paralelo
    with ThreadPoolExecutor(
        max_workers=6
    ) as executor:  # ajuste o max_workers conforme CPU e DB
        futures = [
            executor.submit(
                insert_chunk, chunk, query_tabela_controle_migracao, db_pool
            )
            for chunk in list_of_chunks
        ]

    print(f"\n ---- Tabela de controle atualizada com sucesso!\n")


def insere_id_lote_tabela(registro, conexao):
    """
    Insere dados na tabela com base nos campos fornecidos: idLote, status, end_point.
    """
    query = text(
        """
        INSERT INTO controle_lote (
            idlote, status, end_point
        )
        VALUES (
            :idLote, :status, :end_point
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


def atualizar_id_gerado_tabela_controle(dados, conexao):
    query_atualizar = text(
        """
        UPDATE controle_migracao_registro
        SET id_gerado = :id_gerado,
        situacao_registro = :situacao_registro, 
        mensagem = :mensagem
        WHERE hash_chave_dsk = :hash_chave_dsk
        and tipo_registro = :tipo_registro
    """
    )

    try:
        if dados.get("hash_chave_dsk") is not None:
            conexao.execute(query_atualizar, dados)
            conexao.commit()
        else:
            print("* Parâmetros inválidos para a atualização.")
    except Exception as e:
        print(f'* Erro ao executar função "atualizar_id_gerado_tabela_controle". {e}')


def atualizar_id_gerado_tabela_controle_alteracao_registro(dados, conexao):
    query_atualizar = text(
        """
        UPDATE controle_alteracao_registro
        SET id_gerado = :id_gerado,
        situacao_registro = :situacao_registro, 
        mensagem = :mensagem
        WHERE hash_chave_dsk = :hash_chave_dsk
        and tipo_registro = :tipo_registro
    """
    )

    try:
        if dados.get("hash_chave_dsk") is not None:
            conexao.execute(query_atualizar, dados)
            conexao.commit()
        else:
            print("* Parâmetros inválidos para a atualização.")
    except Exception as e:
        print(f'* Erro ao executar função "atualizar_id_gerado_tabela_controle". {e}')


def atualizar_lote_status_para_analisado(id_lote, conexao, end_point):
    """
    Atualiza o status de um registro na tabela controle_lote para 'ANALISADO'
    com base no idLote fornecido.

    :param id_lote: O ID do lote a ser atualizado.
    :param conexao: Objeto de conexão com o banco de dados.
    """
    query = text(
        """
        UPDATE controle_lote
        SET status = 'ANALISADO'
        WHERE idlote = :idLote
        and end_point = :end_point;
    """
    )

    try:
        if id_lote:
            conexao.execute(query, {"idLote": id_lote, "end_point": end_point})
            conexao.commit()
    except Exception as e:
        conexao.rollback()
        print(f'* Erro ao executar função "atualizar_status_para_analisado". {e}')


def get_id_gerado(
    conn,
    tipo_registro=None,
    i_chave_dsk1=None,
    i_chave_dsk2=None,
    i_chave_dsk3=None,
    i_chave_dsk4=None,
    i_chave_dsk5=None,
    i_chave_dsk6=None,
    idGerado=None,
):

    hash_code = geraHash(
        tipo_registro,
        i_chave_dsk1,
        i_chave_dsk2,
        i_chave_dsk3,
        i_chave_dsk4,
        i_chave_dsk5,
        i_chave_dsk6,
    )
    if idGerado is not None:
        query = "select trim(tipo_registro) as tipo_registro, trim(hash_chave_dsk) as hash_chave_dsk, trim(situacao_registro) as situacao_registro, trim(id_gerado) as id_gerado, trim(i_chave_dsk1) as i_chave_dsk1, trim(i_chave_dsk2) as i_chave_dsk2, trim(i_chave_dsk3) as i_chave_dsk3, trim(i_chave_dsk4) as i_chave_dsk4, trim(i_chave_dsk5) as i_chave_dsk5, trim(mensagem) as mensagem, trim(json_enviado) as json_enviado from public.controle_migracao_registro where tipo_registro = %s and id_gerado = %s;"
        filtered_df = pd.read_sql(
            query,
            conn,
            params=(
                tipo_registro,
                idGerado,
            ),
        )

        if not filtered_df.empty:
            return filtered_df

    else:
        query = "select * from public.controle_migracao_registro where tipo_registro = %s and hash_chave_dsk = %s;"

        filtered_df = pd.read_sql(
            query,
            conn,
            params=(
                tipo_registro,
                hash_code,
            ),
        )

        if not filtered_df.empty:
            return filtered_df.get("id_gerado").item()

    return None


def verificar_hash_duplicados(hash_codes):
    vistos = set()
    duplicados = set()

    for hash_code in hash_codes:
        if hash_code in vistos:
            duplicados.add(hash_code)
        else:
            vistos.add(hash_code)

    return duplicados


def clean_string(input_string: str) -> str:
    """
    Remove acentos e caracteres especiais de uma string, mantendo apenas as letras.

    Args:
        texto (str): A string a ser "limpa".

    Returns:
        str: A string sem acentos e caracteres especiais.
    """
    # Normalize a string para remover acentos
    texto_normalizado = unicodedata.normalize("NFD", input_string)
    # Filtra apenas caracteres não combinantes (acentos) e mantém letras
    texto_limpo = "".join(
        c for c in texto_normalizado if unicodedata.category(c) != "Mn"
    )
    return texto_limpo


def clean_numbers(input_string: str) -> str:
    """
    Remove todos os caracteres não numéricos de uma string, mantendo apenas os números.

    Args:
        input_string (str): A string a ser "limpa".

    Returns:
        str: A string contendo apenas números.
    """
    return re.sub(r"\D", "", input_string)  # Remove tudo que não for número


def timestamp_to_month_year(timestamp: pd.Timestamp) -> str:
    """
    Transforma um timestamp em uma string no formato Mês/Ano.

    Args:
    timestamp (pd.Timestamp): O timestamp a ser transformado.

    Returns:
    str: A string no formato Mês/Ano.
    """
    months = [
        "jan",
        "fev",
        "mar",
        "abr",
        "mai",
        "jun",
        "jul",
        "ago",
        "set",
        "out",
        "nov",
        "dez",
    ]
    month_year = f"{months[timestamp.month - 1]}/{timestamp.year}"
    return month_year


def timestamp_to_year_month(timestamp: pd.Timestamp) -> str:
    """
    Transforma um timestamp em uma string no formato Ano/Mês.

    Args:
    timestamp (pd.Timestamp): O timestamp a ser transformado.

    Returns:
    str: A string no formato Ano/Mês.
    """
    month_year = f"{timestamp.year}/{timestamp.month:02d}"
    return month_year


# def timestamp_para_mes_ano(timestamp: pd.Timestamp) -> str:
#     """
#     Transforma um timestamp em uma string no formato Mês/Ano (ex: Jan/2025).

#     Args:
#         timestamp (pd.Timestamp): O timestamp a ser transformado.

#     Returns:
#         str: A string no formato Mês/Ano.
#     """
#     # Lista com as abreviações dos meses em português
#     meses = (
#         "Jan",
#         "Fev",
#         "Mar",
#         "Abr",
#         "Mai",
#         "Jun",
#         "Jul",
#         "Ago",
#         "Set",
#         "Out",
#         "Nov",
#         "Dez",
#     )

#     # O atributo 'month' retorna um número de 1 a 12.
#     # Subtraímos 1 para usá-lo como índice da nossa lista (que começa em 0).
#     mes_abreviado = meses[timestamp.month - 1]

#     # Formata a string de saída
#     mes_ano = f"{mes_abreviado}/{timestamp.year}"

#     return mes_ano

import pandas as pd
from typing import Union

def timestamp_para_mes_ano(timestamp: Union[pd.Timestamp, datetime.datetime]) -> str:
    """
    Transforma um timestamp em uma string no formato Mês/Ano (ex: 01/2025).

    Args:
        timestamp (pd.Timestamp ou datetime.datetime): O timestamp a ser transformado.

    Returns:
        str: A string no formato MM/AAAA (dois dígitos para o mês).
    """
    
    # Verifica se o timestamp é None ou pd.NaT antes de tentar formatar
    if pd.isna(timestamp):
        return None

    mes_ano = timestamp.strftime('%m/%Y')

    return mes_ano



def transform_date_column(column: list) -> list:
    """
    Identifica se a coluna é do tipo date ou datetime e transforma os valores em strings.

    Args:
    column (list): A coluna a ser transformada.

    Returns:
    list: A coluna com os valores de data transformados em strings.
    """
    if not column:
        return column

    transformed_column = []
    elem = column
    # for elem in column:
    if isinstance(elem, datetime.datetime):
        transformed_column.append(elem.strftime("%Y-%m-%d %H:%M:%S"))
    elif isinstance(elem, datetime.date):
        transformed_column.append(elem.strftime("%Y-%m-%d"))
    else:
        transformed_column.append(elem)

    return transformed_column[0]


"""select 
	cl.idLote
from controle_lote cl 
where cl.status = 'NAO_ANALISADO'
and cl.end_point = ''"""


def get_lotes_nao_analisados(conn, end_point=None):
    return pd.read_sql_query(
        "select cl.idLote from controle_lote cl where cl.status = 'NAO_ANALISADO' and cl.end_point = %s order by cl.data_hora_envio asc;",
        conn,
        params=(end_point,),
    ).to_dict(orient="records")
    # return pd.read_sql_query(
    #     "select cl.idLote from controle_lote cl where cl.end_point = %s order by cl.data_hora_envio asc;",
    #     conn,
    #     params=(end_point,),
    # ).to_dict(orient="records")


def get_lotes_travados(conn, executar=False):
    if executar:
        return pd.read_sql_query(
            "select cl.* from controle_lote cl where cl.status = 'NAO_ANALISADO' order by cl.end_point asc, cl.data_hora_envio desc",
            conn,
        ).to_dict(orient="records")


def buscar_por_hash(lista_dicionarios, hash_id):
    """
    Busca um dicionário em uma lista de dicionários pelo valor de 'hash_chave_dsk'.

    :param lista_dicionarios: Lista de dicionários.
    :param hash_id: O valor do hash a ser procurado.
    :return: O dicionário correspondente ou None se não encontrado.
    """
    return next(
        (d for d in lista_dicionarios if d.get("hash_chave_dsk") == hash_id), None
    )


def atualizar_id_gerado_tabela_intermediaria(conexao, nome_tabela, end_point):

    query = text(
        f"""
        UPDATE {nome_tabela}
            SET idgerado = CAST(cmr.id_gerado AS bigint)
        FROM controle_migracao_registro cmr
        WHERE {nome_tabela}.hash_id = cmr.hash_chave_dsk
            AND cmr.tipo_registro = :end_point
            AND (cmr.situacao_registro = 'SUCESSO' OR cmr.mensagem = 'EXTRACAO_CLOUD')
            AND {nome_tabela}.idgerado IS NULL;
    """
    )

    try:
        conexao.execute(query, {"end_point": end_point})
        conexao.commit()
        print(f" ---- Id's da tabela {nome_tabela} atualizada!")
    except Exception as e:
        conexao.rollback()
        print(
            f'* Erro ao executar função "atualizar_id_gerado_tabela_intermediaria". {e}'
        )


def atualizar_campo_alterado_tabela_intermediaria_ajuste(
    conexao, nome_tabela, end_point
):

    query = text(
        f"""
        UPDATE {nome_tabela}
            SET alterado = true
        FROM controle_alteracao_registro cmr
        WHERE {nome_tabela}.hash_id = cmr.hash_chave_dsk
            AND cmr.tipo_registro = :end_point
            AND (cmr.situacao_registro = 'SUCESSO')
            AND {nome_tabela}.alterado IS FALSE;
    """
    )

    try:
        conexao.execute(query, {"end_point": end_point})
        conexao.commit()
        print(f" ---- Campo alterado da tabela {nome_tabela} marcado como TRUE!")
    except Exception as e:
        conexao.rollback()
        print(
            f'* Erro ao executar função "atualizar_campo_alterado_tabela_intermediaria_ajuste". {e}'
        )


def limpar_string(texto: str) -> str:
    """
    Remove quebras de linha e espaços duplos de uma string.

    Args:
        texto (str): A string a ser limpa.

    Returns:
        str: A string limpa, sem quebras de linha ou espaços duplos.
    """
    return re.sub(r"[\s\n\r]+", " ", texto).replace(";", " ").strip()


def remover_campos_none(end_point, dicionario: dict) -> dict:
    """
    Remove campos com valores None de um dicionário.

    Args:
        dicionario (dict): O dicionário a ser processado.

    Returns:
        dict: Um novo dicionário sem os campos com valores None.
    """
    if end_point in dicionario and isinstance(dicionario[end_point], dict):
        dicionario[end_point] = {
            chave: valor
            for chave, valor in dicionario[end_point].items()
            if valor is not None
        }
    return dicionario


def get_id_gerado_logradouro_aux(conn, logradouro, municipio):

    query = """select 
                l.idgerado
            from logradouros l 
            inner join municipios m on m.idgerado = l.idmunicipio 
            where l.nome = %s and m.nome = %s"""

    filtered_df = pd.read_sql(
        query,
        conn,
        params=(
            logradouro,
            municipio,
        ),
    )

    if not filtered_df.empty:
        return filtered_df.get("idgerado").item()

    return None


def validar_inscricao_municipal(im: str) -> bool:
    """
    Valida a Inscrição Municipal (IM) com base no formato comum.

    :param im: Número da Inscrição Municipal.
    :return: True se for válida, False caso contrário.
    """
    print(im)
    if not im:
        return False

    im = re.sub(r"\D", "", im.strip())  # Remove caracteres não numéricos

    if 5 <= len(im) <= 15:  # Geralmente varia entre 5 e 15 dígitos
        return True

    return False


def validar_inscricao_estadual(ie: str) -> bool:
    """
    Valida a Inscrição Estadual (IE) considerando apenas o formato numérico geral.

    :param ie: Número da Inscrição Estadual.
    :return: True se for válida, False caso contrário.
    """
    if not ie:
        return False

    ie = re.sub(r"\D", "", ie.strip())  # Remove caracteres não numéricos

    return 8 <= len(ie) <= 14  # IE geralmente tem entre 8 e 14 dígitos


def clean_json_strings(data):
    """
    Remove quebras de linha e espaços extras de todas as strings dentro de um JSON.

    Args:
        data (dict or list): O JSON a ser limpo.

    Returns:
        dict or list: O JSON sem quebras de linha e espaços extras nas strings.
    """
    if isinstance(data, dict):
        return {key: clean_json_strings(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [clean_json_strings(item) for item in data]
    elif isinstance(data, str):
        return " ".join(
            data.replace("\r", "").replace("\n", " ").split()
        )  # Remove \r\n e espaços extras
    return data


def gerar_txt(jsons_list, arquivo_saida="saida.json"):
    """
    Gera um arquivo .txt a partir de uma lista de JSONs.

    :param jsons_list: Lista de dicionários JSON
    :param arquivo_saida: Nome do arquivo de saída (padrão: "saida.txt")
    """
    with open(arquivo_saida, "w", encoding="utf-8") as arquivo:
        # arquivo.write(json.dumps(jsons_list, ensure_ascii=False) + "\n")
        json.dump(jsons_list, arquivo, indent=4)


def gerar_txt_lista(lista, arquivo_saida="saida.json"):
    """
    Gera um arquivo .txt a partir de uma lista de JSONs.

    :param jsons_list: Lista de dicionários JSON
    :param arquivo_saida: Nome do arquivo de saída (padrão: "saida.txt")
    """
    with open(arquivo_saida, "w", encoding="utf-8") as arquivo:
        for item in lista:
            arquivo.write(str(item) + "\n")


def ler_arquivo_json(caminho_arquivo):
    try:
        with open(caminho_arquivo, "r", encoding="utf-8") as arquivo:
            lista_json = json.load(arquivo)
            return lista_json
    except Exception as e:
        print(f"Erro ao ler o arquivo JSON: {e}")
        return


# Função para inserir um chunk de dados
# def insert_chunk(chunk, query_insert, db_pool):

#     with db_pool.get_connection() as conn:
#         session = conn
#         try:
#             session.execute(query_insert, chunk)
#             session.commit()
#             return len(chunk)
#         except Exception as e:
#             session.rollback()
#             print(f"Erro no chunk: {e}")
#             return 0
#         finally:
#             session.close()

def insert_chunk(chunk, query_insert, db_pool):

    with db_pool.get_connection() as conn:
        try:
            conn.execute(query_insert, chunk) 
            
            conn.commit() 
            
            return len(chunk)
            
        except Exception as e:
            conn.rollback() 
            print(f"ERRO DE INSERÇÃO DE DADOS: {e}")
            if chunk:
                print(f"Primeiro item problemático (Debug): {chunk[0]}")
                
            return 0
            


# Divide a lista em chunks
def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def liberar_memoria():
    """Libera memória RAM devolvendo ao SO, se possível."""
    # Remove referências órfãs
    gc.collect()

    sistema = platform.system()

    try:
        if sistema == "Linux":
            # malloc_trim via glibc
            libc = ctypes.CDLL("libc.so.6")
            libc.malloc_trim(0)
        elif sistema == "Darwin":  # macOS
            # No macOS não há malloc_trim equivalente, mas podemos tentar purge
            libc = ctypes.CDLL("libc.dylib")
            libc.malloc_zone_pressure_relief(0, 0)
        elif sistema == "Windows":
            # Usa SetProcessWorkingSetSize para limpar páginas não usadas
            kernel32 = ctypes.windll.kernel32
            process = kernel32.GetCurrentProcess()
            kernel32.SetProcessWorkingSetSize(process, -1, -1)
        else:
            print(f"Sistema {sistema} não suportado para liberação agressiva.")
    except Exception as e:
        print(f"Falha ao liberar memória: {e}")


def carregar_ids_em_memoria(conn):
    query = """
        SELECT tipo_registro, hash_chave_dsk, id_gerado
        FROM public.controle_migracao_registro
        WHERE tipo_registro IN ('municipios', 'competencias', 'lista_servicos_entidades');
    """
    df = pd.read_sql(query, conn)
    # Criar dict { (tipo_registro, hash) : id_gerado }
    return {
        (row["tipo_registro"].strip(), row["hash_chave_dsk"].strip()): row["id_gerado"]
        for _, row in df.iterrows()
    }


def get_id_gerado_mem(tipo_registro, map_ids, *chaves):
    hash_code = geraHash(tipo_registro, *chaves)
    return map_ids.get((tipo_registro, hash_code))

def get_descricao_gerado_mem(tipo_registro, map_descricoes, *chaves):
    hash_code = geraHash(tipo_registro, *chaves)
    
    return map_descricoes.get((tipo_registro, hash_code))


def get_id_gerado_bairro_aux(conn, nomeBairro, municipio):
    if not municipio or not nomeBairro:
        return None

    query = """select 
            l.idgerado
        from bairros l 
        inner join municipios m on m.idgerado = l.idmunicipio 
        where l.nome = %s and m.nome = %s"""

    filtered_df = pd.read_sql(
        query,
        conn,
        params=(
            nomeBairro,
            municipio,
        ),
    )

    if not filtered_df.empty:
        return filtered_df.get("idgerado").item()

    return None


def fuzzy_similar(str1, str2):
    return fuzz.ratio(str1, str2)  # retorna a porcentagem de similaridade


def get_logradouro_id(
    logradouro_alvo: str, idMunicipio: int, df: pd.DataFrame, nome_coluna: str
) -> pd.Series:
    """
    Busca em um DataFrame o logradouro com o maior percentual de similaridade.

    Args:
        logradouro_alvo (str): A string do logradouro que você quer encontrar.
        df (pd.DataFrame): O DataFrame onde a busca será realizada.
        nome_coluna (str): O nome da coluna do DataFrame que contém os logradouros.

    Returns:
        pd.Series: A linha inteira do DataFrame que contém a melhor correspondência,
                   incluindo uma nova coluna 'pontuacao_similaridade'.
    """
    # Calcula a similaridade de cada logradouro no DataFrame com o logradouro_alvo
    # e armazena os resultados em uma nova coluna.

    df_municipio = df[df["idmunicipio"] == int(idMunicipio)].copy()

    # 2. Verificação de segurança: se o filtro resultar em um DataFrame vazio,
    # significa que o idMunicipio não existe nos dados.
    if df_municipio.empty:
        print(f"Aviso: Nenhum dado encontrado para o idMunicipio {idMunicipio}.")
        return pd.DataFrame()

    # 3. Calcula a similaridade apenas no DataFrame já filtrado.
    df_municipio["pontuacao_similaridade"] = df_municipio[nome_coluna].apply(
        lambda logradouro_df: fuzzy_similar(logradouro_alvo, logradouro_df)
    )

    # 4. Encontra o índice da linha com a maior pontuação de similaridade.
    indice_melhor_correspondencia = df_municipio["pontuacao_similaridade"].idxmax()

    # 5. Retorna a linha inteira correspondente a esse índice.
    melhor_correspondencia = df_municipio.loc[indice_melhor_correspondencia]

    return melhor_correspondencia


def carrega_logradouros(conn):
    query = """
        select
            l.*
        from logradouros l
        where l.idGerado is not null;
    """
    df = pd.read_sql(query, conn)
    return df


def get_bairro_id(
    bairro_alvo: str, idMunicipio: int, df: pd.DataFrame, nome_coluna: str
) -> pd.Series:
    """
    Busca em um DataFrame o bairro com o maior percentual de similaridade,
    restringindo a busca a um idMunicipio específico.

    Args:
        bairro_alvo (str): A string do bairro que você quer encontrar.
        idMunicipio (int): O ID do município para filtrar a busca.
        df (pd.DataFrame): O DataFrame onde a busca será realizada.
        nome_coluna (str): O nome da coluna do DataFrame que contém os bairros.

    Returns:
        pd.Series: A linha inteira do DataFrame que contém a melhor correspondência,
                   incluindo uma nova coluna 'pontuacao_similaridade'.
                   Retorna None se o idMunicipio não for encontrado.
    """
    # 1. Filtra o DataFrame para conter apenas dados do município desejado.
    df_municipio = df[df["idmunicipio"] == int(idMunicipio)].copy()

    # 2. Se o filtro resultar em um DataFrame vazio, retorna None.
    if df_municipio.empty:
        print(f"Aviso: Nenhum bairro encontrado para o idMunicipio {idMunicipio}.")
        return pd.DataFrame()

    # 3. Calcula a similaridade de cada bairro no DataFrame filtrado com o bairro_alvo.
    df_municipio["pontuacao_similaridade"] = df_municipio[nome_coluna].apply(
        lambda bairro_df: fuzzy_similar(bairro_alvo, bairro_df)
    )

    # 4. Encontra o índice da linha que tem a maior pontuação de similaridade.
    indice_melhor_correspondencia = df_municipio["pontuacao_similaridade"].idxmax()

    # 5. Retorna a linha inteira (uma Series) correspondente a esse índice.
    melhor_correspondencia = df_municipio.loc[indice_melhor_correspondencia]

    return melhor_correspondencia


def carrega_bairros(conn):
    query = """
        select
            b.*
        from bairros b
        where b.idGerado is not null;
    """
    df = pd.read_sql(query, conn)
    return df


def processar_lote_completo(lote, params, endpoint, tipo_registro, db_pool):
    """
    Função 'worker' que processa um único lote.
    """
    try:
        # Passo 1: Cada thread abre sua própria conexão
        with db_pool.get_connection() as conn:

            lote_formatado = {"idLote": lote.get("idlote")}

            # Passo 2: Chama a função de análise silenciosa
            retorno_lote = analisa_lote_paralelo(
                bearer=params["token"],
                post=lote_formatado,
                sistema="eNota Cloud",
                endPoint=endpoint,
                log=None,  # Idealmente, aqui você usaria um logger thread-safe
            )

            # Passo 3: Processa o retorno e atualiza o BD (lógica original)
            if retorno_lote:
                for item in retorno_lote:
                    dados_controle = {}
                    if item.get("erroPayload").get("mensagemErro"):
                        dados_controle["situacao_registro"] = "ERRO"
                    else:
                        dados_controle["situacao_registro"] = "SUCESSO"

                    dados_controle["id_gerado"] = item.get("sucessoPayload").get(
                        "idGerado"
                    )
                    dados_controle["mensagem"] = item.get("erroPayload").get(
                        "mensagemErro"
                    )
                    dados_controle["hash_chave_dsk"] = item.get("sucessoPayload").get(
                        "idIntegracao"
                    )
                    dados_controle["tipo_registro"] = tipo_registro

                    atualizar_id_gerado_tabela_controle(
                        conexao=conn, dados=dados_controle
                    )
                    atualizar_lote_status_para_analisado(
                        conexao=conn,
                        id_lote=lote_formatado.get("idLote"),
                        end_point=endpoint,
                    )
            conn.close()

        # Retorna o ID do lote processado e sucesso
        return (lote.get("idlote"), "Sucesso")

    except Exception as e:
        # Retorna o ID do lote e a mensagem de erro
        return (lote.get("idlote"), str(e))


def processar_lote_completo_ajustes(lote, params, endpoint, tipo_registro, db_pool):
    """
    Função 'worker' que processa um único lote.
    """
    try:
        # Passo 1: Cada thread abre sua própria conexão
        with db_pool.get_connection() as conn:

            lote_formatado = {"idLote": lote.get("idlote")}

            # Passo 2: Chama a função de análise silenciosa
            retorno_lote = analisa_lote_paralelo(
                bearer=params["token"],
                post=lote_formatado,
                sistema="eNota Cloud",
                endPoint=endpoint,
                log=None,  # Idealmente, aqui você usaria um logger thread-safe
            )

            # Passo 3: Processa o retorno e atualiza o BD (lógica original)
            if retorno_lote:
                for item in retorno_lote:
                    dados_controle = {}
                    if item.get("erroPayload").get("mensagemErro"):
                        dados_controle["situacao_registro"] = "ERRO"
                    else:
                        dados_controle["situacao_registro"] = "SUCESSO"

                    dados_controle["id_gerado"] = item.get("sucessoPayload").get(
                        "idGerado"
                    )
                    dados_controle["mensagem"] = item.get("erroPayload").get(
                        "mensagemErro"
                    )
                    dados_controle["hash_chave_dsk"] = item.get("sucessoPayload").get(
                        "idIntegracao"
                    )
                    dados_controle["tipo_registro"] = tipo_registro

                    atualizar_id_gerado_tabela_controle_alteracao_registro(
                        conexao=conn, dados=dados_controle
                    )
                    atualizar_lote_status_para_analisado(
                        conexao=conn,
                        id_lote=lote_formatado.get("idLote"),
                        end_point=endpoint,
                    )
            conn.close()

        # Retorna o ID do lote processado e sucesso
        return (lote.get("idlote"), "Sucesso")

    except Exception as e:
        # Retorna o ID do lote e a mensagem de erro
        return (lote.get("idlote"), str(e))

def decode_dirty_text(value):
    """
    Decodifica bytes ou memoryview para string, tratando caracteres inválidos.
    """
    if value is None:
        return None

    # Se já for string, retorna direto
    if isinstance(value, str):
        return value

    # --- A CORREÇÃO ESTÁ AQUI ---
    # Se for memoryview (retorno comum do psycopg2 para BYTEA), converte para bytes
    if isinstance(value, memoryview):
        value = value.tobytes()

    # Agora 'value' é garantidamente bytes.
    # Tenta decodificar como CP1252 (padrão Windows), substituindo erros
    try:
        return value.decode("cp1252", errors="replace")
    except:
        # Fallback para latin1 se necessário (raro chegar aqui com errors='replace' acima)
        try:
            return value.decode("latin1", errors="replace")
        except:
            # Último recurso: UTF-8 forçado ignorando erros
            return value.decode("utf-8", errors="ignore")


def decodificar_hex_seguro(valor_hex):
    """
    1. Recebe string Hexadecimal (ASCII puro).
    2. Converte para Bytes Brutos.
    3. Decodifica como CP1252 substituindo caracteres inválidos.
    """
    if not valor_hex:
        return ""

    try:
        # Converte a string hex de volta para bytes brutos (b'\xe0\x81...')
        bytes_brutos = binascii.unhexlify(valor_hex)

        # Aqui a mágica acontece: errors='replace' mata o byte 0x81
        return bytes_brutos.decode("cp1252", errors="replace")
    except Exception as e:
        # Log de erro se necessário, retorna vazio ou o original para não travar
        print(f"Erro ao converter: {e}")
        return ""