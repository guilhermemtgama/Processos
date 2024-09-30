# Criar uma classe para clientes da netflix
from logging import exception


class Cliente:
    def __init__(self, nome, email, plano):
        self.nome = nome
        self.email = email
        self.lista_Planos = ["Basic", "Premium"]
        if plano in self.lista_Planos:
            self.plano = plano
        else:
            raise exception("Plano invalido")

    def mudar_Plano(self, novo_Plano):
        if novo_Plano in self.lista_Planos:
            self.plano = novo_Plano
        else:
            print("Plano invalido")

    def ver_filme(self, filme, plano_filme):
        if self.plano == plano_filme:
            print(f"Ver o filme {filme}")
        elif self.plano == "Premium":
            print(f"Ver o filme {filme}")
        elif self.plano == "Basic" and plano_filme == "Premium":
            print("Faça o upgrade para o plano premium para ver esse filme")
        else:
            print("Plano Invalido")


cliente = Cliente("Guilherme", "guilherme.mtgama@outlook.com", "Basic")

print(cliente.nome)
print(cliente.plano)
cliente.ver_filme("Rei Leão", "Premium")
cliente.mudar_Plano("Premium")
cliente.ver_filme("Rei Leão", "Premium")

