# Importação das bibliotecas necessárias para a análise de dados e machine learning.
# pandas: Usado para manipulação e análise de dados em formato de tabela (DataFrame).
import pandas as pd
# Módulos do scikit-learn para divisão de dados, treinamento do modelo e avaliação.
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
# Módulos para visualização de dados.
# matplotlib.pyplot: Para a criação de gráficos (como a matriz de confusão).
import matplotlib.pyplot as plt
# seaborn: Baseado no matplotlib, cria gráficos estatísticos mais bonitos e informativos.
import seaborn as sns
# Biblioteca padrão do Python para lidar com avisos.
import warnings

# Ignora todos os avisos (warnings) para manter a saída do console limpa,
# o que é útil para demonstrações ou scripts de uso único.
warnings.filterwarnings('ignore')

# --- Funções de Análise e Sugestão da IA (Replica do Backend para testes offline) ---

def classificar_tensao_trifasica(row):
    """
    Classifica a tensão em Crítica, Precária, Adequada ou Inativo com base nas
    normas da ANEEL (PRODIST Módulo 8, Tabela 2). Esta função simula a lógica
    de negócio de um sistema de backend.

    Parâmetros:
    - row (pandas.Series): Uma linha do DataFrame, contendo dados de tensão para L1, L2 e L3.

    Retorna:
    - str: A classificação da tensão ('Crítica', 'Precária', 'Adequada' ou 'Inativo').
    """
    tensao1, tensao2, tensao3 = row['Tensao_L1'], row['Tensao_L2'], row['Tensao_L3']
    
    # Se todas as tensões estão próximas de zero, considera-se que o sistema está inativo.
    if all(t < 5 for t in [tensao1, tensao2, tensao3]):
        return 'Inativo'

    # Classificação Crítica: sobretensão (acima de 233V) ou subtensão (abaixo de 191V).
    if any(t > 233 for t in [tensao1, tensao2, tensao3]) or any(t < 191 for t in [tensao1, tensao2, tensao3]):
        return 'Crítica'
    
    # Classificação Precária: sobretensão (entre 231V e 233V) ou subtensão (entre 191V e 202V).
    elif any(t > 231 for t in [tensao1, tensao2, tensao3]) or any(t < 202 for t in [tensao1, tensao2, tensao3]):
        return 'Precária'
        
    # Se não se enquadra nas categorias Crítica ou Precária, a tensão é considerada Adequada.
    else:
        return 'Adequada'

def adicionar_sugestao_detalhada(row):
    """
    Gera sugestões de ação detalhadas e específicas para cada tipo de alerta de tensão
    (Crítica e Precária) em cada fase.

    Parâmetros:
    - row (pandas.Series): Uma linha do DataFrame com a previsão da classe de tensão.

    Retorna:
    - str: Uma mensagem de sugestão detalhada para o usuário.
    """
    classificacao = row['Previsao_Classe_Tensao']
    if classificacao == 'Adequada' or classificacao == 'Inativo':
        return "Operação dentro dos parâmetros normais. Nenhuma ação é necessária."
    
    detalhes_fases, sugestoes = [], set()
    for fase in ['L1', 'L2', 'L3']:
        tensao = row.get(f'Tensao_{fase}', 0)
        
        # Sobretensão e subtensão crítica
        if tensao > 233:
            detalhes_fases.append(f"Fase {fase} com sobretensão CRÍTICA ({tensao:.1f}V).")
            sugestoes.add("Ação Recomendada: Contatar a concessionária imediatamente. Inspecionar o transformador.")
        elif tensao < 191 and tensao > 5: # Ignora o estado inativo
            detalhes_fases.append(f"Fase {fase} com subtensão CRÍTICA ({tensao:.1f}V).")
            sugestoes.add("Ação Recomendada: Desligar cargas não essenciais. Inspecionar disjuntores e fiação.")
        
        # Sobretensão e subtensão precária
        elif tensao > 231:
            detalhes_fases.append(f"Fase {fase} com sobretensão PRECÁRIA ({tensao:.1f}V).")
            sugestoes.add("Ação Recomendada: Monitorar a estabilidade da tensão nas próximas horas.")
        elif tensao < 202 and tensao > 5: # Ignora o estado inativo
            detalhes_fases.append(f"Fase {fase} com subtensão PRECÁRIA ({tensao:.1f}V).")
            sugestoes.add("Ação Recomendada: Realizar inspeção e reaperto das conexões elétricas.")
            
    mensagem_final = "\n".join(detalhes_fases)
    if sugestoes:
        mensagem_final += "\n\n" + "\n".join(sorted(list(sugestoes)))
    return mensagem_final if mensagem_final else "Anomalia detectada. Realizar inspeção geral."

