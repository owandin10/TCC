from flask import Blueprint, jsonify, request
from api.services import obter_dados_api

api_blueprint = Blueprint("api", __name__)

@api_blueprint.route("/dados-usina", methods=["GET"])
def obter_dados():
    # Recebe o nome da usina via query string, com valor padrão se não for informado.
    nome_usina = request.args.get("usina", default="UsinaTeste")
    dados = obter_dados_api(nome_usina)
    return jsonify(dados)