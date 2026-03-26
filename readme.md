
# Betha Cloud Extrator 🚀

Este projeto é um framework em Python desenvolvido para extrair dados das APIs Betha, com suporte nativo a Refresh Token (Silent Login) e 
Paginação Automática.

## 📋 Pré-requisitos
Python 3.10 ou superior.
Bibliotecas necessárias: requests, python-dotenv.
Arquivo .env configurado na raiz do projeto.

## ⚙️ Configuração do Ambiente
Crie um arquivo chamado .env e preencha com suas credenciais obtidas via inspecionar elemento (F12) no navegador:

### Variáveis de Ambiente (.env)
| Variável | Descrição | Exemplo |
| :--- | :--- | :--- |
| `CLIENT_ID` | ID da aplicação no Console Betha | `e9797...` |
| `TOKEN_TELA` | Access Token obtido no navegador | `Bearer ...` |
| `USER_ACCESS` | Contexto de acesso do usuário | `12345` |
| `REDIRECT_URI` | URL de retorno cadastrada | `https://...` |

>>> VERIFICAR O CLIENT_ID AQUI: 
https://plataforma-oauth.betha.cloud/auth/oauth2/tokeninfo?access_token={ADICIONE_TOKEN_TELA_AQUI}


## 🏗️ Estrutura do Projeto
| Componente | Descrição |
| :--- | :--- |
| **auth_handler.py** | Refresh Token automático e Silent Login |
| **api_service.py** | Timeout de 30s e paginação multi-sistema |
| **main.py** | Interface de execução com opção de Refresh forçado |

## 🚀 Como Usar
### 1. Cria o ambiente
python -m venv venv

### 2. Ativa (Exemplo PowerShell)
.\venv\Scripts\Activate.ps1

### 3. Atualiza o pip (Opcional mas recomendado)
python -m pip install --upgrade pip

### 4. Instala Bibliotecas
pip install -r requirements.txt

### 5. Extração Padrão
Para rodar uma extração, configure a URL desejada no arquivo main.py e execute: python main.py

### 6. Forçar Atualização de Token
Caso queira garantir que a extração comece com um token novo, altere a variável no main:
OPCAO_FORCAR_REFRESH = True

### 7. Endpoints Suportados
O sistema identifica automaticamente as chaves de retorno (conteudo, content ou registros), funcionando para Livro Eletrônico e Tributos.


## 🛠️ Solução de Problemas
| Funcionalidade | Descrição | Status |
| :--- | :--- | :--- |
| **Auth Handler** | Gerenciamento de Refresh Token | ✅ Funcional |
| **API Service** | Consumo de endpoints e paginação | ✅ Funcional |
| **Timeout** | Tempo de espera de 30 segundos | ⚙️ Configurado |


## 📈 Roadmap de Evolução

- [ ] **Integração SQL:** Criar conector para gravar dados em PostgreSQL.
- [ ] **Multi-Sistema:** Validar endpoints de dos demais sistemas Betha.
- [ ] **Normalização:** Script para converter JSONB em tabelas relacionais limpas.
- [ ] **Dockerização:** Criar um Dockerfile para rodar o extrator em containers.
