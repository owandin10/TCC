# -*- coding: utf-8 -*-
# ======================================================================

# Dashboard de Monitoramento de Usinas Solares Fotovoltaicas
# ------------------------------------------------------------------------------
# Este é um aplicativo web interativo construído com a biblioteca Dash,
# permitindo a visualização de dados de uma usina solar e o diagnóstico
# de possíveis falhas utilizando um modelo de Inteligência Artificial.
# A aplicação integra visualizações gráficas, indicadores de desempenho
# e um relatório de alertas com sugestões de manutenção.
# ======================================================================

import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.graph_objects as go
from datetime import date
import os
from sklearn.ensemble import RandomForestClassifier
import traceback

# --- 1. Configuração e Inicialização do Ambiente ---
# ---------------------------------------------------
# Define o caminho do arquivo de dados e as variáveis globais que
# irão persistir durante a vida do aplicativo, como o DataFrame
# de dados e o modelo de IA. A inicialização global evita o
# reprocessamento a cada requisição, otimizando a performance.

try:
    # Tenta obter o caminho absoluto do diretório do script para garantir a
    # portabilidade do código em diferentes ambientes.
    PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
except NameError:
    # Fallback seguro para ambientes de execução onde __file__ não está disponível.
    PROJECT_ROOT = os.getcwd()

DATA_FILE_PATH = os.path.join(PROJECT_ROOT, "data", "data.csv")

# Variáveis globais para armazenar os dados e o modelo de IA.
df_usina_global = None
model_global = None
feature_columns_global = ['Dem_Ativa', 'Corrente_L1', 'Corrente_L2', 'Corrente_L3', 'Tensao_L1', 'Tensao_L2', 'Tensao_L3']


# --- 2. Funções de Análise e IA ---
# ----------------------------------
# Funções de lógica de negócio responsáveis pela classificação dos dados
# e pela geração de sugestões de diagnóstico.

def classificar_tensao_trifasica(row):
    """
    Classifica a tensão trifásica em categorias de risco (Crítica, Precária)
    ou de estabilidade (Adequada, Inativo) com base em limites técnicos.
    A lógica reflete a interpretação de padrões de qualidade de energia.
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
    Gera uma string de sugestão detalhada para o problema de tensão detectado.
    As sugestões são baseadas na classificação da IA e em regras de negócio
    para fornecer um diagnóstico prático ao operador do sistema.
    """
    classificacao = row['Previsao_Classe_Tensao']
    if classificacao in ['Adequada', 'Inativo']:
        return "Operação dentro dos parâmetros normais."

    detalhes_fases, sugestoes = [], set()
    for fase in ['L1', 'L2', 'L3']:
        tensao = row.get(f'Tensao_{fase}', 0)
        if tensao > 233:
            detalhes_fases.append(f"Fase {fase} com sobretensão CRÍTICA ({tensao:.1f}V).")
            sugestoes.add("Ação: Contatar a concessionária imediatamente. Inspecionar o transformador.")
        elif tensao > 231:
            detalhes_fases.append(f"Fase {fase} com sobretensão PRECÁRIA ({tensao:.1f}V).")
            sugestoes.add("Ação: Monitorar a estabilidade da tensão nas próximas horas.")
        elif tensao < 191:
            detalhes_fases.append(f"Fase {fase} com subtensão CRÍTICA ({tensao:.1f}V).")
            sugestoes.add("Ação: Desligar cargas não essenciais. Inspecionar disjuntores e fiação.")
        elif tensao < 202:
            detalhes_fases.append(f"Fase {fase} com subtensão PRECÁRIA ({tensao:.1f}V).")
            sugestoes.add("Ação: Realizar inspeção e reaperto das conexões elétricas.")

    mensagem_final = "\n".join(detalhes_fases)
    if sugestoes:
        # Ordena as sugestões para garantir consistência.
        mensagem_final += "\n\n" + "\n".join(sorted(list(sugestoes)))

    return mensagem_final if mensagem_final else "Anomalia detectada. Realizar inspeção geral."

