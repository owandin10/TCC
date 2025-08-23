from flask import Flask
from flask_cors import CORS

# Importamos o nosso blueprint que contém as rotas da API
from api.routes import main_bp

# --- 1. Criação e Configuração da Aplicação ---

def create_app():
    """
    Cria e configura uma instância da aplicação Flask.
    Esta é uma factory function, uma boa prática para aplicações Flask.
    """
    # Cria a instância da aplicação
    app = Flask(__name__)
    
    # ATIVAÇÃO DO CORS: A linha mais importante para a comunicação funcionar.
    # Isto permite que o seu dashboard (ex: http://localhost:8050)
    # faça requisições para este servidor (http://localhost:5000).
    CORS(app)
    
    # Registamos o blueprint que contém as nossas rotas.
    # Todas as rotas definidas em 'main_bp' (em api/routes.py)
    # agora fazem parte da nossa aplicação.
    app.register_blueprint(main_bp)
    
    print("DEBUG APP: Aplicação Flask criada e rotas registadas.")
    return app


# --- 2. Bloco de Execução Principal ---

if __name__ == '__main__':
    # Criamos a nossa aplicação chamando a factory function
    app = create_app()
    
    print("DEBUG APP: A iniciar o servidor Flask...")
    
    # Executa a aplicação.
    # 'host="0.0.0.0"' permite que o servidor seja acessível na sua rede.
    # 'debug=True' ativa o modo de depuração para vermos os erros facilmente.
    app.run(host='0.0.0.0', port=5000, debug=True)