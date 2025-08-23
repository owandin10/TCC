import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import date

# --- CONFIGURAÇÃO ---
API_URL_BASE = "http://127.0.0.1:5000/api/dados-usina" 

app = dash.Dash(__name__, external_stylesheets=[
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css',
    'https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap'
], suppress_callback_exceptions=True)
app.title = "Monitoramento IFG - Usina Solar"

# ------ DATAS PARA O SELETOR ------
PRIMEIRO_DIA_DADOS_CSV = date(2025, 1, 4)
DATA_INICIAL_VISUALIZACAO = date(2025, 1, 23)
ULTIMO_DIA_DADOS_CSV = date(2025, 5, 20)
# -----------------------------------

# Estilos reutilizáveis
card_info_style = {
    'backgroundColor': 'white', 'border': '1px solid #e0e0e0',
    'borderRadius': '10px', 'padding': '20px',
    'boxShadow': '0 4px 8px rgba(0,0,0,0.1)', 'marginBottom': '20px',
    'textAlign': 'center', 'height': '150px'
}

card_unificado_style = {
    'backgroundColor': 'white', 'border': '1px solid #e0e0e0',
    'borderRadius': '10px', 'padding': '20px',
    'boxShadow': '0 4px 8px rgba(0,0,0,0.1)', 'marginBottom': '20px',
    'textAlign': 'center'
}

button_style = {
    'fontSize': '1.2em', 'fontWeight': '600', 'padding': '10px 20px',
    'borderRadius': '8px', 'margin': '5px', 'border': 'none', 'cursor': 'pointer',
    'transition': 'all 0.3s ease-in-out', 'boxShadow': '0 2px 4px rgba(0,0,0,0.2)'
}

light_theme = {
    'background': '#f8f9fa', 'text': '#212529', 'header_bg': '#000000',
    'header_text': 'white', 'graph_bg': 'white', 'graph_plot_bg': 'white',
    'critical_color': '#FF9999', 'precarious_color': '#FFD866'
}

# --- LAYOUTS DAS PÁGINAS ---

# Layout da Página Principal (Dashboard de Geração)
dashboard_layout = html.Div(
    id='main-dashboard-layout',
    style={'backgroundColor': light_theme['background'], 'color': light_theme['text'], 'fontFamily': 'Poppins'},
    children=[
        html.Div(
            className="d-flex align-items-center justify-content-center p-4 text-white",
            style={'position': 'relative', 'backgroundColor': light_theme['header_bg']},
            children=[
                html.H3("G & W", style={'position': 'absolute', 'left': '20px'}),
                html.H1("Plataforma de Monitoramento e Diagnóstico de Geração Distribuída", style={'margin': '0'})
            ]
        ),
        html.Div(
            className="p-3",
            children=[
                dcc.Link(html.Button("Relatório de IA e Alarmes", className="btn btn-danger"), href="/ia-report"),
            ]
        ),
        html.Div(
            className="container mt-4",
            children=[
                html.Div(
                    className="d-flex flex-column align-items-center mb-4",
                    children=[
                        html.H5("Selecione a Data para Visualização", className="mb-2"),
                        dcc.DatePickerSingle(
                            id='seletor-data-diario',
                            min_date_allowed=PRIMEIRO_DIA_DADOS_CSV, max_date_allowed=ULTIMO_DIA_DADOS_CSV,
                            initial_visible_month=DATA_INICIAL_VISUALIZACAO, date=DATA_INICIAL_VISUALIZACAO.isoformat(),
                            display_format='DD/MM/YYYY',
                        ),
                        html.Div(
                            className="d-flex justify-content-center mt-3",
                            children=[
                                html.Button("Gráfico de Geração", id="btn-geracao", style={**button_style, 'backgroundColor': 'green', 'color': 'white'}),
                                html.Button("Gráfico de Tensão", id="btn-tensao", style={**button_style, 'backgroundColor': 'orange', 'color': 'white'}),
                                html.Button("Gráfico de Corrente", id="btn-corrente", style={**button_style, 'backgroundColor': 'purple', 'color': 'white'})
                            ]
                        )
                    ]
                ),
                html.Div([
                    dcc.Graph(id='grafico-geracao-diaria', style={'display': 'block'}),
                    dcc.Graph(id='grafico-tensao-diaria', style={'display': 'none'}),
                    dcc.Graph(id='grafico-corrente-diaria', style={'display': 'none'})
                ]),
                html.Hr(className="my-4"),
                html.Div([
                    html.H3("Resumo do Dia Selecionado", className="text-center mb-3"),
                    html.Div(
                        className="row justify-content-center",
                        children=[
                            html.Div(id='card-geracao-total', className="col-md-6 col-lg-4 mb-3"),
                            html.Div(id='card-dados-pico', className="col-md-6 col-lg-4 mb-3"),
                            html.Div(id='card-tensao-corrente-unificado', className="col-md-8 col-lg-6 mb-3")
                        ]
                    )
                ])
            ]
        ),
        html.Div(html.P("Desenvolvido por Wanderley Oliveira e Gilberto Ferreira", className="text-center text-muted mt-4"))
    ]
)

