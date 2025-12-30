import requests
import json # Usado para formatar a saída e facilitar a leitura

# --- Documentação do Código ---

# 1. DEFINIÇÕES:
# Vamos usar o ID de um jogo que JÁ ACONTECEU para termos dados reais.
# Este ID é do jogo Flamengo vs Atlético-MG (Brasileirão 2024).
# Você pode trocar este ID pelo ID de qualquer jogo do Sofascore.
ID_JOGO = "11880996" 

# Estas são as URLs das APIs "escondidas" que o Sofascore usa.
URL_API_EVENTO = f"https://api.sofascore.com/api/v1/event/{ID_JOGO}"
URL_API_INCIDENTES = f"https://api.sofascore.com/api/v1/event/{ID_JOGO}/incidents"

# Precisamos simular ser um navegador para a API não nos bloquear.
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

print(f"--- Buscando dados da API do Sofascore para o Jogo ID: {ID_JOGO} ---")

try:
    # 2. CHAMADA DA API (ÁRBITRO):
    # Faz a requisição para a API de dados gerais do evento.
    response_evento = requests.get(URL_API_EVENTO, headers=headers)
    response_evento.raise_for_status() # Verifica se a requisição foi bem-sucedida
    
    # Converte a resposta (que é uma string JSON) para um dicionário Python.
    dados_evento = response_evento.json()
    
    # 3. EXTRAÇÃO DO ÁRBITRO:
    # Navegamos pelo dicionário Python para encontrar a informação.
    print("\n--- 1. ANÁLISE DO ÁRBITRO ---")
    try:
        # A estrutura é: dados_evento -> 'event' -> 'referee' -> 'name'
        arbitro_nome = dados_evento['event']['referee']['name']
        print(f"ÁRBITRO ENCONTRADO: {arbitro_nome}")
    except KeyError:
        print("Árbitro não encontrado (Jogo pode não ter ocorrido ou o dado não está disponível).")

    # 4. CHAMADA DA API (CARTÕES E VAR):
    # Faz a requisição para a API de incidentes do jogo.
    response_incidentes = requests.get(URL_API_INCIDENTES, headers=headers)
    response_incidentes.raise_for_status()
    
    dados_incidentes = response_incidentes.json()

    # 5. EXTRAÇÃO DOS INCIDENTES (CARTÕES E VAR):
    print("\n--- 2. ANÁLISE DE INCIDENTES ---")
    cartoes_amarelos = 0
    cartoes_vermelhos = 0
    revisoes_var = 0

    # 'incidents' é uma lista de eventos. Vamos iterar sobre ela.
    for incidente in dados_incidentes['incidents']:
        
        # Checando por Cartões
        if incidente['incidentType'] == 'card':
            if incidente.get('color') == 'yellow':
                cartoes_amarelos += 1
            elif incidente.get('color') == 'red':
                cartoes_vermelhos += 1

        # Checando por VAR (Isso é uma suposição de como eles marcam o VAR)
        # Muitas vezes o VAR é um 'incidentType' == 'var' ou uma chave 'varReview'
        if 'varReview' in incidente and incidente['varReview'] == True:
            revisoes_var += 1
        
        # (DEBUG) Descomente a linha abaixo para ver TODOS os incidentes
        # print(json.dumps(incidente, indent=2)) 

    print(f"Total de Cartões Amarelos no jogo: {cartoes_amarelos}")
    print(f"Total de Cartões Vermelhos no jogo: {cartoes_vermelhos}")
    print(f"Total de Revisões do VAR: {revisoes_var}")


except requests.exceptions.RequestException as e:
    print(f"\nERRO: Falha ao acessar a API do Sofascore.")
    print(f"Detalhe: {e}")