def carregar_e_treinar():
    """
    Função de inicialização do aplicativo. Carrega os dados do arquivo CSV,
    realiza o pré-processamento e treina o modelo de classificação.
    Esta função é chamada uma única vez na inicialização do servidor.
    """
    global df_usina_global, model_global
    print(">>> INICIANDO APLICAÇÃO: Carregando dados e treinando modelo de IA...")
    try:
        # Leitura e processamento inicial dos dados.
        df = pd.read_csv(DATA_FILE_PATH, sep=',', decimal='.', parse_dates=['DateTime'])
        df = df.set_index('DateTime')
        for col in feature_columns_global:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        df['Classe_Tensao'] = df.apply(classificar_tensao_trifasica, axis=1)

        # Treinamento do modelo RandomForestClassifier.
        df_treino = df[df['Classe_Tensao'] != 'Inativo'].copy()
        X, y = df_treino[feature_columns_global], df_treino['Classe_Tensao']
        model_rf = RandomForestClassifier(n_estimators=100, random_state=42)
        model_rf.fit(X, y)

        # Atribuição dos resultados às variáveis globais.
        model_global, df_usina_global = model_rf, df
        print(">>> INICIALIZAÇÃO COMPLETA: Modelo pronto e dados carregados.")
    except Exception as e:
        print(f"ERRO FATAL ao carregar/treinar: {e}")
        df_usina_global, model_global = pd.DataFrame(), None


# --- 3. Inicialização e Layout do Aplicativo ---
# -----------------------------------------------
# Define o objeto app do Dash e a estrutura visual do dashboard.
# O layout é dividido em duas páginas: o dashboard principal e o
# relatório de IA, acessíveis através de rotas.

app = dash.Dash(__name__, external_stylesheets=['https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css'], suppress_callback_exceptions=True)
app.title = "Monitoramento IFG - Usina Solar"

# Constantes de estilo para manter a consistência visual.
PRIMEIRO_DIA_DADOS_CSV, DATA_INICIAL_VISUALIZACAO, ULTIMO_DIA_DADOS_CSV = date(2025, 1, 4), date(2025, 1, 23), date(2025, 5, 20)
card_style = {'backgroundColor': 'white', 'border': '1px solid #e0e0e0', 'borderRadius': '12px', 'padding': '20px', 'boxShadow': '0 6px 12px rgba(0,0,0,0.1)', 'height': '100%'}
button_style = {'fontSize': '1.1em', 'fontWeight': '600', 'padding': '12px 24px', 'borderRadius': '10px', 'margin': '8px', 'border': 'none', 'cursor': 'pointer'}
light_theme = {'background': '#f0f2f5', 'text': '#333333', 'header_bg': '#1a1a2e', 'header_text': 'white', 'graph_bg': 'white', 'critical_color': '#e74c3c', 'precarious_color': '#f39c12', 'stable_color': '#2ecc71'}
alarm_block_style = {'borderRadius': '12px', 'padding': '20px', 'marginBottom': '15px', 'boxShadow': '0 4px 8px rgba(0,0,0,0.1)', 'color': 'white'}

# Layout da página principal do dashboard.
dashboard_layout = html.Div(style={'backgroundColor': light_theme['background'], 'color': light_theme['text'], 'minHeight': '100vh', 'display': 'flex', 'flexDirection': 'column'}, children=[
    html.Div(className="d-flex align-items-center justify-content-center p-4 text-white", style={'backgroundColor': light_theme['header_bg'], 'position': 'relative'}, children=[
        html.H3("G&W", style={'position': 'absolute', 'left': '20px', 'color': light_theme['header_text']}),
        html.H1("Plataforma de Monitoramento e Diagnóstico", style={'margin': '0', 'fontSize': '1.8em'})
    ]),
    html.Div(className="text-center p-3", children=[
        dcc.Link(html.Button("Relatório de IA e Alarmes", className="btn", style={**button_style, 'backgroundColor': light_theme['critical_color'], 'color': 'white'}), href="/ia-report")
    ]),
    html.Div(className="container mt-4 flex-grow-1", children=[
        html.Div(className="d-flex flex-column align-items-center mb-4 p-4", style={'backgroundColor': 'white', 'borderRadius': '12px'}, children=[
            html.H5("Selecione a Data para Visualização", className="mb-2"),
            dcc.DatePickerSingle(id='seletor-data-diario', min_date_allowed=PRIMEIRO_DIA_DADOS_CSV, max_date_allowed=ULTIMO_DIA_DADOS_CSV, date=DATA_INICIAL_VISUALIZACAO.isoformat(), display_format='DD/MM/YYYY'),
            html.Div(className="d-flex flex-wrap justify-content-center mt-3", children=[
                html.Button("Geração (kW)", id="btn-geracao", n_clicks=0, style={**button_style, 'backgroundColor': light_theme['stable_color'], 'color': 'white'}),
                html.Button("Tensão (V)", id="btn-tensao", n_clicks=0, style={**button_style, 'backgroundColor': light_theme['precarious_color'], 'color': 'white'}),
                html.Button("Corrente (A)", id="btn-corrente", n_clicks=0, style={**button_style, 'backgroundColor': light_theme['critical_color'], 'color': 'white'})
            ])
        ]),
        dcc.Loading(id="loading-main-content", children=[
            dcc.Graph(id='grafico-principal'),
            html.Hr(className="my-4"),
            html.H3("Resumo do Dia Selecionado", className="text-center mb-3"),
            html.Div(id='cards-resumo-container', className="row justify-content-center align-items-stretch")
        ])
    ]),
    html.Footer(html.P("Sistema desenvolvido por Wanderley Oliveira e Gilberto Ferreira", className="text-center text-muted p-3"), style={'backgroundColor': light_theme['background']})
])

