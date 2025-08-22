import unittest
from app import app

class TestAPI(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        app.testing = True

    def test_obter_dados(self):
        # Testa a rota passando um parâmetro via query string
        response = self.client.get("/api/dados-usina?usina=Teste")
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()