class Vendedor():
    def __init__(self,nome):
        self.nome = nome
        self.vendas = 0

    def vendeu(self, vendas):
        self.vendas = vendas

    def bateu_meta(self, meta):
        if self.vendas > meta:
            print("O vendedor {0}, bateu a meta {1}".format(self.nome, meta))
        else:
            print("O vendedor {0}, não bateu  meta {1}".format(self.nome, meta))