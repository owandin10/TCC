from flask import Flask
from api.routes import api_blueprint # Importe o blueprint

app = Flask(__name__)

app.register_blueprint(api_blueprint, url_prefix="/api") # << MODIFICADO: Adicionado url_prefix="/api"

@app.route("/")
def home():
  
    return "Flask está rodando corretamente e o blueprint da API deve estar acessível em /api/dados-usina!"

if __name__ == "_main_":
    # Para rodar com 'python app.py'
    app.run(debug=True)