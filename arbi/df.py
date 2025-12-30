import pandas as pd
import numpy as np
from io import StringIO

# --- Documentação do Código ---
# 1. Importa as bibliotecas necessárias: pandas para DataFrames e numpy para operações numéricas.
# 2. A string 'dados_simulados' armazena os dados em formato CSV (valores separados por vírgula).
#    Cada linha representa um jogo.
#    Colunas importantes:
#    - ID_Jogo: Identificador único do jogo.
#    - Arbitro: Nome do árbitro a ser monitorado.
#    - Time_Casa / Time_Visitante: Times envolvidos.
#    - Cartoes_Amarelos / Cartoes_Vermelhos: Total de cartões dados pelo árbitro no jogo.
#    - Uso_VAR: Indica se o árbitro consultou o VAR (Sim/Não).
#    - Resultado_Reclamado: Se houve reclamação controversa após o jogo (Sim/Não).

dados_simulados = """
ID_Jogo,Arbitro,Time_Casa,Time_Visitante,Cartoes_Amarelos,Cartoes_Vermelhos,Uso_VAR,Resultado_Reclamado
1001,Sandro Ricci,Flamengo,Vasco,6,1,Sim,Sim
1002,Wilton Pereira Sampaio,Palmeiras,Corinthians,3,0,Nao,Nao
1003,Sandro Ricci,Sao Paulo,Santos,7,0,Nao,Sim
1004,Anderson Daronco,Gremio,Internacional,2,0,Nao,Nao
1005,Wilton Pereira Sampaio,Atletico-MG,Cruzeiro,5,1,Sim,Nao
1006,Sandro Ricci,Vasco,Botafogo,4,0,Sim,Nao
1007,Anderson Daronco,Fluminense,Bahia,6,1,Sim,Sim
1008,Wilton Pereira Sampaio,Coritiba,Goias,1,0,Nao,Nao
1009,Anderson Daronco,Cuiaba,Fortaleza,8,0,Sim,Sim
1010,Sandro Ricci,Atletico-PR,America-MG,3,0,Nao,Nao
"""

def get_df_jogos():
    # Cria o DataFrame a partir da string CSV
    df_jogos = pd.read_csv(StringIO(dados_simulados))

    # Garante que as colunas de cartões são números inteiros
    df_jogos['Cartoes_Amarelos'] = df_jogos['Cartoes_Amarelos'].astype(int)
    df_jogos['Cartoes_Vermelhos'] = df_jogos['Cartoes_Vermelhos'].astype(int)

    # Cria uma coluna para o total de cartões
    df_jogos['Total_Cartoes'] = df_jogos['Cartoes_Amarelos'] + df_jogos['Cartoes_Vermelhos']

    return df_jogos

# Remova ou comente a exibição do DataFrame, se necessário
# print("--- DataFrame de Dados Simulados ---")
# print(df_jogos.head())
# print("-" * 40)