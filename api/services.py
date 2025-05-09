import random
from datetime import datetime, timedelta

def _gerar_dados_simulados_usina():
    dados_base = {
        "nome": "Usina Solar Gerada Dinamicamente",
        "localizacao": "Trindade, GO",
        "capacidade_instalada_kw": 200.0,
        "status_operacional": "Operacional",
        "ultima_atualizacao": datetime.now().isoformat() + "Z",
    }

    dados_base["dados_atuais"] = {
        "energia_gerada_kw": round(random.uniform(50, 180), 2),
        "irradiacao_solar_w_m2": random.randint(300, 1000),
        "temperatura_modulos_c": round(random.uniform(25, 60), 1),
        "consumo_interno_kw": round(random.uniform(1, 10), 2),
    }
    dados_base["dados_atuais"]["energia_injetada_rede_kw"] = round(
        dados_base["dados_atuais"]["energia_gerada_kw"] - dados_base["dados_atuais"]["consumo_interno_kw"], 2
    )
    if dados_base["dados_atuais"]["energia_injetada_rede_kw"] < 0:
        dados_base["dados_atuais"]["energia_injetada_rede_kw"] = 0

    dados_base["alarmes_ativos"] = []
    if random.random() < 0.2:
        dados_base["alarmes_ativos"].append({
            "id_alarme": f"ALM{random.randint(100, 199)}",
            "descricao": random.choice([
                "Baixo rendimento no Inversor X",
                "Falha de comunicação com String Y",
                "Temperatura elevada no painel Z"
            ]),
            "severidade": random.choice(["Baixa", "Média", "Alta"]),
            "timestamp": (datetime.now() - timedelta(minutes=random.randint(5, 60))).isoformat() + "Z"
        })

    dados_base["leituras_historicas"] = []
    hora_atual = datetime.now()
    for i in range(3):
        timestamp_historico = hora_atual - timedelta(hours=i+1)
        dados_base["leituras_historicas"].append({
            "timestamp": timestamp_historico.isoformat() + "Z",
            "energia_gerada_kw": round(random.uniform(30, 170), 2),
            "irradiacao_solar_w_m2": random.randint(200, 900)
        })

    return dados_base

def obter_dados_api(nome_usina):
    try:
        dados_simulados = _gerar_dados_simulados_usina()
        return dados_simulados
    except Exception as e:
        return {"erro": f"Um erro inesperado ocorreu ao gerar dados simulados: {str(e)}"}