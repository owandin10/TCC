from flask import Blueprint, jsonify, request
# Importamos a função de lógica de negócio do nosso módulo de serviços
from .services import obter_dados_para_api

# Criamos um "Blueprint". É a forma organizada do Flask de agrupar rotas relacionadas.
# O primeiro argumento, 'api', é o nome do blueprint.
main_bp = Blueprint('main_bp', __name__)


@main_bp.route('/api/dados-usina', methods=['GET'])
def endpoint_dados_usina():
    """
    Este é o endpoint principal que o Dashboard Dash irá chamar.
    Ele recebe a data como um parâmetro na URL.
    """
    # Pega o parâmetro 'data' da URL (ex: ?data=2025-01-14)
    data_str = request.args.get('data')
    print(f"DEBUG ROUTES: Requisição recebida para data: {data_str}")
    
    # Chama a função do nosso serviço para obter os dados já formatados
    dados = obter_dados_para_api(data_str)
    
    # Retorna os dados como uma resposta JSON
    return jsonify(dados)