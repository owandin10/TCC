# ======================================================================

# Módulo de Backend
# ------------------------------------------------------------------------------
======================================================================

import pandas as pd
import os
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier
import traceback

# --- 1. Configuração e Inicialização do Ambiente ---
# ---------------------------------------------------
# Define o caminho do arquivo de dados e as variáveis globais que
# serão usadas para armazenar o DataFrame e o modelo de IA.
# A utilização de variáveis globais permite que o modelo e os dados
# sejam carregados apenas uma vez, evitando o reprocessamento em
# cada nova requisição da API.

try:
    # Tenta obter o caminho absoluto do diretório da API para garantir
    # que o código funcione em diferentes ambientes de execução.
    API_DIR = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT = os.path.dirname(API_DIR)
except NameError:
    # Um fallback seguro para ambientes onde a variável __file__ não está
    # disponível, como em notebooks interativos.
    PROJECT_ROOT = os.getcwd()

# Define o caminho completo para o arquivo de dados CSV.
DATA_FILE_PATH = os.path.join(PROJECT_ROOT, "data", "data.csv")

# Declaração das variáveis globais que serão preenchidas na inicialização.
df_usina_global = None
model_global = None
feature_columns_global = []

# --- 2. Núcleo de Inteligência e Análise ---
# ------------------------------------------
# Funções responsáveis pela lógica de classificação e geração de sugestões,
# que constituem a "inteligência" do sistema.

def classificar_tensao_trifasica(row):
    """
    Classifica a tensão trifásica de uma medição em uma de quatro categorias
    com base em limites predefinidos da ANEEL (Agência Nacional de Energia Elétrica).
    
    - 'Crítica': Tensão fora do limite regulamentar.
    - 'Precária': Tensão fora da faixa de tensão adequada, mas ainda dentro da tolerância.
    - 'Adequada': Tensão dentro da faixa ideal de operação.
    - 'Inativo': Tensões zeradas, indicando que o sistema pode estar desligado.
    """
    tensao1, tensao2, tensao3 = row['Tensao_L1'], row['Tensao_L2'], row['Tensao_L3']
    if any(t > 233 for t in [tensao1, tensao2, tensao3]) or any(t < 191 for t in [tensao1, tensao2, tensao3]):
        return 'Crítica'
    elif any(t > 231 for t in [tensao1, tensao2, tensao3]) or any(t < 202 for t in [tensao1, tensao2, tensao3]):
        return 'Precária'
    elif all(t > 0 for t in [tensao1, tensao2, tensao3]):
        return 'Adequada'
    else:
        return 'Inativo'

def adicionar_sugestao_detalhada(row):
    """
    Gera sugestões de diagnóstico e ações específicas para cada tipo de
    anomalia de tensão. As sugestões são adaptadas com base na fase afetada
    e na gravidade do problema.
    
    As sugestões são armazenadas em um 'set' para garantir a unicidade,
    evitando repetições no relatório final.
    """
    classificacao = row['Previsao_Classe_Tensao']
    if classificacao == 'Adequada' or classificacao == 'Inativo':
        return "Operação dentro dos parâmetros normais. Nenhuma ação é necessária."

    detalhes_fases = []
    sugestoes = set() # Usar um set para evitar sugestões duplicadas

    for fase in ['L1', 'L2', 'L3']:
        tensao = row.get(f'Tensao_{fase}', 0)
        # Análise de Sobretensão (tensão alta)
        if tensao > 233:
            detalhes_fases.append(f"Fase {fase} com sobretensão CRÍTICA ({tensao:.1f}V).")
            sugestoes.add("Causa Provável: Flutuações na rede da concessionária ou falha no tap do transformador.")
            sugestoes.add("Ação Recomendada: Contatar a concessionária imediatamente. Inspecionar o transformador.")
        elif tensao > 231:
            detalhes_fases.append(f"Fase {fase} com sobretensão PRECÁRIA ({tensao:.1f}V).")
            sugestoes.add("Causa Provável: Variações momentâneas na rede elétrica.")
            sugestoes.add("Ação Recomendada: Monitorar a estabilidade da tensão nas próximas horas.")
        # Análise de Subtensão (tensão baixa)
        elif tensao < 191:
            detalhes_fases.append(f"Fase {fase} com subtensão CRÍTICA ({tensao:.1f}V).")
            sugestoes.add("Causa Provável: Sobrecarga no circuito, fiação subdimensionada ou falha grave no inversor.")
            sugestoes.add("Ação Recomendada: Desligar cargas não essenciais. Inspecionar disjuntores e fiação. Verificar logs de erro do inversor.")
        elif tensao < 202:
            detalhes_fases.append(f"Fase {fase} com subtensão PRECÁRIA ({tensao:.1f}V).")
            sugestoes.add("Causa Provável: Conexões frouxas, oxidadas ou queda de tensão nos cabos.")
            sugestoes.add("Ação Recomendada: Realizar inspeção visual e reaperto das conexões elétricas.")
    
    # Constrói a mensagem final concatenando os detalhes e as sugestões únicas.
    mensagem_final = "\n".join(detalhes_fases)
    if sugestoes:
        sugestoes_unicas = sorted(list(sugestoes))
        mensagem_final += "\n\n" + "\n".join(sugestoes_unicas)

    return mensagem_final if mensagem_final else "Anomalia detectada. Realizar inspeção geral no sistema."

# --- 3. Funções Principais da API ---
# ------------------------------------
# Funções que orquestram o fluxo de dados, do carregamento à geração
# do relatório final.

