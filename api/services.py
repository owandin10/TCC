import pandas as pd
import os
from datetime import datetime
<<<<<<< HEAD
# MUDANÇA: NumPy não é mais necessário para este cálculo
# import numpy as np

# --- 1. Configuração de Caminhos e Variáveis Globais ---
try:
    API_DIR = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT = os.path.dirname(API_DIR)
except NameError:
    PROJECT_ROOT = os.getcwd()

DATA_FILE_PATH = os.path.join(PROJECT_ROOT, "data", "data.csv")

df_usina_global = None

# --- 2. Funções de Lógica de Negócio (ATUALIZADAS) ---

def carregar_e_processar_dados_usina():
    """
    Carrega e processa os dados da usina a partir do CSV.
=======

# --- 1. Configuração de Caminhos e Variáveis Globais (AJUSTADO PARA A ESTRUTURA) ---
# O código agora calcula o caminho corretamente a partir da localização deste ficheiro.
try:
    # O diretório deste ficheiro (services.py) é '.../TCC/api'
    API_DIR = os.path.dirname(os.path.abspath(__file__))
    # Subimos um nível para chegar à raiz do projeto '.../TCC'
    PROJECT_ROOT = os.path.dirname(API_DIR)
except NameError:
    # Fallback para ambientes onde __file__ não está definido
    PROJECT_ROOT = os.getcwd()

# Construímos o caminho para a pasta de dados a partir da raiz do projeto
DATA_FILE_PATH = os.path.join(PROJECT_ROOT, "data", "Inversor_1.csv")

# DataFrame global que armazenará os dados da usina após o carregamento
df_usina_global = None


# --- 2. Funções de Lógica de Negócio ---

def carregar_e_processar_dados_usina():
    """
    Carrega e processa os dados da usina de forma robusta e eficiente.
    Esta função é chamada uma vez quando o servidor inicia.
>>>>>>> 75bda8578b4454d271a0481bea29f97f8b8821c7
    """
    global df_usina_global
    print("DEBUG SERVICES: --------------- INÍCIO DO CARREGAMENTO DOS DADOS ---------------")
    
    if not os.path.exists(DATA_FILE_PATH):
        print(f"ERRO FATAL SERVICES: Ficheiro CSV NÃO ENCONTRADO em '{DATA_FILE_PATH}'")
        df_usina_global = None
        return

    try:
        df = pd.read_csv(
            DATA_FILE_PATH,
            encoding='utf-8',
            sep=',',
            decimal='.',
            parse_dates=['DateTime'],
            index_col='DateTime'
        )
        print("DEBUG SERVICES: CSV carregado com sucesso.")

<<<<<<< HEAD
        colunas_interesse = [
            'Dem_Ativa', 'Dem_Reat', 
            'Tensao_L1', 'Tensao_L2', 'Tensao_L3',
            'Corrente_L1', 'Corrente_L2', 'Corrente_L3',
            'Fat_Pot', 'Fat_Carga'
        ]

        df['Dia'] = df.index.date
        
        for col in colunas_interesse:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        df.fillna(0, inplace=True)
=======
        df['Dia'] = df.index.date
        df.rename(columns={'Dem_Ativa': 'energia_gerada_kw', 'Tensao': 'tensao_v'}, inplace=True)
        
        colunas_interesse = ['energia_gerada_kw', 'tensao_v']
        df.fillna({col: 0 for col in colunas_interesse}, inplace=True)
>>>>>>> 75bda8578b4454d271a0481bea29f97f8b8821c7

        df_usina_global = df.copy()
        print("DEBUG SERVICES: --------------- PROCESSAMENTO CONCLUÍDO ---------------")
    except Exception as e:
        import traceback
        print(f"ERRO FATAL SERVICES ao carregar/processar o CSV: {e}")
        print(traceback.format_exc())
        df_usina_global = None


def obter_dados_para_api(data_solicitada_str=None):
    """
<<<<<<< HEAD
    Prepara e retorna os dados para a API, com a geração total do dia (kWh)
    calculada pela soma das potências instantâneas.
    """
    if df_usina_global is None or df_usina_global.empty:
        return {"erro": "Falha crítica: Dados da usina não carregados no servidor."}
    
    try:
        dados_formatados = {
            "nome": "Usina IFG - Inversor 1 (Dados Trifásicos)",
            "localizacao": "IFG Goiânia - Subestação",
            "geracao_total_dia_kwh": 0,
            "dados_pico_dia": {},
=======
    Prepara e retorna os dados para a API a partir do DataFrame global.
    """
    if df_usina_global is None or df_usina_global.empty:
        return {"erro": "Falha crítica: Dados da usina não carregados no servidor. Verifique os logs."}
    
    try:
        dados_atuais_raw = df_usina_global.iloc[-1]
        
        dados_formatados = {
            "nome": "Usina IFG - Inversor 1 (Dados Reais Padronizados)",
            "localizacao": "IFG Goiânia - Subestação",
            "ultima_atualizacao_geral": dados_atuais_raw.name.isoformat() + "Z",
            "dados_atuais_geral": {
                "energia_gerada_kw": dados_atuais_raw.get('energia_gerada_kw', 'N/D'),
                "tensao_v": dados_atuais_raw.get('tensao_v', 'N/D'),
            },
>>>>>>> 75bda8578b4454d271a0481bea29f97f8b8821c7
            "leituras_dia_selecionado": [],
            "erro_dia_selecionado": None
        }
        
