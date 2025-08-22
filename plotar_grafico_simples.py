import pandas as pd
import plotly.express as px
import os

# --- PASSO 1: CONFIGURAÇÃO DE CAMINHOS ---
# O script espera que o ficheiro CSV esteja numa subpasta chamada 'data'.

try:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
except NameError:
    BASE_DIR = os.getcwd()

# ATENÇÃO: Verifique se o nome do seu novo CSV é realmente "dados.csv"
caminho_do_csv = os.path.join(BASE_DIR, "data", "data.csv")
print(f"A tentar ler o ficheiro em: {caminho_do_csv}")

# --- PASSO 2: LEITURA E VALIDAÇÃO DO FICHEIRO CSV ---
try:
    df = pd.read_csv(
        caminho_do_csv,
        sep=',',
        # IMPORTANTE: Se o seu CSV usa vírgula como decimal (ex: 220,5), mude para decimal=','
        decimal='.', 
        parse_dates=['DateTime'],
        index_col='DateTime'
    )
    print("Ficheiro CSV lido com sucesso.")
except FileNotFoundError:
    print(f"\nERRO CRÍTICO: O ficheiro não foi encontrado. Verifique o caminho: '{caminho_do_csv}'")
    exit()
except Exception as e:
    print(f"\nERRO CRÍTICO ao ler o ficheiro CSV: {e}")
    exit()

# --- PASSO 3: LIMPEZA DOS DADOS (VERSÃO ATUALIZADA) ---
# Lista de todas as colunas que devem ser numéricas
cols_numericas = [
    'Dem_Ativa', 'Dem_Reat', 
    'Tensao_L1', 'Tensao_L2', 'Tensao_L3',
    'Corrente_L1', 'Corrente_L2', 'Corrente_L3',
    'Fat_Pot', 'Fat_Carga'
]

# Itera sobre a lista e converte cada coluna, tratando erros
for col in cols_numericas:
    # Verifica se a coluna existe antes de tentar converter
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    else:
        print(f"AVISO: A coluna '{col}' não foi encontrada no seu CSV.")

df.fillna(0, inplace=True)
print("Limpeza e conversão de dados concluída.")

# --- PASSO 4: LOOP INTERATIVO PARA SELECIONAR O DIA ---
while True:
    print("\n------------------------------------------------------------")
    data_min = df.index.date.min().strftime('%Y-%m-%d')
    data_max = df.index.date.max().strftime('%Y-%m-%d')
    print(f"As datas disponíveis vão de {data_min} a {data_max}.")

    data_selecionada_str = input("Digite a data que você quer ver (formato AAAA-MM-DD) ou 'sair' para fechar: ")

    if data_selecionada_str.lower() == 'sair':
        print("A encerrar o programa.")
        break

    try:
        data_selecionada = pd.to_datetime(data_selecionada_str).date()
        df_dia = df[df.index.date == data_selecionada].copy()

        if not df_dia.empty:
            print(f"\nA mostrar gráficos para o dia {data_selecionada_str}...")

            # Gráfico de Geração Ativa (Sem alterações)
            fig_geracao = px.area(
                df_dia,
                x=df_dia.index,
                y="Dem_Ativa",
                title=f"Geração de Energia Ativa para o dia {data_selecionada_str}",
                labels={"index": "Hora do Dia", "Dem_Ativa": "Geração Ativa (kW)"}
            )
            fig_geracao.show()

            # Gráfico de Tensão (ATUALIZADO PARA 3 FASES)
            fig_tensao = px.line(
                df_dia,
                x=df_dia.index,
                y=["Tensao_L1", "Tensao_L2", "Tensao_L3"], # Plota as 3 fases
                title=f"Tensão CA por Fase para o dia {data_selecionada_str}",
                labels={"index": "Hora do Dia", "value": "Tensão (V)", "variable": "Fase"}
            )
            fig_tensao.show()

            # NOVO GRÁFICO DE CORRENTE (ADICIONADO)
            fig_corrente = px.line(
                df_dia,
                x=df_dia.index,
                y=["Corrente_L1", "Corrente_L2", "Corrente_L3"], # Plota as 3 fases
                title=f"Corrente CA por Fase para o dia {data_selecionada_str}",
                labels={"index": "Hora do Dia", "value": "Corrente (A)", "variable": "Fase"}
            )
            fig_corrente.show()

        else:
            print(f"AVISO: Nenhum dado foi encontrado para o dia {data_selecionada_str}. Por favor, tente outra data.")

    except ValueError:
        print(f"ERRO: '{data_selecionada_str}' não é uma data válida. Por favor, use o formato AAAA-MM-DD.")
    except Exception as e:
        print(f"Ocorreu um erro inesperado ao gerar os gráficos: {e}")
