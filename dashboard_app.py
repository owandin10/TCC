import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import date

# --- CONFIGURAÇÃO ---
API_URL_BASE = "http://127.0.0.1:5000/api/dados-usina" 

app = dash.Dash(__name__, external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'], suppress_callback_exceptions=True)
app.title = "Monitoramento Detalhado da Usina Solar IFG"

# ------ DATAS PARA O SELETOR ------
PRIMEIRO_DIA_DADOS_CSV = date(2025, 1, 4)
DATA_INICIAL_VISUALIZACAO = date(2025, 1, 23)
ULTIMO_DIA_DADOS_CSV = date(2025, 5, 20)
# -----------------------------------

# --- LAYOUTS DAS PÁGINAS ---

# Layout da Página Principal (Dashboard de Geração)
dashboard_layout = html.Div([
    html.Div([
        dcc.Link(html.Button("Relatório de IA e Alarmes"), href="/ia-report", style={'position': 'absolute', 'top': '20px', 'left': '20px'}),
        html.H1("Dashboard de Monitoramento da Usina Solar", style={'textAlign': 'center', 'color': '#007BFF'}),
    ], style={'position': 'relative'}),
    
    html.Div([
        dcc.DatePickerSingle(
            id='seletor-data-diario',
            min_date_allowed=PRIMEIRO_DIA_DADOS_CSV, max_date_allowed=ULTIMO_DIA_DADOS_CSV,
            initial_visible_month=DATA_INICIAL_VISUALIZACAO, date=DATA_INICIAL_VISUALIZACAO.isoformat(),
            display_format='DD/MM/YYYY',
        ),
    ], style={'textAlign': 'center', 'padding': '10px'}),
    
    html.Div([
        html.Div(dcc.Graph(id='grafico-geracao-diaria'), style={'width': '33%'}),
        html.Div(dcc.Graph(id='grafico-tensao-diaria'), style={'width': '33%'}),
        html.Div(dcc.Graph(id='grafico-corrente-diaria'), style={'width': '33%'})
    ], style={'display': 'flex'}),
    
    html.Hr(),
    html.Div([
        html.H3("Resumo do Dia Selecionado", style={'textAlign': 'center'}),
        html.Div(id='info-usina-geral', style={'maxWidth': '800px', 'margin': 'auto'})
    ])
])

# Layout da Página de Relatório de IA
ai_report_layout = html.Div([
    html.Div([
        dcc.Link(html.Button("Voltar para o Dashboard"), href="/", style={'position': 'absolute', 'top': '20px', 'left': '20px'}),
        html.H1("Relatório de Diagnóstico com IA", style={'textAlign': 'center', 'color': '#007BFF'}),
    ], style={'position': 'relative'}),
    
    html.Div([
        dcc.DatePickerSingle(
            id='ia-seletor-data',
            min_date_allowed=PRIMEIRO_DIA_DADOS_CSV, max_date_allowed=ULTIMO_DIA_DADOS_CSV,
            initial_visible_month=DATA_INICIAL_VISUALIZACAO, date=DATA_INICIAL_VISUALIZACAO.isoformat(),
            display_format='DD/MM/YYYY',
        ),
    ], style={'textAlign': 'center', 'padding': '20px'}),
    
    html.H4("Ocorrências de Risco Previstas pela IA", style={'textAlign': 'center'}),
    dcc.Loading(id="loading-ai-report", children=[html.Div(id='ai-report-container')])
])

# --- Estrutura principal com roteamento ---
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

@app.callback(Output('page-content', 'children'), [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/ia-report':
        return ai_report_layout
    return dashboard_layout

# --- CALLBACKS DO DASHBOARD PRINCIPAL ---
@app.callback(
    [Output('info-usina-geral', 'children'),
     Output('grafico-geracao-diaria', 'figure'),
     Output('grafico-tensao-diaria', 'figure'),
     Output('grafico-corrente-diaria', 'figure')],
    [Input('seletor-data-diario', 'date')]
)
def atualizar_dashboard_principal(data_selecionada_str):
    if not data_selecionada_str:
        return dash.no_update

    url = f"{API_URL_BASE}?data={data_selecionada_str}"
    try:
        response = requests.get(url, timeout=10).json()
        if "erro" in response or response.get("erro_dia_selecionado"):
            raise Exception(response.get("erro") or response.get("erro_dia_selecionado"))

        df_dia = pd.DataFrame(response['leituras_dia_selecionado'])
        df_dia['DateTime'] = pd.to_datetime(df_dia['DateTime'])
        
        fig_geracao = go.Figure(data=go.Scatter(x=df_dia['DateTime'], y=df_dia['Dem_Ativa'], mode='lines', fill='tozeroy')).update_layout(title="Potência Ativa (kW)")
        fig_tensao = go.Figure().add_traces([go.Scatter(x=df_dia['DateTime'], y=df_dia[f'Tensao_L{i}'], name=f'Tensão L{i}') for i in [1,2,3]]).update_layout(title="Tensão por Fase (V)")
        fig_corrente = go.Figure().add_traces([go.Scatter(x=df_dia['DateTime'], y=df_dia[f'Corrente_L{i}'], name=f'Corrente L{i}') for i in [1,2,3]]).update_layout(title="Corrente por Fase (A)")

        pico = response['dados_pico_dia']
        resumo_html = html.Div([
            html.Div([
                html.H5("Informações Gerais"),
                html.P(f"Energia Gerada no Dia: {response['geracao_total_dia_kwh']:.2f} kWh"),
            ], style={'width': '48%', 'display': 'inline-block'}),
            html.Div([
                html.H5(f"Dados no Pico ({pd.to_datetime(pico['timestamp_pico']).strftime('%H:%M')})"),
                html.P(f"Potência: {pico.get('Dem_Ativa', 0):.2f} kW"),
            ], style={'width': '48%', 'display': 'inline-block'})
        ])
        
        return resumo_html, fig_geracao, fig_tensao, fig_corrente
    except Exception as e:
        fig_vazia = go.Figure().update_layout(title_text=f"Erro: {e}")
        return html.P(f"Erro ao carregar dados: {e}"), fig_vazia, fig_vazia, fig_vazia

# --- CALLBACK DA PÁGINA DE IA ---
@app.callback(
    Output('ai-report-container', 'children'),
    [Input('ia-seletor-data', 'date')]
)
def gerar_relatorio_ia(data_selecionada_str):
    if not data_selecionada_str:
        return html.P("Selecione uma data para a análise.")

    url = f"{API_URL_BASE}?data={data_selecionada_str}"
    try:
        response = requests.get(url, timeout=20).json()
        if "erro" in response: raise Exception(response["erro"])
        
        relatorio_data = response.get('relatorio_ia', [])
        
        if not relatorio_data:
            return html.Div([
                html.H5("✅ Sistema Estável", style={'color': 'green'}),
                html.P("Nenhuma ocorrência de risco foi prevista pela IA.")
            ], style={'textAlign': 'center', 'padding': '20px'})

        return dash_table.DataTable(
            columns=[
                {'name': 'Horário', 'id': 'Horario'},
                {'name': 'Classe Prevista', 'id': 'Previsao_Classe_Tensao'},
                {'name': 'Sugestão da IA', 'id': 'Sugestao'},
            ],
            data=relatorio_data,
            style_cell={'whiteSpace': 'normal', 'height': 'auto'},
            style_data_conditional=[
                {'if': {'filter_query': '{Previsao_Classe_Tensao} = "Crítica"'}, 'backgroundColor': '#FF4136', 'color': 'white'},
                {'if': {'filter_query': '{Previsao_Classe_Tensao} = "Precária"'}, 'backgroundColor': '#FF851B', 'color': 'white'}
            ]
        )
    except Exception as e:
        return html.P(f"Erro ao carregar a análise da IA: {e}", style={'color': 'red'})

if __name__ == '__main__':
    app.run(debug=True, port=8050)
