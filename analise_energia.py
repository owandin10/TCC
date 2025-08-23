import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import classification_report, confusion_matrix

# Bloco 1: Carregamento e Tratamento Inicial dos Dados
def carregar_dados_e_tratar_colunas(file_path):
    df = pd.read_csv(file_path)

    # Dicionário de mapeamento para os nomes exatos do seu arquivo CSV
    column_mapping = {
        'DateTime': 'Timestamp',
        'Dem_Ativa': 'Geracao', # Usando a coluna Dem_Ativa no lugar de Geracao
        'Corrente_L1': 'Corrente_L1',
        'Corrente_L2': 'Corrente_L2',
        'Corrente_L3': 'Corrente_L3',
        'Tensao_L1': 'Tensao_L1',
        'Tensao_L2': 'Tensao_L2',
        'Tensao_L3': 'Tensao_L3'
    }
    
    # Renomeia as colunas usando o dicionário de mapeamento
    df = df.rename(columns=column_mapping)
    
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    df = df.set_index('Timestamp')
    return df

# Bloco 2: Limpeza e Preparação dos Dados
def preparar_dados(df):
    df = df.fillna(0)
    numeric_cols = ['Geracao', 'Corrente_L1', 'Corrente_L2', 'Corrente_L3', 'Tensao_L1', 'Tensao_L2', 'Tensao_L3']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    return df

# Bloco 3: Lógica de Classificação da Tensão
def classificar_tensao_trifasica(row):
    tensao1, tensao2, tensao3 = row['Tensao_L1'], row['Tensao_L2'], row['Tensao_L3']
    if any(t > 233 for t in [tensao1, tensao2, tensao3]) or any(t < 191 for t in [tensao1, tensao2, tensao3]):
        return 'Crítica'
    elif any(t > 231 for t in [tensao1, tensao2, tensao3]) or any(t < 202 for t in [tensao1, tensao2, tensao3]):
        return 'Precária'
    else:
        return 'Adequada'

# Bloco 4: Treinamento do Modelo de IA
def treinar_modelo(df):
    features = ['Geracao', 'Corrente_L1', 'Corrente_L2', 'Corrente_L3', 'Tensao_L1', 'Tensao_L2', 'Tensao_L3']
    target = 'Classe_Tensao'
    X = df[features]
    y = df[target]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    model_rf = RandomForestClassifier(n_estimators=100, random_state=42)
    model_rf.fit(X_train, y_train)
    return model_rf, X_test, y_test

# Bloco 5: Avaliação do Modelo (opcional)
def avaliar_modelo(model, X_test, y_test):
    y_pred = model.predict(X_test)
    cm = confusion_matrix(y_test, y_pred)
    classes = ['Adequada', 'Precária', 'Crítica']
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=classes, yticklabels=classes)
    plt.title('Matriz de Confusão do Modelo de Classificação')
    plt.xlabel('Valores Previstos')
    plt.ylabel('Valores Reais')
    plt.show()
    print("\nRelatório de Classificação Detalhado:")
    print(classification_report(y_test, y_pred))

# Bloco 6: Lógica para Sugestões Detalhadas
def adicionar_sugestao_trifasica(row):
    previsao = row['Previsao_Classe_Tensao']
    sugestoes = []
    if previsao == 'Adequada':
        return "Tensão na faixa normal em todas as fases. Sem alerta."
    for fase in ['L1', 'L2', 'L3']:
        tensao = row[f'Tensao_{fase}']
        if tensao > 233:
            sugestoes.append(f"Tensão {fase}: acima do limite! Causa: Geração excessiva ou flutuação na rede. Sugestão: Verifique as configurações do inversor ou contate a concessionária.")
        elif tensao < 191:
            sugestoes.append(f"Tensão {fase}: abaixo do limite! Causa: Sobrecarga na rede, problemas no inversor. Sugestão: Verifique se há sobrecarga ou se o inversor está operando corretamente.")
        elif previsao == 'Precária':
            if 231 <= tensao <= 233:
                sugestoes.append(f"Tensão {fase}: um pouco acima do ideal. Causa: Flutuações da rede elétrica. Sugestão: Monitore a rede e as conexões.")
            elif 202 <= tensao < 202:
                sugestoes.append(f"Tensão {fase}: um pouco abaixo do ideal. Causa: Queda de tensão em cabos, conexões frouxas. Sugestão: Verifique a fiação e as conexões.")
    return "ALERTA: " + " ".join(sugestoes) if sugestoes else "Tensão anormal. Causas indefinidas. Realize inspeção geral."

# Bloco 7: Relatório Final
def gerar_relatorio_final(df):
    pd.set_option('display.max_rows', None)
    print("Datas disponíveis no DataFrame:")
    print(df.index.strftime('%Y-%m-%d').unique())
    data_analise_str = input("\nDigite a data que deseja analisar (formato AAAA-MM-DD): ")
    
    try:
        data_analise = pd.to_datetime(data_analise_str).date()
        df_dia = df[df.index.date == data_analise].copy()
        if df_dia.empty:
            print(f"Nenhum dado encontrado para a data {data_analise_str}.")
        else:
            df_operacao = df_dia[(df_dia.index.hour >= 6) & (df_dia.index.hour < 18)].copy()
            if not df_operacao.empty:
                df_risco = df_operacao[(df_operacao['Previsao_Classe_Tensao'] == 'Precária') | (df_operacao['Previsao_Classe_Tensao'] == 'Crítica')].copy()
                print(f"\nRelatório de Ocorrências de Risco ({data_analise_str}, 06:00h às 18:00h):")
                if not df_risco.empty:
                    print(df_risco[['Tensao_L1', 'Tensao_L2', 'Tensao_L3', 'Previsao_Classe_Tensao', 'Sugestão']])
                else:
                    print(f"Nenhuma ocorrência de risco encontrada no período de operação para o dia {data_analise_str}. O sistema operou de forma estável.")
            else:
                print(f"Nenhum dado de operação (06:00h às 18:00h) encontrado para a data {data_analise_str}.")
    except ValueError:
        print("Formato de data inválido. Por favor, use o formato AAAA-MM-DD.")

# Fluxo principal do programa
if __name__ == "__main__":
    file_path = "data/data.csv"
    
    try:
        df = carregar_dados_e_tratar_colunas(file_path)
        df = preparar_dados(df)
        df['Classe_Tensao'] = df.apply(classificar_tensao_trifasica, axis=1)
        
        model_rf, X_test, y_test = treinar_modelo(df)
        
        df['Previsao_Classe_Tensao'] = model_rf.predict(df[X_test.columns])
        df['Sugestão'] = df.apply(adicionar_sugestao_trifasica, axis=1)
        
        gerar_relatorio_final(df)
    except FileNotFoundError:
        print(f"Erro: O arquivo '{file_path}' não foi encontrado. Por favor, verifique o caminho e o nome do arquivo.")


