import requests
from config.settings import API_KEY, URL_BASE

def obter_dados_api(nome_usina):
    try:
        url = f"{URL_BASE}?usina={nome_usina}&apikey={API_KEY}"
        response = requests.get(url)
        response.raise_for_status()  # Levanta exceções para status de erro HTTP
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"erro": str(e)}