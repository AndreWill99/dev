# app.py
from flask import Flask, render_template
import pandas as pd
import requests
from io import StringIO
import time # Usaremos para evitar sobrecarregar a API

app = Flask(__name__)

# --- 1. LÓGICA DE EXTRAÇÃO DE DADOS (A Nova Parte!) ---

def buscar_dados_reais():
    """
    Função principal de "ETL". Busca dados de vários jogos na API
    do Sofascore e os transforma em um DataFrame limpo.
    """
    print("Iniciando busca de dados reais na API do Sofascore...")
    
    # LISTA DE IDs DE JOGOS (Exemplos do Brasileirão 2024)
    # Na vida real, teríamos que buscar essa lista dinamicamente.
    # Por enquanto, usamos IDs fixos de jogos que já ocorreram.
    lista_ids_jogos = [
        "11880996", # Flamengo x Atlético-MG
        "11880988", # Bahia x Fluminense
        "11880979", # Palmeiras x Vitória
        "11881005", # Botafogo x Grêmio
        "11880990", # Cruzeiro x Cuiabá
    ]
    
    dados_dos_jogos = [] # Lista para guardar os dados de cada jogo
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    for id_jogo in lista_ids_jogos:
        try:
            # URLs da API para este ID
            URL_API_EVENTO = f"https://api.sofascore.com/api/v1/event/{id_jogo}"
            URL_API_INCIDENTES = f"https://api.sofascore.com/api/v1/event/{id_jogo}/incidents"
            
            # Pequena pausa para não sermos bloqueados por "excesso de requisições"
            time.sleep(0.5) 
            
            # 1. Buscar dados gerais (Árbitro, Times)
            response_evento = requests.get(URL_API_EVENTO, headers=headers)
            response_evento.raise_for_status()
            dados_evento = response_evento.json()['event']
            
            # 2. Buscar incidentes (Cartões, VAR)
            response_incidentes = requests.get(URL_API_INCIDENTES, headers=headers)
            response_incidentes.raise_for_status()
            dados_incidentes = response_incidentes.json()['incidents']
            
            # --- Transformação (T) ---
            
            # Extração do Árbitro
            arbitro_nome = "Não disponível" # Valor padrão
            if 'referee' in dados_evento and dados_evento['referee'] is not None:
                arbitro_nome = dados_evento['referee']['name']

            # Extração dos Times
            time_casa = dados_evento['homeTeam']['name']
            time_visitante = dados_evento['awayTeam']['name']
            
            # Contagem de Incidentes
            cartoes_amarelos = 0
            cartoes_vermelhos = 0
            revisoes_var = 0
            
            for incidente in dados_incidentes:
                if incidente['incidentType'] == 'card':
                    if incidente.get('color') == 'yellow': cartoes_amarelos += 1
                    elif incidente.get('color') == 'red': cartoes_vermelhos += 1
                if 'varReview' in incidente and incidente['varReview'] == True:
                    revisoes_var += 1
            
            # Adiciona os dados limpos deste jogo à nossa lista
            dados_dos_jogos.append({
                "ID_Jogo": id_jogo,
                "Arbitro": arbitro_nome,
                "Time_Casa": time_casa,
                "Time_Visitante": time_visitante,
                "Cartoes_Amarelos": cartoes_amarelos,
                "Cartoes_Vermelhos": cartoes_vermelhos,
                "Uso_VAR": "Sim" if revisoes_var > 0 else "Nao",
                "Total_Cartoes": cartoes_amarelos + cartoes_vermelhos
            })
            
            print(f"Sucesso ao buscar Jogo ID: {id_jogo} ({time_casa} x {time_visitante})")

        except Exception as e:
            print(f"ERRO ao buscar Jogo ID: {id_jogo}. Detalhe: {e}")
            
    # --- Fim do Loop ---
    
    # 3. Converter a lista de dicionários em um DataFrame do Pandas
    if not dados_dos_jogos:
        # Se nenhum dado foi coletado, retorna um DataFrame vazio
        return pd.DataFrame(columns=["ID_Jogo", "Arbitro", "Time_Casa", "Time_Visitante", "Cartoes_Amarelos", "Cartoes_Vermelhos", "Uso_VAR", "Total_Cartoes"])

    df_jogos = pd.DataFrame(dados_dos_jogos)
    print("--- DataFrame de Dados Reais Criado com Sucesso ---")
    print(df_jogos.head())
    return df_jogos

