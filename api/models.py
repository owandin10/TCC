class Usina:
    def __init__(self, nome, energia_gerada, consumo, status):
        self.nome = nome
        self.energia_gerada = energia_gerada
        self.consumo = consumo
        self.status = status

    def to_dict(self):
        return {
            "nome": self.nome,
            "energia_gerada": self.energia_gerada,
            "consumo": self.consumo,
            "status": self.status
        }