# --- CONTINUAÇÃO DO CÓDIGO DA ETAPA 1 ---
import pandas as pd
from df import get_df_jogos

# ----------------------------------------------------------------------
# 2. ANÁLISE DE PADRÕES GERAIS POR ÁRBITRO
# ----------------------------------------------------------------------

print("\n" + "=" * 50)
print("  2. Análise de Padrões por Árbitro (Métricas Gerais)")
print("=" * 50)

# Obtém o DataFrame de jogos
df_jogos = get_df_jogos()

# A) Média de Cartões por Árbitro
# Usamos groupby('Arbitro') para agrupar e .agg() para aplicar funções (média e contagem)
analise_geral = df_jogos.groupby('Arbitro').agg(
    Total_Jogos=('ID_Jogo', 'count'), # Conta quantos jogos cada árbitro apitou
    Media_Cartoes_Total=('Total_Cartoes', 'mean'), # Média de cartões por jogo
    Media_Amarelos=('Cartoes_Amarelos', 'mean'),
    Media_Vermelhos=('Cartoes_Vermelhos', 'mean')
).reset_index() # Transforma o 'Arbitro' de índice para coluna

print("\n--- A) Média de Cartões e Jogos Apitados por Árbitro ---")
print(analise_geral.sort_values(by='Media_Cartoes_Total', ascending=False))
# Documentação: Este DataFrame mostra a média de cartões total e por cor. 
# O árbitro com a maior média é considerado mais rigoroso.

# B) Frequência de Uso do VAR
# Filtramos apenas os jogos onde 'Uso_VAR' foi 'Sim' e contamos por árbitro
uso_var = df_jogos[df_jogos['Uso_VAR'] == 'Sim'].groupby('Arbitro')['ID_Jogo'].count().reset_index(name='Vezes_Usou_VAR')

# Merge com a análise geral para ter o total de jogos e calcular a frequência
analise_var = pd.merge(analise_geral[['Arbitro', 'Total_Jogos']], uso_var, on='Arbitro', how='left').fillna(0)
analise_var['Frequencia_VAR'] = (analise_var['Vezes_Usou_VAR'] / analise_var['Total_Jogos']) * 100

print("\n--- B) Frequência de Uso do VAR (em %) ---")
print(analise_var[['Arbitro', 'Frequencia_VAR']].sort_values(by='Frequencia_VAR', ascending=False))
# Documentação: Este cálculo mostra a porcentagem de jogos em que o árbitro 
# consultou o VAR. Árbitros com maior frequência podem ser mais cautelosos.

# ----------------------------------------------------------------------
# 3. ANÁLISE DE VIÉS POR TIME (Média de Cartões quando apita o "Flamengo" - Exemplo)
# ----------------------------------------------------------------------

print("\n" + "=" * 50)
print("  3. Análise de Viés (Média de Cartões em Jogos do Flamengo)")
print("=" * 50)

TIME_ALVO = 'Flamengo'

# Filtra apenas os jogos em que o Time_Alvo jogou (casa ou visitante)
df_time_alvo = df_jogos[
    (df_jogos['Time_Casa'] == TIME_ALVO) | (df_jogos['Time_Visitante'] == TIME_ALVO)
]

# Agrupa esses jogos filtrados por árbitro e calcula a nova média de cartões
analise_viés = df_time_alvo.groupby('Arbitro').agg(
    Jogos_Com_Time=('ID_Jogo', 'count'),
    Media_Cartoes_Com_Time=('Total_Cartoes', 'mean')
).reset_index()

print(f"\n--- Média de Cartões quando apita jogos do time '{TIME_ALVO}' ---")
print(analise_viés.sort_values(by='Media_Cartoes_Com_Time', ascending=False))
# Documentação: Compara a média de cartões de cada árbitro APENAS quando o time alvo joga. 
# Podemos comparar este valor com a Média_Cartoes_Total (Seção 2A) para verificar se há uma diferença significativa.

# NOTA: O viés real requer a contagem de cartões DADOS AO TIME, não o total no jogo.
# A implementação mais complexa envolveria analisar uma coluna de "Eventos" que detalha o cartão e o jogador/time.