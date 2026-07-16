import requests
import time
import json

class BethaGetService:
    def __init__(self, auth_provider):
        self.auth = auth_provider

    def get_data(self, url, params=None, max_retries=3):
        headers = self.auth.dict_header
        retries = 0

        print(f"DEBUG HEADERS: {headers}") 

        while retries < max_retries:
            try:
                response = requests.get(url, headers=headers, params=params, timeout=45)
                response.raise_for_status() 
                
                return response.json() 

            except requests.Timeout:
                retries += 1
                print(f"\n ⚠️ A API demorou para responder (Timeout). Tentativa {retries} de {max_retries}...")
                time.sleep(5) 
                
            except requests.RequestException as e:
                retries += 1
                print(f"\n ⚠️ Falha na requisição: {e}. Tentativa {retries} de {max_retries}...")
                time.sleep(5)

        print(f"\n ❌ Erro Crítico: A API não respondeu após {max_retries} tentativas.")
        return None

    def get_all_pages(self, url, limit=50):
        todos = []
        offset = 0
        tem_mais = True
        
        while tem_mais:
            params = {"limit": limit, "offset": offset}
            dados = self.get_data(url, params=params)
            
            if dados is None: 
                break

            reg_pagina = (
                dados.get('conteudo') or 
                dados.get('content') or 
                dados.get('registros') or []
            )
            
            for item in reg_pagina:
                #print(json.dumps(item, ensure_ascii=False))
                print(item)

            todos.extend(reg_pagina)
            
            flag_mais = dados.get('maisPaginas') or dados.get('hasNext')
            if flag_mais is not None:
                tem_mais = flag_mais
            else:
                tem_mais = len(reg_pagina) >= limit
                
            if not reg_pagina: 
                break
                
            offset += limit
            
        return todos