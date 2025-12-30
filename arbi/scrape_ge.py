import requests
from bs4 import BeautifulSoup

# --- Documentação do Código ---
# 1. Definimos a URL do jogo que queremos analisar.
#    Esta é a parte mais "frágil": se a estrutura da URL do GE mudar, isso quebra.
#    Estamos usando um jogo que já aconteceu (ex: Brasileirão 2025, 01/11).
URL_ALVO = "https://ge.globo.com/rs/futebol/brasileirao-serie-a/jogo/02-11-2025/internacional-atletico-mg.ghtml"

# 2. Definimos um "User-Agent".
#    Muitos sites (incluindo o GE) bloqueiam requisições que parecem ser de robôs.
#    Este 'header' faz nosso script se passar por um navegador Chrome comum.
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def analisar_pagina_jogo(url):
    print(f"--- Iniciando Scraping Estático em: {url} ---\n")
    
    try:
        # 3. Faz a requisição HTTP (como um navegador)
        response = requests.get(url, headers=headers)
        response.raise_for_status() # Lança um erro se a página não for encontrada (ex: 404)
        
        # 4. Cria o objeto 'soup'
        #    'soup' é o HTML da página "traduzido" para um objeto Python que podemos
        #    consultar (usando o 'lxml' como motor de análise).
        soup = BeautifulSoup(response.text, 'lxml')
        
        # ----------------------------------------------------------------------
        # TENTATIVA 1: Encontrar o Árbitro (Dado Provavelmente Estático)
        # ----------------------------------------------------------------------
        
        # NOTA DE IMPLEMENTAÇÃO:
        # Para encontrar a 'class' correta, eu teria que:
        # 1. Abrir o GE no Chrome.
        # 2. Clicar com o botão direito no nome do árbitro.
        # 3. Clicar em "Inspecionar Elemento".
        # 4. Ver o nome da classe. (Ex: 'ficha-tecnica__arbitragem-item')
        
        # Vamos usar uma classe hipotética, mas muito comum em "fichas técnicas"
        arbitro_tag = soup.find('div', class_='ficha-tecnica__arbitragem-nome') # Nome da classe é um exemplo
        
        print("--- Resultado da Busca por ÁRBITRO ---")
        if arbitro_tag:
            arbitro_nome = arbitro_tag.text.strip()
            print(f"SUCESSO! Árbitro encontrado: {arbitro_nome}\n")
        else:
            # Se não achou com a classe, tentamos um método mais genérico
            # (Ex: procurar a palavra "Árbitro:" na página)
            print("FALHA: Não foi possível encontrar a tag do árbitro no HTML estático.\n")


        # ----------------------------------------------------------------------
        # TENTATIVA 2: Encontrar os Cartões (Dado Provavelmente Dinâmico)
        # ----------------------------------------------------------------------
        
        # NOTA DE IMPLEMENTAÇÃO:
        # Cartões geralmente estão em uma "timeline" ou "feed de eventos".
        # Vamos procurar por itens que pareçam ser eventos de cartão.
        # (Ex: class='feed-eventos__item--cartao')
        
        cartoes_tags = soup.find_all('div', class_='feed-eventos__item--cartao') # Nome da classe é um exemplo
        
        print("--- Resultado da Busca por CARTÕES ---")
        if len(cartoes_tags) > 0:
            print(f"SUCESSO! Encontrados {len(cartoes_tags)} eventos de cartão.")
            for cartao in cartoes_tags:
                print(f" - Evento: {cartao.text.strip()}")
        else:
            print("FALHA: Nenhum evento de cartão foi encontrado no HTML estático.\n")
            
    
    except requests.exceptions.RequestException as e:
        print(f"ERRO: Falha ao acessar a URL. O site pode estar fora do ar ou bloqueando o acesso.")
        print(f"Detalhe: {e}")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")


# Executa a função
analisar_pagina_jogo(URL_ALVO)