<<<<<<< HEAD
        dia_para_analise = None
        if data_solicitada_str:
            try:
                dia_para_analise = datetime.strptime(data_solicitada_str, '%Y-%m-%d').date()
            except (ValueError, TypeError):
                dados_formatados["erro_dia_selecionado"] = f"Formato de data inválido: {data_solicitada_str}."
                dia_para_analise = df_usina_global['Dia'].max()
        else:
            dia_para_analise = df_usina_global['Dia'].max()

        if pd.notna(dia_para_analise):
            df_dia_selecionado = df_usina_global[df_usina_global['Dia'] == dia_para_analise].sort_index()
            
            if df_dia_selecionado.empty:
                msg_erro_dia = f"Nenhum dado encontrado para {dia_para_analise.strftime('%Y-%m-%d')}"
                dados_formatados["erro_dia_selecionado"] = msg_erro_dia
            else:
                # --- CÁLCULO CORRIGIDO CONFORME SUA LÓGICA ---
                # Energia (kWh) = Soma das potências (kW) * intervalo de tempo (h)
                # O intervalo é de 5 minutos, que equivale a 5/60 de uma hora.
                intervalo_em_horas = 5 / 60
                soma_das_potencias = df_dia_selecionado['Dem_Ativa'].sum()
                geracao_total_kwh = soma_das_potencias * intervalo_em_horas
                dados_formatados["geracao_total_dia_kwh"] = round(geracao_total_kwh, 2)

                # --- Lógica do Pico do Dia (Inalterada) ---
                idx_pico = df_dia_selecionado['Dem_Ativa'].idxmax()
                dados_pico_raw = df_dia_selecionado.loc[idx_pico]
                
                dados_formatados["dados_pico_dia"] = {
                    "timestamp_pico": idx_pico.isoformat() + "Z",
                    "Dem_Ativa": dados_pico_raw.get('Dem_Ativa', 'N/D'),
                    "Dem_Reat": dados_pico_raw.get('Dem_Reat', 'N/D'),
                    "Tensao_L1": dados_pico_raw.get('Tensao_L1', 'N/D'),
                    "Tensao_L2": dados_pico_raw.get('Tensao_L2', 'N/D'),
                    "Tensao_L3": dados_pico_raw.get('Tensao_L3', 'N/D'),
                    "Corrente_L1": dados_pico_raw.get('Corrente_L1', 'N/D'),
                    "Corrente_L2": dados_pico_raw.get('Corrente_L2', 'N/D'),
                    "Corrente_L3": dados_pico_raw.get('Corrente_L3', 'N/D'),
                    "Fat_Pot": dados_pico_raw.get('Fat_Pot', 'N/D'),
                    "Fat_Carga": dados_pico_raw.get('Fat_Carga', 'N/D')
                }
                
                df_dia_selecionado_reset = df_dia_selecionado.reset_index()
                leituras_dia = df_dia_selecionado_reset.to_dict('records')
=======
        dia_para_grafico = None
        if data_solicitada_str:
            try:
                dia_para_grafico = datetime.strptime(data_solicitada_str, '%Y-%m-%d').date()
            except (ValueError, TypeError):
                dados_formatados["erro_dia_selecionado"] = f"Formato de data inválido recebido: {data_solicitada_str}."
                dia_para_grafico = df_usina_global['Dia'].max()
        else:
            dia_para_grafico = df_usina_global['Dia'].max()

        if pd.notna(dia_para_grafico):
            df_dia_selecionado = df_usina_global[df_usina_global['Dia'] == dia_para_grafico]
            if df_dia_selecionado.empty:
                msg_erro_dia = f"Nenhum dado encontrado para {dia_para_grafico.strftime('%Y-%m-%d')}"
                dados_formatados["erro_dia_selecionado"] = msg_erro_dia
            else:
                leituras_dia = []
                for timestamp, row in df_dia_selecionado.iterrows():
                    leituras_dia.append({
                        "timestamp": timestamp.isoformat() + "Z",
                        "hora_minuto": timestamp.strftime('%H:%M'),
                        "energia_gerada_kw": row.get('energia_gerada_kw', 0),
                        "tensao_v": row.get('tensao_v', 0)
                    })
>>>>>>> 75bda8578b4454d271a0481bea29f97f8b8821c7
                dados_formatados["leituras_dia_selecionado"] = leituras_dia
        
        return dados_formatados
        
    except Exception as e:
        import traceback
        print(f"ERRO FATAL SERVICES [obter_dados_para_api]: {e}")
        print(traceback.format_exc())
        return {"erro": f"Erro crítico no servidor ao processar dados: {str(e)}"}


# --- 3. Execução Inicial ---
<<<<<<< HEAD
carregar_e_processar_dados_usina()
=======
# Carrega os dados na memória uma vez quando este módulo é importado pela primeira vez
carregar_e_processar_dados_usina()
>>>>>>> 75bda8578b4454d271a0481bea29f97f8b8821c7
