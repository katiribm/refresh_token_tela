import pandas as pd
from utils.conexao.conectaBanco import PostgresConnection
import json


def salvar_tributos_no_postgres(lista_dados, nome_tabela):
    if not lista_dados:
        return

    try:
        df = pd.json_normalize(lista_dados)

        for col in df.columns:
            # Verifica se o primeiro item não nulo da coluna é uma lista ou dicionário
            sample_value = df[col].dropna().iloc[0] if not df[col].dropna().empty else None
            
            if isinstance(sample_value, (list, dict)):
                print(f"⚙️ Convertendo coluna complexa: {col}")
                df[col] = df[col].apply(lambda x: json.dumps(x, ensure_ascii=False) if x is not None else None)

        # 3. Persistência
        with PostgresConnection.connect(db_name="ajustes", port=5432) as conn:
            df.to_sql(
                nome_tabela, 
                con=conn.engine, 
                if_exists='append', 
                index=False, 
                chunksize=1000
            )
            
        print(f"✅ Sucesso: {len(df)} linhas inseridas na tabela '{nome_tabela}'.")
    except Exception as e:
        print(f"❌ Erro ao salvar no banco: {e}")