# Layout da Página de Relatório de IA
ai_report_layout = html.Div(
    className="container mt-4",
    style={'backgroundColor': light_theme['background'], 'color': light_theme['text'], 'fontFamily': 'Poppins'},
    children=[
        html.Div(
            className="d-flex align-items-center justify-content-center p-4 rounded-3 text-white",
            style={'backgroundColor': light_theme['header_bg']},
            children=[html.H1("Relatório de Diagnóstico com IA")]
        ),
        html.Div(
            className="p-3",
            children=[dcc.Link(html.Button("Voltar para o Dashboard", className="btn btn-secondary"), href="/")]
        ),
        html.Div([
            dcc.DatePickerSingle(
                id='ia-seletor-data',
                min_date_allowed=PRIMEIRO_DIA_DADOS_CSV, max_date_allowed=ULTIMO_DIA_DADOS_CSV,
                initial_visible_month=DATA_INICIAL_VISUALIZACAO, date=DATA_INICIAL_VISUALIZACAO.isoformat(),
                display_format='DD/MM/YYYY',
            ),
        ], style={'textAlign': 'center', 'padding': '20px'}),
        dcc.Loading(id="loading-ai-report", children=[html.Div(id='ai-report-container')])
    ]
)


# --- Estrutura principal com roteamento ---
app.layout = html.Div(id='page-container', children=[
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

@app.callback(Output('page-content', 'children'), [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/ia-report':
        return ai_report_layout
    return dashboard_layout

# --- CALLBACKS DO DASHBOARD PRINCIPAL (CORRIGIDOS) ---

@app.callback(
    [Output('grafico-geracao-diaria', 'style'),
     Output('grafico-tensao-diaria', 'style'),
     Output('grafico-corrente-diaria', 'style'),
     Output('card-geracao-total', 'style'),
     Output('card-dados-pico', 'style'),
     Output('card-tensao-corrente-unificado', 'style')],
    [Input('btn-geracao', 'n_clicks'),
     Input('btn-tensao', 'n_clicks'),
     Input('btn-corrente', 'n_clicks')]
)
def toggle_graphs_and_cards(btn_geracao, btn_tensao, btn_corrente):
    ctx = dash.callback_context
    if not ctx.triggered:
        return ({'display': 'block'}, {'display': 'none'}, {'display': 'none'},
                {'display': 'block'}, {'display': 'block'}, {'display': 'none'})
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if button_id == 'btn-tensao':
        return ({'display': 'none'}, {'display': 'block'}, {'display': 'none'},
                {'display': 'none'}, {'display': 'none'}, {'display': 'block'})
    elif button_id == 'btn-corrente':
        return ({'display': 'none'}, {'display': 'none'}, {'display': 'block'},
                {'display': 'none'}, {'display': 'none'}, {'display': 'block'})
    else: 
        return ({'display': 'block'}, {'display': 'none'}, {'display': 'none'},
                {'display': 'block'}, {'display': 'block'}, {'display': 'none'})

@app.callback(
    [Output('card-geracao-total', 'children'),
     Output('card-dados-pico', 'children'),
     Output('card-tensao-corrente-unificado', 'children'),
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
        
        fig_geracao = go.Figure(data=go.Scatter(x=df_dia['DateTime'], y=df_dia['Dem_Ativa'], mode='lines', fill='tozeroy', line={'color': 'green'})).update_layout(
            title={"text": "Potência Ativa (kW)", "x": 0.5}, paper_bgcolor=light_theme['graph_bg'], plot_bgcolor=light_theme['graph_plot_bg'], font_color=light_theme['text']
        )
        
        fig_tensao = go.Figure().add_traces([
            go.Scatter(x=df_dia['DateTime'], y=df_dia['Tensao_L1'], name='Tensão L1', line={'color': '#FF8C00'}),
            go.Scatter(x=df_dia['DateTime'], y=df_dia['Tensao_L2'], name='Tensão L2', line={'color': '#FFA500'}),
            go.Scatter(x=df_dia['DateTime'], y=df_dia['Tensao_L3'], name='Tensão L3', line={'color': '#FFD700'})
        ]).update_layout(
            title={"text": "Tensão por Fase (V)", "x": 0.5}, paper_bgcolor=light_theme['graph_bg'], plot_bgcolor=light_theme['graph_plot_bg'], font_color=light_theme['text']
        )
        
        fig_corrente = go.Figure().add_traces([
            go.Scatter(x=df_dia['DateTime'], y=df_dia['Corrente_L1'], name='Corrente L1', line={'color': '#800080'}),
            go.Scatter(x=df_dia['DateTime'], y=df_dia['Corrente_L2'], name='Corrente L2', line={'color': '#9400D3'}),
            go.Scatter(x=df_dia['DateTime'], y=df_dia['Corrente_L3'], name='Corrente L3', line={'color': '#BA55D3'})
        ]).update_layout(
            title={"text": "Corrente por Fase (A)", "x": 0.5}, paper_bgcolor=light_theme['graph_bg'], plot_bgcolor=light_theme['graph_plot_bg'], font_color=light_theme['text']
        )

        pico = response['dados_pico_dia']
        
        card_geracao_children = html.Div([
            html.H5("Energia Gerada", style={'color': '#007BFF'}),
            html.H2(f"{response['geracao_total_dia_kwh']:.2f} kWh", style={'fontWeight': 'bold'})
        ], style=card_info_style)
        
        card_pico_children = html.Div([
            html.H5("Pico do Dia", style={'color': '#007BFF'}),
            html.H2(f"{pico.get('Dem_Ativa', 0):.2f} kW", style={'fontWeight': 'bold'}),
            html.P(f"às {pd.to_datetime(pico.get('timestamp_pico')).strftime('%H:%M')}" if pico.get('timestamp_pico') else "N/A")
        ], style=card_info_style)
        
        card_unificado_children = html.Div([
            html.Div([
                html.H5("Tensão no Pico", style={'color': 'orange'}),
                html.P(f"L1: {pico.get('Tensao_L1', 0):.1f}V"),
                html.P(f"L2: {pico.get('Tensao_L2', 0):.1f}V"),
                html.P(f"L3: {pico.get('Tensao_L3', 0):.1f}V"),
            ], style={'display': 'inline-block', 'width': '49%'}),
            html.Div([
                html.H5("Corrente no Pico", style={'color': 'purple'}),
                html.P(f"L1: {pico.get('Corrente_L1', 0):.1f}A"),
                html.P(f"L2: {pico.get('Corrente_L2', 0):.1f}A"),
                html.P(f"L3: {pico.get('Corrente_L3', 0):.1f}A"),
            ], style={'display': 'inline-block', 'width': '49%'})
        ], style=card_unificado_style)

        return card_geracao_children, card_pico_children, card_unificado_children, fig_geracao, fig_tensao, fig_corrente
    except Exception as e:
        fig_vazia = go.Figure().update_layout(title_text=f"Erro: {e}")
        empty_card = html.Div([html.P(f"Erro ao carregar dados: {e}")], style=card_info_style)
        return empty_card, empty_card, empty_card, fig_vazia, fig_vazia, fig_vazia

# --- CALLBACK DA PÁGINA DE IA (CORRIGIDO E COMPLETO) ---
@app.callback(
    Output('ai-report-container', 'children'),
    [Input('ia-seletor-data', 'date')]
)
def gerar_relatorio_ia(data_selecionada_str):
    if not data_selecionada_str:
        return html.P("Selecione uma data para a análise.", style={'textAlign': 'center', 'marginTop': '20px'})


    url = f"{API_URL_BASE}?data={data_selecionada_str}"
    try:
        response = requests.get(url, timeout=20).json()
        if "erro" in response: raise Exception(response["erro"])
       
        relatorio_data = pd.DataFrame(response.get('relatorio_ia', []))
       
        if relatorio_data.empty:
            return html.Div([
                html.H5("Sistema Estável", style={'color': 'green'}),
                html.P("Nenhuma ocorrência de risco foi prevista pela IA.")
            ], style={'textAlign': 'center', 'padding': '20px', 'backgroundColor': '#e9f5e9', 'borderRadius': '10px'})


        # Separa os dados em tabelas críticas e precárias
        critical_alarms = relatorio_data[relatorio_data['Previsao_Classe_Tensao'] == 'Crítica'].to_dict('records')
        precarious_alarms = relatorio_data[relatorio_data['Previsao_Classe_Tensao'] == 'Precária'].to_dict('records')


        children = []


        # Tabela de alarmes críticos
        critical_table = html.Div([
            html.H4("Alarmes Críticos", style={'textAlign': 'center', 'marginTop': '20px', 'color': '#FF4136'}),
            dash_table.DataTable(
                columns=[
                    {'name': 'Horário', 'id': 'Horario'},
                    {'name': 'Classe Prevista', 'id': 'Previsao_Classe_Tensao'},
                    {'name': 'Sugestão da IA', 'id': 'Sugestao'},
                ],
                data=critical_alarms,
                style_cell={'whiteSpace': 'normal', 'height': 'auto', 'minWidth': '100px', 'overflow': 'hidden', 'textOverflow': 'ellipsis', 'color': 'black', 'backgroundColor': 'white', 'textAlign': 'left'},
                style_data_conditional=[
                    {'if': {'filter_query': '{Previsao_Classe_Tensao} = "Crítica"'}, 'backgroundColor': light_theme['critical_color']},
                ],
                style_header={'backgroundColor': light_theme['critical_color'], 'color': 'black', 'fontWeight': 'bold'},
                style_table={'overflowY': 'auto', 'height': '400px', 'overflowX': 'auto', 'border': '1px solid #e0e0e0', 'borderRadius': '10px', 'boxShadow': '0 4px 8px rgba(0,0,0,0.1)'}
            )
        ], style={'padding': '10px'})


        # Tabela de alarmes precários
        precarious_table = html.Div([
            html.H4("Alarmes Precários", style={'textAlign': 'center', 'marginTop': '20px', 'color': '#FFD700'}),
            dash_table.DataTable(
                columns=[
                    {'name': 'Horário', 'id': 'Horario'},
                    {'name': 'Classe Prevista', 'id': 'Previsao_Classe_Tensao'},
                    {'name': 'Sugestão da IA', 'id': 'Sugestao'},
                ],
                data=precarious_alarms,
                style_cell={'whiteSpace': 'normal', 'height': 'auto', 'minWidth': '100px', 'overflow': 'hidden', 'textOverflow': 'ellipsis', 'color': 'black', 'backgroundColor': 'white', 'textAlign': 'left'},
                style_data_conditional=[
                    {'if': {'filter_query': '{Previsao_Classe_Tensao} = "Precária"'}, 'backgroundColor': light_theme['precarious_color']},
                ],
                style_header={'backgroundColor': light_theme['precarious_color'], 'color': 'black', 'fontWeight': 'bold'},
                style_table={'overflowY': 'auto', 'height': '400px', 'overflowX': 'auto', 'border': '1px solid #e0e0e0', 'borderRadius': '10px', 'boxShadow': '0 4px 8px rgba(0,0,0,0.1)'}
            )
        ], style={'padding': '10px'})
       
        # Layout de duas colunas lado a lado
        children = html.Div(
            className="row justify-content-center",
            children=[
                html.Div(className="col-lg-6 col-md-12 mb-3", children=critical_table) if critical_alarms else None,
                html.Div(className="col-lg-6 col-md-12 mb-3", children=precarious_table) if precarious_alarms else None,
                html.Div(
                    className="col-12 text-center",
                    children=[
                        html.Div(
                            [
                                html.H5("Sistema Estável", style={'color': 'green'}),
                                html.P("Nenhuma ocorrência de risco foi prevista pela IA.")
                            ],
                            style={'textAlign': 'center', 'padding': '20px', 'backgroundColor': '#e9f5e9', 'borderRadius': '10px'}
                        )
                    ]
                ) if not critical_alarms and not precarious_alarms else None
            ]
        )
           
        return children


    except Exception as e:
        return html.P(f"Erro ao carregar a análise da IA: {e}", style={'color': 'red', 'textAlign': 'center', 'marginTop': '20px'})

if __name__ == '__main__':
    app.run(debug=True, port=8050)
