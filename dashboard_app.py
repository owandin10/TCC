print("DEBUG: Iniciando dashboard_app.py") # ESTA É A PRIMEIRA LINHA EXECUTÁVEL

import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import requests
import pandas as pd
import plotly.express as px

print("DEBUG: Importações concluídas")

API_URL = "http://127.0.0.1:5000/api/dados-usina"

print(f"DEBUG: API_URL definida como: {API_URL}")

app = dash.Dash(__name__, external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css']) # CORRIGIDO: _name para _name_
app.title = "Monitoramento Inteligente de Usina Solar"

print("DEBUG: Instância da app Dash criada")

# Layout da aplicação Dash
app.layout = html.Div(children=[
    html.H1(
        children="Dashboard de Monitoramento da Usina Solar",
        style={'textAlign': 'center', 'color': '#007BFF'}
    ),
    html.Div(id='info-usina-geral', style={'padding': '20px', 'border': '1px solid #ddd', 'borderRadius': '5px', 'marginBottom': '20px'}),
    dcc.Interval(
        id='intervalo-atualizacao-dados',
        interval=5*1000,
        n_intervals=0
    ),
    html.Div([
        html.H3("Histórico de Geração (kW)"),
        dcc.Graph(id='grafico-historico-geracao')
    ], style={'width': '70%', 'display': 'inline-block', 'verticalAlign': 'top', 'padding': '10px'}),
    html.Div([
        html.H3("Alarmes Ativos"),
        html.Div(id='lista-alarmes-ativos')
    ], style={'width': '28%', 'display': 'inline-block', 'verticalAlign': 'top', 'padding': '10px', 'borderLeft': '1px solid #eee'})
])

print("DEBUG: Layout da app definido")

# Callback
@app.callback(
    [Output('info-usina-geral', 'children'),
     Output('grafico-historico-geracao', 'figure'),
     Output('lista-alarmes-ativos', 'children')],
    [Input('intervalo-atualizacao-dados', 'n_intervals')]
)
def atualizar_dados_da_interface(n):
    print(f"DEBUG: Callback 'atualizar_dados_da_interface' chamada com n_intervals={n}")
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        dados_usina = response.json()

        if "erro" in dados_usina:
            info_geral_html = html.P(f"Erro ao buscar dados: {dados_usina['erro']}")
            fig_vazia = {}
            alarmes_html = html.P("Não foi possível carregar os alarmes.")
            return info_geral_html, fig_vazia, alarmes_html

        info_geral_html = html.Div([
            html.H4(f"Nome: {dados_usina.get('nome', 'N/D')}"),
            html.P(f"Localização: {dados_usina.get('localizacao', 'N/D')}"),
            html.P(f"Status: {dados_usina.get('status_operacional', 'N/D')}"),
            html.P(f"Última Atualização: {dados_usina.get('ultima_atualizacao', 'N/D')}"),
            html.Hr(),
            html.H5("Dados Atuais:"),
            html.P(f"Geração: {dados_usina.get('dados_atuais', {}).get('energia_gerada_kw', 'N/D')} kW"),
            html.P(f"Irradiação Solar: {dados_usina.get('dados_atuais', {}).get('irradiacao_solar_w_m2', 'N/D')} W/m²"),
            html.P(f"Temperatura dos Módulos: {dados_usina.get('dados_atuais', {}).get('temperatura_modulos_c', 'N/D')} °C"),
        ])

        leituras_historicas = dados_usina.get('leituras_historicas', [])
        if leituras_historicas:
            df_historico = pd.DataFrame(leituras_historicas)
            df_historico['timestamp'] = pd.to_datetime(df_historico['timestamp'])
            fig_historico = px.line(
                df_historico,
                x='timestamp',
                y='energia_gerada_kw',
                title="Energia Gerada (kW) vs. Tempo",
                markers=True
            )
            fig_historico.update_layout(xaxis_title="Data e Hora", yaxis_title="Energia Gerada (kW)")
        else:
            fig_historico = {}

        alarmes_ativos = dados_usina.get('alarmes_ativos', [])
        if alarmes_ativos:
            lista_items_alarme = []
            for alarme in alarmes_ativos:
                lista_items_alarme.append(html.Div([
                    html.H5(f"ID: {alarme.get('id_alarme', 'N/D')}", style={'color': 'red' if alarme.get('severidade') == 'Alta' else 'orange'}),
                    html.P(f"Descrição: {alarme.get('descricao', 'N/D')}"),
                    html.P(f"Severidade: {alarme.get('severidade', 'N/D')}"),
                    html.P(f"Timestamp: {alarme.get('timestamp', 'N/D')}"),
                    html.Hr()
                ], style={'border': '1px solid #f8d7da', 'padding': '10px', 'marginBottom': '10px', 'borderRadius': '5px'}))
            alarmes_html = html.Div(lista_items_alarme)
        else:
            alarmes_html = html.P("Nenhum alarme ativo no momento.")

        return info_geral_html, fig_historico, alarmes_html

    except requests.exceptions.RequestException as e:
        print(f"DEBUG: Erro de conexão com a API na callback: {e}")
        erro_conexao_html = html.P(f"Não foi possível conectar à API de dados: {API_URL}. Verifique se o servidor Flask está rodando.")
        return erro_conexao_html, {}, html.P("Erro ao carregar alarmes.")
    except Exception as e:
        print(f"DEBUG: Erro inesperado na callback: {e}")
        erro_inesperado_html = html.P(f"Ocorreu um erro inesperado: {str(e)}")
        return erro_inesperado_html, {}, html.P("Erro ao carregar alarmes.")

print("DEBUG: Definição da callback concluída")

if __name__ == '__main__':
    print("DEBUG: Entrando no bloco if __name__ == '__main__'")
    app.run_server(debug=True, port=8050)
    print("DEBUG: app.run_server() foi chamado") # Pode não ser alcançada se o servidor bloquear