# Layout da página de Relatório de IA.
ai_report_layout = html.Div(style={'backgroundColor': light_theme['background'], 'color': light_theme['text'], 'minHeight': '100vh'}, children=[
    html.Div(className="container mt-4", children=[
        html.Div(className="d-flex align-items-center justify-content-center p-4 text-white", style={'backgroundColor': light_theme['header_bg']}, children=[html.H1("Relatório de Diagnóstico com IA")]),
        html.Div(className="p-3 text-center", children=[dcc.Link(html.Button("Voltar para o Dashboard", className="btn btn-secondary", style=button_style), href="/")]),
        html.Div(dcc.DatePickerSingle(id='ia-seletor-data', min_date_allowed=PRIMEIRO_DIA_DADOS_CSV, max_date_allowed=ULTIMO_DIA_DADOS_CSV, date=DATA_INICIAL_VISUALIZACAO.isoformat(), display_format='DD/MM/YYYY'), style={'textAlign': 'center', 'padding': '20px'}),
        dcc.Loading(id="loading-ai-report", children=[html.Div(id='ai-report-container')])
    ])
])

# Layout principal que gerencia as rotas.
app.layout = html.Div([dcc.Location(id='url', refresh=False), html.Div(id='page-content')])


# --- 4. Callbacks e Interatividade ---
# -------------------------------------
# Define as funções de callback que conectam as interações do usuário (entradas)
# com as atualizações do layout do aplicativo (saídas).

@app.callback(Output('page-content', 'children'), [Input('url', 'pathname')])
def display_page(pathname):
    """
    Roteia a navegação do usuário entre as diferentes páginas do aplicativo
    com base no pathname da URL.
    """
    if pathname == '/ia-report':
        return ai_report_layout
    return dashboard_layout

@app.callback(
    [Output('grafico-principal', 'figure'),
     Output('cards-resumo-container', 'children')],
    [Input('seletor-data-diario', 'date'),
     Input('btn-geracao', 'n_clicks'),
     Input('btn-tensao', 'n_clicks'),
     Input('btn-corrente', 'n_clicks')]
)
def update_dashboard_unified(data_selecionada_str, btn_g, btn_t, btn_c):
    """
    Callback unificado que atualiza o gráfico principal e os cards de resumo
    com base na data selecionada e no botão de visualização clicado.
    Ele determina qual gráfico mostrar com base no contexto do callback.
    """
    if not data_selecionada_str or df_usina_global is None:
        raise dash.exceptions.PreventUpdate

    try:
        ctx = dash.callback_context
        button_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered and ctx.triggered[0]['value'] else 'btn-geracao'
        
        dia_para_analise = pd.to_datetime(data_selecionada_str).date()
        df_dia = df_usina_global[df_usina_global.index.date == dia_para_analise].copy()

        if df_dia.empty:
            fig_vazia = go.Figure().update_layout(title_text=f"Nenhum dado para {dia_para_analise.strftime('%d/%m/%Y')}", template="plotly_white")
            cards_vazios = [html.Div(html.P(f"Nenhum dado para {dia_para_analise.strftime('%d/%m/%Y')}"), style=card_style, className="col-md-4")]
            return fig_vazia, cards_vazios

        pico = df_dia.loc[df_dia['Dem_Ativa'].idxmax()]
        
        fig, cards = None, []
        if button_id == 'btn-tensao':
            fig = go.Figure().add_traces([go.Scatter(x=df_dia.index, y=df_dia[f'Tensao_L{i}'], name=f'Tensão L{i}') for i in [1, 2, 3]])
            fig.update_layout(title="Tensão por Fase (V)", template="plotly_white")
            card_tensao = html.Div([html.H5("Tensão no Pico"), *[html.P(f"L{i}: {pico.get(f'Tensao_L{i}', 0):.1f}V") for i in [1, 2, 3]]], style=card_style)
            cards = [html.Div(card_tensao, className="col-md-4")]
        elif button_id == 'btn-corrente':
            fig = go.Figure().add_traces([go.Scatter(x=df_dia.index, y=df_dia[f'Corrente_L{i}'], name=f'Corrente L{i}') for i in [1, 2, 3]])
            fig.update_layout(title="Corrente por Fase (A)", template="plotly_white")
            card_corrente = html.Div([html.H5("Corrente no Pico"), *[html.P(f"L{i}: {pico.get(f'Corrente_L{i}', 0):.1f}A") for i in [1, 2, 3]]], style=card_style)
            cards = [html.Div(card_corrente, className="col-md-4")]
        else: # Padrão: btn-geracao
            fig = go.Figure(data=go.Scatter(x=df_dia.index, y=df_dia['Dem_Ativa'], mode='lines', fill='tozeroy', line={'color': light_theme['stable_color']}))
            fig.update_layout(title="Potência Ativa (kW)", template="plotly_white")
            card_geracao = html.Div([html.H5("Energia Gerada"), html.H2(f"{df_dia['Dem_Ativa'].sum() * (5/60):.2f} kWh")], style=card_style)
            card_pico = html.Div([html.H5("Pico de Geração"), html.H2(f"{pico['Dem_Ativa']:.2f} kW"), html.P(f"às {pico.name.strftime('%H:%M')}")], style=card_style)
            cards = [html.Div(card_geracao, className="col-md-4"), html.Div(card_pico, className="col-md-4")]
        return fig, cards

    except Exception as e:
        print(f"ERRO CALLBACK DASHBOARD: {e}")
        fig_vazia = go.Figure().update_layout(title_text=f"Erro ao carregar dados: {e}", template="plotly_white")
        cards_vazios = [html.Div(html.P(f"Erro: {e}"), style=card_style, className="col-md-4")]
        return fig_vazia, cards_vazios