def carregar_dados_e_treinar_modelo():
    """
    Função de inicialização do serviço.
    Carrega o arquivo CSV, pré-processa os dados, cria a variável alvo 'Classe_Tensao'
    e treina o modelo de IA (Random Forest Classifier).
    Os dados e o modelo treinados são armazenados em variáveis globais para
    acesso eficiente por outras funções.
    """
    global df_usina_global, model_global, feature_columns_global
    print("DEBUG SERVICES: --------------- INÍCIO DO CARREGAMENTO E TREINAMENTO DA IA ---------------")
    
    try:
        # Lê o arquivo CSV com configurações de separador e tratamento de datas.
        df = pd.read_csv(DATA_FILE_PATH, sep=',', decimal='.', parse_dates=['DateTime'])
        df = df.set_index('DateTime')

        # Converte colunas numéricas e preenche valores ausentes (NaN) com 0.
        numeric_cols = ['Dem_Ativa', 'Corrente_L1', 'Corrente_L2', 'Corrente_L3', 'Tensao_L1', 'Tensao_L2', 'Tensao_L3']
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        # Aplica a função de classificação para criar a variável 'Classe_Tensao'.
        df['Classe_Tensao'] = df.apply(classificar_tensao_trifasica, axis=1)
        df_treino = df[df['Classe_Tensao'] != 'Inativo'].copy()
        
        # Define as colunas de entrada (features) e a coluna alvo para o modelo.
        feature_columns_global = ['Dem_Ativa', 'Corrente_L1', 'Corrente_L2', 'Corrente_L3', 'Tensao_L1', 'Tensao_L2', 'Tensao_L3']
        target = 'Classe_Tensao'
        
        X = df_treino[feature_columns_global]
        y = df_treino[target]
        
        # Inicializa e treina o modelo de classificação.
        model_rf = RandomForestClassifier(n_estimators=100, random_state=42)
        model_rf.fit(X, y)
        
        # Atribui o modelo e o DataFrame às variáveis globais.
        model_global = model_rf
        df_usina_global = df.copy()
        
        print("DEBUG SERVICES: --------------- MODELO DE IA TREINADO E PRONTO ---------------")
    except Exception as e:
        print(f"ERRO FATAL SERVICES ao carregar/treinar: {e}")
        print(traceback.format_exc())

def obter_dados_para_api(data_solicitada_str=None):
    """
    Função principal da API. Recebe uma data (opcionalmente) e processa os dados
    desse dia para gerar um relatório completo, que inclui:
    - Dados de todas as medições do dia.
    - Informações sobre o pico de geração.
    - Um relatório de IA com alertas de tensão e sugestões detalhadas.
    """
    # Verifica se os dados e o modelo globais foram carregados com sucesso.
    if df_usina_global is None or model_global is None:
        return {"erro": "Dados ou modelo de IA não carregados no servidor."}
    
    try:
        # Determina o dia a ser analisado. Se nenhuma data for fornecida,
        # usa a data mais recente disponível nos dados.
        dia_para_analise = pd.to_datetime(data_solicitada_str).date() if data_solicitada_str else df_usina_global.index.date.max()
        df_dia = df_usina_global[df_usina_global.index.date == dia_para_analise].copy()
        
        # Estrutura o dicionário de resposta com valores padrão.
        dados_formatados = {
            "leituras_dia_selecionado": df_dia.reset_index().to_dict('records'),
            "relatorio_ia": [], 
            "erro_dia_selecionado": None, 
            "dados_pico_dia": {},
        }
        
        if df_dia.empty:
            # Retorna uma mensagem de erro se não houver dados para o dia solicitado.
            dados_formatados["erro_dia_selecionado"] = f"Nenhum dado para {dia_para_analise.strftime('%Y-%m-%d')}"
            return dados_formatados
        
        # Identifica e armazena os dados do pico de geração do dia.
        pico = df_dia.loc[df_dia['Dem_Ativa'].idxmax()]
        dados_formatados["dados_pico_dia"] = pico.to_dict()
        dados_formatados["dados_pico_dia"]["timestamp_pico"] = pico.name.isoformat()
        
        # --- Execução do Modelo de IA e Geração de Relatório ---
        # Filtra os dados apenas para o horário de operação diurna (6h às 19h).
        df_operacao = df_dia[(df_dia.index.hour >= 6) & (df_dia.index.hour < 19)].copy()
        
        if not df_operacao.empty:
            # Usa o modelo de IA para prever a classe de tensão para cada medição.
            X_pred = df_operacao[feature_columns_global]
            df_operacao['Previsao_Classe_Tensao'] = model_global.predict(X_pred)
            
            # Aplica a função de sugestão para gerar o relatório detalhado.
            df_operacao['Sugestao'] = df_operacao.apply(adicionar_sugestao_detalhada, axis=1)
            
            # Filtra apenas os registros que requerem atenção (Crítica ou Precária).
            df_risco = df_operacao[df_operacao['Previsao_Classe_Tensao'].isin(['Crítica', 'Precária'])].copy()
            
            if not df_risco.empty:
                # Formata o horário para o relatório final.
                df_risco['Horario'] = df_risco.index.strftime('%H:%M:%S')
                dados_formatados["relatorio_ia"] = df_risco.reset_index().to_dict('records')

        # Adiciona cálculo de geração total do dia (kWh).
        # A Dem_Ativa é uma leitura a cada 5 minutos, então multiplicamos por 5/60.
        intervalo_h = 5 / 60
        geracao_total = df_dia['Dem_Ativa'].sum() * intervalo_h
        dados_formatados["geracao_total_dia_kwh"] = round(geracao_total, 2)

        return dados_formatados

    except Exception as e:
        print(f"ERRO SERVICES na API: {e}")
        print(traceback.format_exc())
        return {"erro": f"Erro interno no servidor ao processar dados: {e}"}