# --- Funções para o Fluxo de Análise Offline ---

def carregar_e_preparar_dados(file_path):
    """
    Carrega os dados de um arquivo CSV, limpa-os e prepara o DataFrame para análise.

    Parâmetros:
    - file_path (str): O caminho do arquivo CSV.

    Retorna:
    - pandas.DataFrame: O DataFrame carregado e limpo, ou None em caso de erro.
    """
    try:
        # Lê o arquivo CSV com configurações específicas para separador, decimal e data.
        df = pd.read_csv(file_path, sep=',', decimal='.', parse_dates=['DateTime'])
        df = df.set_index('DateTime')
        
        # Converte colunas numéricas para o tipo correto e trata valores ausentes.
        numeric_cols = ['Dem_Ativa', 'Corrente_L1', 'Corrente_L2', 'Corrente_L3', 'Tensao_L1', 'Tensao_L2', 'Tensao_L3']
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
        print(f"Dados carregados com sucesso de '{file_path}'.")
        return df
    except FileNotFoundError:
        print(f"Erro: Arquivo não encontrado em '{file_path}'")
        return None
    except Exception as e:
        print(f"Erro ao carregar ou preparar os dados: {e}")
        return None

def treinar_modelo_ia(df):
    """
    Prepara os dados, treina um modelo de classificação de Random Forest e retorna
    o modelo treinado e os dados de teste.

    Parâmetros:
    - df (pandas.DataFrame): O DataFrame com os dados de energia.

    Retorna:
    - tuple: O modelo treinado, o conjunto de dados de teste (X_test) e os rótulos de teste (y_test).
             Retorna None para todos em caso de falha.
    """
    if df is None: return None, None, None
    
    # Adiciona a coluna de classes de tensão ao DataFrame.
    df['Classe_Tensao'] = df.apply(classificar_tensao_trifasica, axis=1)
    
    # Cria um subconjunto de dados para treinamento, removendo a classe 'Inativo'
    # para evitar vieses no modelo.
    df_treino = df[df['Classe_Tensao'] != 'Inativo'].copy()
    
    if len(df_treino['Classe_Tensao'].unique()) < 2:
        print("Erro: Classes insuficientes para treinamento do modelo. São necessárias no mínimo 2 classes.")
        return None, None, None

    # Define as 'features' (variáveis de entrada) e o 'target' (variável a ser prevista).
    features = ['Dem_Ativa', 'Corrente_L1', 'Corrente_L2', 'Corrente_L3', 'Tensao_L1', 'Tensao_L2', 'Tensao_L3']
    target = 'Classe_Tensao'
    
    X = df_treino[features]
    y = df_treino[target]
    
    # Divide os dados em conjuntos de treino e teste (80/20) de forma estratificada
    # para manter a proporção das classes.
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # Instancia e treina o modelo Random Forest, que é um classificador robusto.
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    print("\nModelo de IA treinado com sucesso.")
    return model, X_test, y_test