@app.callback(Output('ai-report-container', 'children'), [Input('ia-seletor-data', 'date')])
def gerar_relatorio_ia(data_selecionada_str):
    """
    Callback responsável por gerar o relatório de diagnóstico da IA.
    Ele processa os dados do dia selecionado, utiliza o modelo de IA
    treinado e renderiza os alertas visuais com sugestões.
    """
    if not data_selecionada_str or df_usina_global is None or model_global is None:
        return html.P("Selecione uma data para a análise.")
    try:
        dia_para_analise = pd.to_datetime(data_selecionada_str).date()
        df_dia = df_usina_global[df_usina_global.index.date == dia_para_analise].copy()
        
        if df_dia.empty:
            return html.P(f"Nenhum dado para {dia_para_analise.strftime('%d/%m/%Y')}.")

        df_operacao = df_dia[(df_dia.index.hour >= 6) & (df_dia.index.hour < 19)].copy()
        
        if df_operacao.empty:
            return html.Div([html.H5("Sistema Estável"), html.P("Nenhuma ocorrência de risco (sem dados no período de operação).")], style={'textAlign': 'center', 'padding': '20px'})

        df_operacao['Previsao_Classe_Tensao'] = model_global.predict(df_operacao[feature_columns_global])
        df_risco = df_operacao[df_operacao['Previsao_Classe_Tensao'].isin(['Crítica', 'Precária'])].copy()
        
        if df_risco.empty:
            return html.Div([html.H5("Sistema Estável"), html.P("Nenhuma ocorrência de risco foi prevista pela IA.")], style={'textAlign': 'center', 'padding': '20px'})

        df_risco['Sugestao'] = df_risco.apply(adicionar_sugestao_detalhada, axis=1)
        df_risco['Horario'] = df_risco.index.strftime('%H:%M:%S')

        # Cria os blocos de alerta dinamicamente com base nos dados.
        alarm_blocks = [
            html.Div(className="col-12 col-md-6 col-lg-4 d-flex", children=[
                html.Div(
                    style={**alarm_block_style, 'backgroundColor': light_theme['critical_color'] if row['Previsao_Classe_Tensao'] == 'Crítica' else light_theme['precarious_color'], 'flexGrow': 1},
                    children=[
                        html.H5(f"Alerta: {row['Previsao_Classe_Tensao']} ({row['Horario']})", style={'fontWeight': 'bold'}),
                        html.P(row['Sugestao'], style={'whiteSpace': 'pre-wrap'})
                    ]
                )
            ])
            for index, row in df_risco.iterrows()
        ]
        return html.Div(className="row justify-content-center", children=alarm_blocks)

    except Exception as e:
        print(f"ERRO CALLBACK RELATORIO IA: {e}")
        return html.P(f"Erro ao gerar relatório: {e}", style={'color': 'red'})


# --- 5. Execução do Servidor ---
# -------------------------------
if __name__ == '__main__':
    # Inicia o aplicativo e o servidor web.
    # A função de carregamento e treinamento é chamada antes de o servidor ser
    # executado, garantindo que tudo esteja pronto.
    carregar_e_treinar()
    app.run(debug=True, port=8050)

