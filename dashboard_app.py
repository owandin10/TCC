import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import requests
import pandas as pd
<<<<<<< HEAD
=======
# MUDANÇA: Vamos usar a base do Plotly para mais robustez
>>>>>>> 75bda8578b4454d271a0481bea29f97f8b8821c7
import plotly.graph_objects as go
from datetime import date

# --- CONFIGURAÇÃO ---
API_URL_BASE = "http://127.0.0.1:5000/api/dados-usina" 

app = dash.Dash(__name__, external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'])
app.title = "Monitoramento Detalhado da Usina Solar IFG"

# ------ AJUSTE AS DATAS AQUI CONFORME SEU CSV ------
<<<<<<< HEAD
PRIMEIRO_DIA_DADOS_CSV = date(2025, 1, 4) 
DATA_INICIAL_VISUALIZACAO = date(2025, 1, 23)
=======
PRIMEIRO_DIA_DADOS_CSV = date(2025, 1, 13) 
DATA_INICIAL_VISUALIZACAO = date(2025, 1, 13)
>>>>>>> 75bda8578b4454d271a0481bea29f97f8b8821c7
ULTIMO_DIA_DADOS_CSV = date(2025, 5, 20) 
# -----------------------------------------------

# --- Layout do Dashboard ---
app.layout = html.Div(children=[
    html.H1(
<<<<<<< HEAD
        children="Dashboard de Monitoramento da Usina Solar IFG (Trifásico)",
=======
        children="Dashboard de Monitoramento da Usina Solar IFG",
>>>>>>> 75bda8578b4454d271a0481bea29f97f8b8821c7
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
<<<<<<< HEAD
    
    html.Div([
        html.Div(dcc.Graph(id='grafico-geracao-diaria'), style={'width': '33%', 'display': 'inline-block', 'padding': '0 10px'}),
        html.Div(dcc.Graph(id='grafico-tensao-diaria'), style={'width': '33%', 'display': 'inline-block', 'padding': '0 10px'}),
        html.Div(dcc.Graph(id='grafico-corrente-diaria'), style={'width': '33%', 'display': 'inline-block', 'padding': '0 10px'})
    ], style={'width': '98%', 'margin': 'auto', 'display': 'flex', 'justifyContent': 'center'}),
    
    html.Hr(),
    
    html.Div([
        html.H3("Resumo do Dia Selecionado", style={'textAlign': 'center', 'color': '#555'}),
        html.Div(id='info-usina-geral', style={'padding': '20px', 'border': '1px solid #ddd', 'borderRadius': '5px', 'backgroundColor': '#f9f9f9', 'maxWidth': '800px', 'margin': 'auto'}),
=======
    html.Div([
        html.Div(dcc.Graph(id='grafico-geracao-diaria'), style={'width': '49%', 'display': 'inline-block'}),
        html.Div(dcc.Graph(id='grafico-tensao-diaria'), style={'width': '49%', 'display': 'inline-block'})
    ], style={'width': '95%', 'margin': 'auto', 'display': 'flex', 'justifyContent': 'space-between'}),
    html.Hr(),
    html.Div([
        html.H3("Informações Gerais (Última Leitura do CSV)", style={'textAlign': 'center', 'color': '#555'}),
        html.Div(id='info-usina-geral', style={'padding': '15px', 'border': '1px solid #ddd', 'borderRadius': '5px', 'backgroundColor': '#f9f9f9', 'maxWidth': '600px', 'margin': 'auto'}),
>>>>>>> 75bda8578b4454d271a0481bea29f97f8b8821c7
    ], style={'width': '90%', 'margin': '20px auto'}),
])

# --- Callback Principal (Lógica do Dashboard) ---
@app.callback(
    [Output('info-usina-geral', 'children'),
     Output('grafico-geracao-diaria', 'figure'),
<<<<<<< HEAD
     Output('grafico-tensao-diaria', 'figure'),
     Output('grafico-corrente-diaria', 'figure')],
=======
     Output('grafico-tensao-diaria', 'figure')],
>>>>>>> 75bda8578b4454d271a0481bea29f97f8b8821c7
    [Input('seletor-data-diario', 'date')]
)
def atualizar_interface_completa(data_selecionada_str):
    url_api_com_data = f"{API_URL_BASE}?data={data_selecionada_str}" if data_selecionada_str else API_URL_BASE
    
<<<<<<< HEAD
    default_figure = go.Figure().update_layout(title_text="Aguardando dados...", xaxis={'visible': False}, yaxis={'visible': False})
    
=======
    default_figure = go.Figure()
    default_figure.update_layout(title_text="Aguardando dados...", xaxis={'visible': False}, yaxis={'visible': False})

>>>>>>> 75bda8578b4454d271a0481bea29f97f8b8821c7
    try:
        response = requests.get(url_api_com_data, timeout=10)
        response.raise_for_status()
        dados_usina = response.json()

        if "erro" in dados_usina:
<<<<<<< HEAD
            error_msg = f"Erro da API: {dados_usina['erro']}"
            error_fig = go.Figure().update_layout(title_text=error_msg)
            return html.P(error_msg), error_fig, error_fig, error_fig

        dados_pico_dia = dados_usina.get("dados_pico_dia", {})
        
        if not dados_pico_dia:
             info_geral_html = html.P("Nenhum dado encontrado para a data selecionada.")
        else:
            # Formata o Fator de Carga para exibição em porcentagem
            try:
                fat_carga_valor = float(dados_pico_dia.get('Fat_Carga', 0))
                fat_carga_formatado = f"{fat_carga_valor:.2%}"
            except (ValueError, TypeError):
                fat_carga_formatado = "N/D"

            # NOVO: Formata a Geração Total do Dia
            try:
                geracao_total_kwh = float(dados_usina.get('geracao_total_dia_kwh', 0))
                geracao_total_formatado = f"{geracao_total_kwh:.2f} kWh"
            except (ValueError, TypeError):
                geracao_total_formatado = "N/D"

            info_geral_html = html.Div([
                # Div da Esquerda: Informações Gerais do Dia
                html.Div([
                    html.H4(f"Informações Gerais", style={'marginBottom': '10px'}),
                    html.P(f"Usina: {dados_usina.get('nome', 'N/D')}"),
                    html.P(f"Local: {dados_usina.get('localizacao', 'N/D')}"),
                    # Exibe a Geração Total do Dia de forma destacada
                    html.H5("Energia Gerada no Dia:", style={'marginTop': '15px'}),
                    html.P(geracao_total_formatado, style={'fontSize': '20px', 'fontWeight': 'bold', 'color': '#007BFF'}),
                ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'}),

                # Div da Direita: Detalhes do Pico de Geração
                html.Div([
                    html.H5("Dados no Momento do Pico de Potência:", style={'marginTop': '0', 'marginBottom': '10px'}),
                    html.P(f"Horário do Pico: {pd.to_datetime(dados_pico_dia.get('timestamp_pico')).strftime('%H:%M:%S')}"),
                    html.P(f"Potência Ativa: {dados_pico_dia.get('Dem_Ativa', 'N/D')} kW"),
                    html.P(f"Potência Reativa: {dados_pico_dia.get('Dem_Reat', 'N/D')} kVAr"),
                    html.P(f"Tensão (L1/L2/L3): {dados_pico_dia.get('Tensao_L1', 'N/D')}V / {dados_pico_dia.get('Tensao_L2', 'N/D')}V / {dados_pico_dia.get('Tensao_L3', 'N/D')}V"),
                    html.P(f"Corrente (L1/L2/L3): {dados_pico_dia.get('Corrente_L1', 'N/D')}A / {dados_pico_dia.get('Corrente_L2', 'N/D')}A / {dados_pico_dia.get('Corrente_L3', 'N/D')}A"),
                    html.P(f"Fator de Potência: {dados_pico_dia.get('Fat_Pot', 'N/D')}"),
                    html.P(f"Fator de Carga (Intervalo): {fat_carga_formatado}"),
                ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top', 'paddingLeft': '4%'})
            ])

        # ... (O resto da lógica para os gráficos permanece a mesma)
=======
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

>>>>>>> 75bda8578b4454d271a0481bea29f97f8b8821c7
        leituras_dia = dados_usina.get('leituras_dia_selecionado', [])
        data_para_titulo = data_selecionada_str if data_selecionada_str else "Dia Mais Recente"
        
        fig_geracao = go.Figure()
        fig_tensao = go.Figure()
<<<<<<< HEAD
        fig_corrente = go.Figure()
=======
>>>>>>> 75bda8578b4454d271a0481bea29f97f8b8821c7

        if dados_usina.get("erro_dia_selecionado"):
            erro_dia_msg = dados_usina.get("erro_dia_selecionado")
            fig_geracao.update_layout(title_text=erro_dia_msg)
            fig_tensao.update_layout(title_text=erro_dia_msg)
<<<<<<< HEAD
            fig_corrente.update_layout(title_text=erro_dia_msg)

        elif leituras_dia:
            df_dia = pd.DataFrame(leituras_dia)
            df_dia['DateTime'] = pd.to_datetime(df_dia['DateTime'], errors='coerce')
            
            colunas_para_converter = [
                'Dem_Ativa', 'Tensao_L1', 'Tensao_L2', 'Tensao_L3',
                'Corrente_L1', 'Corrente_L2', 'Corrente_L3'
            ]
            for col in colunas_para_converter:
                if col in df_dia.columns:
                    df_dia[col] = pd.to_numeric(df_dia[col], errors='coerce')
            
            df_dia.dropna(subset=['DateTime'] + colunas_para_converter, inplace=True)
            df_dia = df_dia.sort_values(by='DateTime')

            fig_geracao.add_trace(go.Scatter(x=df_dia['DateTime'], y=df_dia['Dem_Ativa'], mode='lines', fill='tozeroy', name='Geração', line=dict(color='deepskyblue')))
            fig_geracao.update_layout(title_text=f"Potência Ativa (kW) - {data_para_titulo}", xaxis_title="Hora do Dia", yaxis_title="Potência (kW)")

            fig_tensao.add_trace(go.Scatter(x=df_dia['DateTime'], y=df_dia['Tensao_L1'], mode='lines', name='Tensão L1', line=dict(color='red')))
            fig_tensao.add_trace(go.Scatter(x=df_dia['DateTime'], y=df_dia['Tensao_L2'], mode='lines', name='Tensão L2', line=dict(color='green')))
            fig_tensao.add_trace(go.Scatter(x=df_dia['DateTime'], y=df_dia['Tensao_L3'], mode='lines', name='Tensão L3', line=dict(color='blue')))
            fig_tensao.update_layout(title_text=f"Tensão por Fase (V) - {data_para_titulo}", xaxis_title="Hora do Dia", yaxis_title="Tensão (V)")

            fig_corrente.add_trace(go.Scatter(x=df_dia['DateTime'], y=df_dia['Corrente_L1'], mode='lines', name='Corrente L1', line=dict(color='red')))
            fig_corrente.add_trace(go.Scatter(x=df_dia['DateTime'], y=df_dia['Corrente_L2'], mode='lines', name='Corrente L2', line=dict(color='green')))
            fig_corrente.add_trace(go.Scatter(x=df_dia['DateTime'], y=df_dia['Corrente_L3'], mode='lines', name='Corrente L3', line=dict(color='blue')))
            fig_corrente.update_layout(title_text=f"Corrente por Fase (A) - {data_para_titulo}", xaxis_title="Hora do Dia", yaxis_title="Corrente (A)")

=======
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
>>>>>>> 75bda8578b4454d271a0481bea29f97f8b8821c7
        else:
            msg_sem_dados = f"Nenhum dado encontrado para {data_para_titulo}"
            fig_geracao.update_layout(title_text=msg_sem_dados)
            fig_tensao.update_layout(title_text=msg_sem_dados)
<<<<<<< HEAD
            fig_corrente.update_layout(title_text=msg_sem_dados)

        return info_geral_html, fig_geracao, fig_tensao, fig_corrente

    except requests.exceptions.RequestException:
        msg = f"API Indisponível. Verifique se o servidor Flask está rodando em {API_URL_BASE}"
        error_fig = go.Figure().update_layout(title_text=msg)
        return html.P(msg), error_fig, error_fig, error_fig
=======

        return info_geral_html, fig_geracao, fig_tensao

    except requests.exceptions.RequestException:
        msg = f"API Indisponível ou não encontrada. Verifique se o servidor Flask está rodando em {API_URL_BASE}"
        error_fig = go.Figure()
        error_fig.update_layout(title_text=msg)
        return html.P(msg), error_fig, error_fig
>>>>>>> 75bda8578b4454d271a0481bea29f97f8b8821c7
    except Exception as e:
        import traceback
        traceback.print_exc()
        msg = f"Ocorreu um erro inesperado no Dashboard: {str(e)}"
<<<<<<< HEAD
        error_fig = go.Figure().update_layout(title_text=msg)
        return html.P(msg), error_fig, error_fig, error_fig

if __name__ == '__main__':
    app.run(debug=True, port=8050)
=======
        error_fig = go.Figure()
        error_fig.update_layout(title_text=msg)
        return html.P(msg), error_fig, error_fig

if __name__ == '__main__':
    app.run_server(debug=True, port=8050)
>>>>>>> 75bda8578b4454d271a0481bea29f97f8b8821c7
