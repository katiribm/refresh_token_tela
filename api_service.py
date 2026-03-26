import requests
import time
import json

class BethaGetService:
    def __init__(self, auth_provider):
        self.auth = auth_provider

    def get_data(self, url, params=None):
        for tentativa in range(3):
            headers = self.auth.dict_header
            try:
                response = requests.get(url, headers=headers, params=params, timeout=30)
                
                if response.status_code == 401:
                    self.auth.getToken(force_refresh=True)
                    continue
                
                if response.status_code in (200, 201):
                    return response.json()
                
                return None
                
            except requests.exceptions.RequestException:
                time.sleep(2)
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