import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import requests
import pandas as pd
# MUDANÇA: Vamos usar a base do Plotly para mais robustez
import plotly.graph_objects as go
from datetime import date

# --- CONFIGURAÇÃO ---
API_URL_BASE = "http://127.0.0.1:5000/api/dados-usina" 

app = dash.Dash(__name__, external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'])
app.title = "Monitoramento Detalhado da Usina Solar IFG"

# ------ AJUSTE AS DATAS AQUI CONFORME SEU CSV ------
PRIMEIRO_DIA_DADOS_CSV = date(2025, 1, 13) 
DATA_INICIAL_VISUALIZACAO = date(2025, 1, 13)
ULTIMO_DIA_DADOS_CSV = date(2025, 5, 20) 
# -----------------------------------------------

# --- Layout do Dashboard ---
app.layout = html.Div(children=[
    html.H1(
        children="Dashboard de Monitoramento da Usina Solar IFG",
        style={'textAlign': 'center', 'color': '#007BFF', 'marginBottom': '30px'}
    ),
    html.Div([
        html.Label("Selecione uma Data:", style={'marginRight': '10px', 'fontWeight': 'bold'}),
        dcc.DatePickerSingle(
            id='seletor-data-diario',
            min_date_allowed=PRIMEIRO_DIA_DADOS_CSV, 
            max_date_allowed=ULTIMO_DIA_DADOS_CSV, 
            initial_visible_month=DATA_INICIAL_VISUALIZACAO, 
            date=DATA_INICIAL_VISUALIZACAO.isoformat(), 
            display_format='DD/MM/YYYY',
            style={'width': '180px'}
        ),
    ], style={'marginBottom': '20px', 'textAlign': 'center', 'padding': '10px'}),
    html.Div([
        html.Div(dcc.Graph(id='grafico-geracao-diaria'), style={'width': '49%', 'display': 'inline-block'}),
        html.Div(dcc.Graph(id='grafico-tensao-diaria'), style={'width': '49%', 'display': 'inline-block'})
    ], style={'width': '95%', 'margin': 'auto', 'display': 'flex', 'justifyContent': 'space-between'}),
    html.Hr(),
    html.Div([
        html.H3("Informações Gerais (Última Leitura do CSV)", style={'textAlign': 'center', 'color': '#555'}),
        html.Div(id='info-usina-geral', style={'padding': '15px', 'border': '1px solid #ddd', 'borderRadius': '5px', 'backgroundColor': '#f9f9f9', 'maxWidth': '600px', 'margin': 'auto'}),
    ], style={'width': '90%', 'margin': '20px auto'}),
])

# --- Callback Principal (Lógica do Dashboard) ---
@app.callback(
    [Output('info-usina-geral', 'children'),
     Output('grafico-geracao-diaria', 'figure'),
     Output('grafico-tensao-diaria', 'figure')],
    [Input('seletor-data-diario', 'date')]
)
def atualizar_interface_completa(data_selecionada_str):
    url_api_com_data = f"{API_URL_BASE}?data={data_selecionada_str}" if data_selecionada_str else API_URL_BASE
    
    default_figure = go.Figure()
    default_figure.update_layout(title_text="Aguardando dados...", xaxis={'visible': False}, yaxis={'visible': False})

    try:
        response = requests.get(url_api_com_data, timeout=10)
        response.raise_for_status()
        dados_usina = response.json()

        if "erro" in dados_usina:
            error_fig = go.Figure()
            error_fig.update_layout(title_text=f"Erro da API: {dados_usina['erro']}")
            return html.P(f"Erro da API: {dados_usina['erro']}"), error_fig, error_fig

        dados_gerais_backend = dados_usina.get("dados_atuais_geral", {})
        info_geral_html = html.Div([
            html.H4(f"Usina: {dados_usina.get('nome', 'N/D')}", style={'marginBottom': '5px'}),
            html.P(f"Local: {dados_usina.get('localizacao', 'N/D')}"),
            html.P(f"Timestamp da Última Leitura no CSV: {dados_usina.get('ultima_atualizacao_geral', 'N/D')}"),
            html.H5("Detalhes da Última Leitura:"),
            html.P(f"Geração Ativa (kW): {dados_gerais_backend.get('energia_gerada_kw', 'N/D')}"),
            html.P(f"Tensão (V): {dados_gerais_backend.get('tensao_v', 'N/D')}"),
        ])

        leituras_dia = dados_usina.get('leituras_dia_selecionado', [])
        data_para_titulo = data_selecionada_str if data_selecionada_str else "Dia Mais Recente"
        
        fig_geracao = go.Figure()
        fig_tensao = go.Figure()

        if dados_usina.get("erro_dia_selecionado"):
            erro_dia_msg = dados_usina.get("erro_dia_selecionado")
            fig_geracao.update_layout(title_text=erro_dia_msg)
            fig_tensao.update_layout(title_text=erro_dia_msg)
        elif leituras_dia:
            df_dia = pd.DataFrame(leituras_dia)
            
            # --- CORREÇÃO DEFINITIVA ---
            # 1. Criar uma coluna de datetime real, combinando a data com a hora.
            #    Isto remove qualquer ambiguidade sobre a ordem dos dados.
            if data_selecionada_str:
                df_dia['timestamp_real'] = pd.to_datetime(
                    data_selecionada_str + ' ' + df_dia['hora_minuto'], 
                    errors='coerce'
                )
            else: # Fallback se nenhuma data for selecionada (pega do primeiro registro)
                df_dia['timestamp_real'] = pd.to_datetime(df_dia['timestamp'], errors='coerce')

            # 2. Garantir que as colunas de dados são numéricas
            df_dia['energia_gerada_kw'] = pd.to_numeric(df_dia['energia_gerada_kw'], errors='coerce')
            df_dia['tensao_v'] = pd.to_numeric(df_dia['tensao_v'], errors='coerce')
            
            # 3. Remover linhas onde a conversão falhou e ordenar pela nova coluna de timestamp
            df_dia.dropna(subset=['timestamp_real', 'energia_gerada_kw', 'tensao_v'], inplace=True)
            df_dia = df_dia.sort_values(by='timestamp_real')

            # Gráfico de Geração
            fig_geracao.add_trace(go.Scatter(
                x=df_dia['timestamp_real'], # Usar a nova coluna de timestamp
                y=df_dia['energia_gerada_kw'],
                mode='lines',
                fill='tozeroy',
                line=dict(color='deepskyblue')
            ))
            fig_geracao.update_layout(
                title_text=f"Geração Ativa (kW) - {data_para_titulo}",
                xaxis_title="Hora do Dia",
                yaxis_title="Geração Ativa (kW)"
                # Não é mais necessário forçar o tipo de eixo para 'category'
            )

            # Gráfico de Tensão
            fig_tensao.add_trace(go.Scatter(
                x=df_dia['timestamp_real'], # Usar a nova coluna de timestamp
                y=df_dia['tensao_v'],
                mode='lines',
                line=dict(color='darkorange')
            ))
            fig_tensao.update_layout(
                title_text=f"Tensão (V) - {data_para_titulo}",
                xaxis_title="Hora do Dia",
                yaxis_title="Tensão (V)"
            )
        else:
            msg_sem_dados = f"Nenhum dado encontrado para {data_para_titulo}"
            fig_geracao.update_layout(title_text=msg_sem_dados)
            fig_tensao.update_layout(title_text=msg_sem_dados)

        return info_geral_html, fig_geracao, fig_tensao

    except requests.exceptions.RequestException:
        msg = f"API Indisponível ou não encontrada. Verifique se o servidor Flask está rodando em {API_URL_BASE}"
        error_fig = go.Figure()
        error_fig.update_layout(title_text=msg)
        return html.P(msg), error_fig, error_fig
    except Exception as e:
        import traceback
        traceback.print_exc()
        msg = f"Ocorreu um erro inesperado no Dashboard: {str(e)}"
        error_fig = go.Figure()
        error_fig.update_layout(title_text=msg)
        return html.P(msg), error_fig, error_fig

if __name__ == '__main__':
    app.run_server(debug=True, port=8050)