def avaliar_modelo(model, X_test, y_test):
    """
    Avalia a performance do modelo de IA e exibe métricas de desempenho.

    Parâmetros:
    - model: O modelo treinado.
    - X_test (pandas.DataFrame): O conjunto de dados de teste.
    - y_test (pandas.Series): Os rótulos de teste.
    """
    if model is None: return
    
    # Faz previsões no conjunto de teste.
    y_pred = model.predict(X_test)
    
    print("\n--- Relatório de Classificação ---\n")
    # O relatório de classificação mostra precisão, recall, f1-score e suporte por classe.
    print(classification_report(y_test, y_pred))
    
    # Gera a matriz de confusão para visualizar o desempenho de cada classe.
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(8, 6))
    # Usa a biblioteca seaborn para criar um heatmap mais visualmente agradável.
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=model.classes_, yticklabels=model.classes_)
    plt.title('Matriz de Confusão')
    plt.xlabel('Previsto')
    plt.ylabel('Real')
    plt.show()

def gerar_relatorio_console(df, model, data_str):
    """
    Gera um relatório de risco no console para uma data específica. O relatório
    identifica anomalias de tensão e fornece sugestões de ação.

    Parâmetros:
    - df (pandas.DataFrame): O DataFrame completo com os dados.
    - model: O modelo de IA treinado.
    - data_str (str): A data a ser analisada no formato 'YYYY-MM-DD'.
    """
    if df is None or model is None: return
    
    try:
        data_analise = pd.to_datetime(data_str).date()
        
        # Filtra os dados para o dia de análise.
        df_dia = df[df.index.date == data_analise].copy()
        if df_dia.empty:
            print(f"\nNenhum dado encontrado para {data_str}.")
            return

        # Considera apenas o período de operação (6h às 19h).
        df_operacao = df_dia[(df_dia.index.hour >= 6) & (df_dia.index.hour < 19)].copy()
        if df_operacao.empty:
            print(f"\nNenhum dado no período de operação (06h-19h) para {data_str}.")
            return
            
        # Usa o modelo treinado para prever a classe de tensão para os dados operacionais.
        features = ['Dem_Ativa', 'Corrente_L1', 'Corrente_L2', 'Corrente_L3', 'Tensao_L1', 'Tensao_L2', 'Tensao_L3']
        df_operacao['Previsao_Classe_Tensao'] = model.predict(df_operacao[features])
        
        # Adiciona a coluna de sugestões detalhadas ao DataFrame de operação.
        df_operacao['Sugestao'] = df_operacao.apply(adicionar_sugestao_detalhada, axis=1)
        
        # Filtra os dados para encontrar apenas as linhas com riscos (Crítica ou Precária).
        df_risco = df_operacao[df_operacao['Previsao_Classe_Tensao'].isin(['Crítica', 'Precária'])]
        
        print(f"\n--- Relatório de Risco para {data_str} (Período de Operação) ---\n")
        if not df_risco.empty:
            # Exibe os dados relevantes para as ocorrências de risco.
            print(df_risco[['Tensao_L1', 'Tensao_L2', 'Tensao_L3', 'Previsao_Classe_Tensao', 'Sugestao']])
        else:
            print("Nenhum risco de tensão detectado neste período de operação. O sistema está estável.")
            
    except Exception as e:
        print(f"Erro ao gerar relatório: {e}")

# --- Bloco Principal de Execução ---

if __name__ == "__main__":
    # Este bloco de código só é executado quando o script é rodado diretamente.
    # Ele define a sequência de operações para a análise.
    
    # Define o caminho do arquivo de dados.
    file_path = 'dados_exemplo.csv'

    # 1. Carrega e prepara os dados
    df = carregar_e_preparar_dados(file_path)

    if df is not None:
        # 2. Treina o modelo de IA
        model, X_test, y_test = treinar_modelo_ia(df)

        if model is not None:
            # 3. Avalia o modelo
            avaliar_modelo(model, X_test, y_test)

            # 4. Gera relatório de risco para uma data específica
            data_para_analise = '2023-01-01'
            gerar_relatorio_console(df, model, data_para_analise)