# --- 2. LÓGICA DE ANÁLISE (Exatamente como na Etapa 3, mas agora recebe o df) ---

def processar_e_analisar_df(df_jogos):
    """
    Recebe o DataFrame (agora com dados reais) e calcula as estatísticas.
    Esta função é idêntica à lógica da Etapa 2/3.
    """
    
    if df_jogos.empty:
        # Retorna N/D se o DataFrame estiver vazio
        return {
            'analise_geral_html': "<p>Nenhum dado de jogo foi encontrado.</p>",
            'analise_var_html': "<p>Nenhum dado de jogo foi encontrado.</p>",
            'analise_vies_html': "<p>Nenhum dado de jogo foi encontrado.</p>",
            'time_alvo': "N/D"
        }

    # A) ANÁLISE GERAL
    analise_geral = df_jogos.groupby('Arbitro').agg(
        Total_Jogos=('ID_Jogo', 'count'),
        Media_Cartoes_Total=('Total_Cartoes', 'mean'),
    ).reset_index().sort_values(by='Media_Cartoes_Total', ascending=False)
    
    # B) ANÁLISE DE VAR
    uso_var = df_jogos[df_jogos['Uso_VAR'] == 'Sim'].groupby('Arbitro')['ID_Jogo'].count().reset_index(name='Vezes_Usou_VAR')
    analise_var = pd.merge(analise_geral[['Arbitro', 'Total_Jogos']], uso_var, on='Arbitro', how='left').fillna(0)
    analise_var['Frequencia_VAR'] = (analise_var['Vezes_Usou_VAR'] / analise_var['Total_Jogos']) * 100
    analise_var = analise_var[['Arbitro', 'Total_Jogos', 'Frequencia_VAR']].sort_values(by='Frequencia_VAR', ascending=False)

    # C) ANÁLISE DE VIÉS (Exemplo: Time Alvo é 'Flamengo')
    TIME_ALVO = 'Flamengo'
    df_time_alvo = df_jogos[(df_jogos['Time_Casa'] == TIME_ALVO) | (df_jogos['Time_Visitante'] == TIME_ALVO)]
    
    if not df_time_alvo.empty:
        analise_viés = df_time_alvo.groupby('Arbitro').agg(
            Jogos_Com_Time=('ID_Jogo', 'count'),
            Media_Cartoes_Com_Time=('Total_Cartoes', 'mean')
        ).reset_index().sort_values(by='Media_Cartoes_Com_Time', ascending=False)
    else:
        # Cria DataFrame vazio se o time alvo não foi encontrado nos dados
        analise_viés = pd.DataFrame(columns=['Arbitro', 'Jogos_Com_Time', 'Media_Cartoes_Com_Time'])


    # Convertendo DataFrames para HTML para enviar ao Template
    resultados = {
        'analise_geral_html': analise_geral.to_html(classes='table table-striped'),
        'analise_var_html': analise_var.to_html(classes='table table-striped', float_format='%.2f'),
        'analise_vies_html': analise_viés.to_html(classes='table table-striped'),
        'time_alvo': TIME_ALVO
    }
    return resultados

# --- 3. ROTA WEB (Servidor Flask) ---
@app.route('/')
def index():
    # 1. Chama a função que busca dados reais
    df_real = buscar_dados_reais()
    
    # 2. Chama a função que analisa esses dados
    dados_analisados = processar_e_analisar_df(df_real)
    
    # 3. Envia os resultados para o template 'index.html'
    return render_template('index.html', **dados_analisados)

# --- 4. EXECUÇÃO ---
if __name__ == '__main__':
    app.run(debug=True)