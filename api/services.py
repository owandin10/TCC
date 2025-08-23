import pandas as pd
import os
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

# --- 1. Configuração e Variáveis Globais ---
try:
    API_DIR = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT = os.path.dirname(API_DIR)
except NameError:
    PROJECT_ROOT = os.getcwd()

DATA_FILE_PATH = os.path.join(PROJECT_ROOT, "data", "data.csv")

df_usina_global = None
model_global = None
feature_columns_global = []

# --- 2. Funções Auxiliares da IA (Inalteradas) ---
def classificar_tensao_trifasica(row):
    tensao1, tensao2, tensao3 = row['Tensao_L1'], row['Tensao_L2'], row['Tensao_L3']
    if any(t > 233 for t in [tensao1, tensao2, tensao3]) or any(t < 191 for t in [tensao1, tensao2, tensao3]): return 'Crítica'
    elif any(t > 231 for t in [tensao1, tensao2, tensao3]) or any(t < 202 for t in [tensao1, tensao2, tensao3]): return 'Precária'
    elif all(t > 0 for t in [tensao1, tensao2, tensao3]): return 'Adequada'
    else: return 'Inativo'

def adicionar_sugestao_trifasica(row):
    previsao = row['Previsao_Classe_Tensao']
    if previsao in ['Adequada', 'Inativo']: return "Operação normal. Sem alerta."
    sugestoes = []
    for fase in ['L1', 'L2', 'L3']:
        tensao = row[f'Tensao_{fase}']
        if tensao > 233: sugestoes.append(f"Fase {fase} em sobretensão crítica ({tensao:.1f}V). Risco de danos.")
        elif tensao > 231: sugestoes.append(f"Fase {fase} em sobretensão precária ({tensao:.1f}V). Monitore a rede.")
        elif tensao < 191: sugestoes.append(f"Fase {fase} em subtensão crítica ({tensao:.1f}V). Risco de falha.")
        elif tensao < 202: sugestoes.append(f"Fase {fase} em subtensão precária ({tensao:.1f}V). Verifique conexões.")
    return "ALERTA: " + " | ".join(sugestoes) if sugestoes else "Anomalia detectada."

# --- 3. Funções Principais ---

def carregar_dados_e_treinar_modelo():
    global df_usina_global, model_global, feature_columns_global
    print("DEBUG SERVICES: --------------- INÍCIO DO CARREGAMENTO E TREINAMENTO DA IA ---------------")
    
    try:
        # MUDANÇA: Especifica exatamente quais colunas queremos ler.
        # Isto torna a leitura mais segura e ignora colunas extras ou mal formatadas.
        colunas_necessarias = [
            'DateTime', 'Dem_Ativa', 'Dem_Reat', 'Tensao_L1', 'Tensao_L2', 'Tensao_L3',
            'Corrente_L1', 'Corrente_L2', 'Corrente_L3', 'Fat_Pot', 'Fat_Carga'
        ]

        df = pd.read_csv(
            DATA_FILE_PATH,
            sep=',',
            decimal='.',
            parse_dates=['DateTime'],
            usecols=lambda column: column in colunas_necessarias, # Lê apenas as colunas que nos interessam
            on_bad_lines='warn' # Em vez de falhar, apenas avisa sobre linhas com problemas e continua
        )
        df = df.set_index('DateTime')

        # O resto da função continua igual...
        numeric_cols = ['Dem_Ativa', 'Corrente_L1', 'Corrente_L2', 'Corrente_L3', 'Tensao_L1', 'Tensao_L2', 'Tensao_L3']
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        df['Classe_Tensao'] = df.apply(classificar_tensao_trifasica, axis=1)
        df_treino = df[df['Classe_Tensao'] != 'Inativo'].copy()
        
        feature_columns_global = ['Dem_Ativa', 'Corrente_L1', 'Corrente_L2', 'Corrente_L3', 'Tensao_L1', 'Tensao_L2', 'Tensao_L3']
        target = 'Classe_Tensao'
        
        X = df_treino[feature_columns_global]
        y = df_treino[target]
        
        model_rf = RandomForestClassifier(n_estimators=100, random_state=42)
        model_rf.fit(X, y)
        
        model_global = model_rf
        df_usina_global = df.copy()
        
        print("DEBUG SERVICES: --------------- MODELO DE IA TREINADO E PRONTO ---------------")
    except FileNotFoundError:
        print(f"ERRO FATAL SERVICES: Ficheiro CSV NÃO ENCONTRADO em '{DATA_FILE_PATH}'")
    except Exception as e:
        import traceback
        print(f"ERRO FATAL SERVICES ao carregar/treinar: {e}")
        print(traceback.format_exc())

def obter_dados_para_api(data_solicitada_str=None):
    # (Esta função permanece inalterada)
    if df_usina_global is None or model_global is None:
        return {"erro": "Dados ou modelo de IA não carregados no servidor."}
    
    try:
        dia_para_analise = pd.to_datetime(data_solicitada_str).date() if data_solicitada_str else df_usina_global.index.date.max()
        df_dia = df_usina_global[df_usina_global.index.date == dia_para_analise].copy()
        
        dados_formatados = {
            "nome": "Usina IFG - Inversor 1", "localizacao": "IFG Goiânia",
            "geracao_total_dia_kwh": 0, "dados_pico_dia": {}, "leituras_dia_selecionado": [],
            "relatorio_ia": [], "erro_dia_selecionado": None
        }
        
        if df_dia.empty:
            dados_formatados["erro_dia_selecionado"] = f"Nenhum dado para {dia_para_analise.strftime('%Y-%m-%d')}"
        else:
            intervalo_h = 5 / 60
            dados_formatados["geracao_total_dia_kwh"] = round(df_dia['Dem_Ativa'].sum() * intervalo_h, 2)
            dados_formatados["leituras_dia_selecionado"] = df_dia.reset_index().to_dict('records')
            idx_pico = df_dia['Dem_Ativa'].idxmax()
            pico_raw = df_dia.loc[idx_pico]
            dados_formatados["dados_pico_dia"] = pico_raw.to_dict()
            dados_formatados["dados_pico_dia"]["timestamp_pico"] = idx_pico.isoformat() + "Z"
            X_dia = df_dia[feature_columns_global]
            df_dia['Previsao_Classe_Tensao'] = model_global.predict(X_dia)
            df_dia['Sugestao'] = df_dia.apply(adicionar_sugestao_trifasica, axis=1)
            df_risco = df_dia[~df_dia['Previsao_Classe_Tensao'].isin(['Adequada', 'Inativo'])].copy()
            df_risco['Horario'] = df_risco.index.strftime('%H:%M:%S')
            colunas_relatorio = ['Horario', 'Previsao_Classe_Tensao', 'Sugestao']
            dados_formatados["relatorio_ia"] = df_risco[colunas_relatorio].to_dict('records')

        return dados_formatados
    except Exception as e:
        return {"erro": f"Erro no servidor: {str(e)}"}

# --- Execução Inicial ---
carregar_dados_e_treinar_modelo()
