import pygame
import os
import random

tela_Largura = 500
tela_Altura = 800

imagem_Cano = pygame.transform.scale2x(pygame.image.load(os.path.join("FlappyBridImage","imgs", "pipe.png")))
imagem_Chao = pygame.transform.scale2x(pygame.image.load(os.path.join("FlappyBridImage","imgs", "base.png")))
imagem_Background = pygame.transform.scale2x(pygame.image.load(os.path.join("FlappyBridImage","imgs", "bg.png")))
imagens_Passaro = [pygame.transform.scale2x(pygame.image.load(os.path.join("FlappyBridImage","imgs", "bird1.png"))),
                   pygame.transform.scale2x(pygame.image.load(os.path.join("FlappyBridImage","imgs", "bird2.png"))),
                   pygame.transform.scale2x(pygame.image.load(os.path.join("FlappyBridImage","imgs", "bird3.png")))
                   ]
pygame.font.init()
fonte_Pontos = pygame.font.SysFont("Arial", 50)


class Passaro:
    IMGS = imagens_Passaro
    # animações da rotação
    rotacao_Max = 25
    velocidade_Rotacao = 20
    tempo_Animacao = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angulo = 0
        self.velocidade = 0
        self.altura = self.y
        self.tempo = 0
        self.contagem_Imagem = 0
        self.imagem = self.IMGS[0]

    def pular(self):
        self.velocidade = -10.5
        self.tempo = 0
        self.al = self.y

    def mover(self):
        self.tempo += 1
        deslocamento = 1.5 * (self.tempo**2) + self.velocidade * self.tempo
        if deslocamento > 16:
            deslocamento = 16
        elif deslocamento < 0:
            deslocamento -= 2

        self.y += deslocamento

        if deslocamento < 0 or self.y < (self.altura + 50):
            if self.angulo < self.rotacao_Max:
                self.angulo = self.rotacao_Max
        else:
            if self.angulo > -90:
                self.angulo -= self.velocidade_Rotacao
    # definir qual imagem do passaro vai usar
    def desenhar(self, tela):
        self.contagem_Imagem += 1
        if self.contagem_Imagem < self.tempo_Animacao:
            self.imagem = self.IMGS[0]
        elif self.contagem_Imagem < self.tempo_Animacao*2:
            self.imagem = self.IMGS[1]
        elif self.contagem_Imagem < self.tempo_Animacao*3:
            self.imagem = self.IMGS[2]
        elif self.contagem_Imagem < self.tempo_Animacao * 4:
            self.imagem = self.IMGS[1]
        elif self.contagem_Imagem >= self.tempo_Animacao * 4 +1:
            self.imagem = self.IMGS[0]
            self.contagem_Imagem = 0

        # se o passaro tiver caindo eu não vou bater asa
        if self.angulo <= -80:
            self.imagem = self.IMGS[1]
            self.contagem_Imagem = self.tempo_Animacao*2

        # desenhar a imagem
        imagem_Rotacionada = pygame.transform.rotate(self.imagem, self.angulo)
        pos_Centro_Imagem = self.imagem.get_rect(topleft = (self.x, self.y)).center
        retangulo = imagem_Rotacionada.get_rect(center = pos_Centro_Imagem)
        tela.blit(imagem_Rotacionada, retangulo.topleft)

    def get_mask(self):
        pygame.mask.from_surface(self.imagem)


class Cano:
    distancia = 200
    velocidade = 5

    def __init__(self,x):
        self.x = x
        self.altura = 0
        self.pos_Topo = 0
        self.pos_Base = 0
        self.cano_Topo = pygame.transform.flip(imagem_Cano, False, True)
        self. cano_Base = imagem_Cano
        self.passou = False
        self.definir_altura()

    def denir_altura(self):
        self.altura = random.randrange(50, 450)
        self.pos_Topo = self.altura - self.cano_Topo.get_height()
        self.pos_Base = self.altura + self.distancia

    def mover_Cano(self):
        self.x -= self.velocidade

    def desenhar(self,tela):
        tela.blit(self.cano_Topo, (self.x, self.pos_Topo))
        tela.blit(self.cano_Base, (self.x, self.pos_Base))

    def colidir(self, passaro):
        passaro_mask = passaro.get_mask()
        topo_mask = pygame.mask.from_surface(self.cano_Topo)
        base_mask = pygame.mask.from_surface(self.cano_Base)

        distancia_Topo = (self.x - passaro.x, self.pos_Topo - round(passaro.y))
        distancia_base = (self.x - passaro.x, self.pos_Base - round(passaro.y))

        topo_ponto = passaro_mask.overlap(topo_mask, distancia_Topo)
        base_ponto = passaro_mask.overlap(base_mask, distancia_base)

        if base_ponto or topo_ponto:
            return True
        else:
            return  False


class Chao:
    velocidade = 5
    largura = imagem_Chao.get_width()
    imagem = imagem_Chao

    def __init__(self, y):
        self.y = y
        self.x0 = 0
        self.x1 = self.largura

    def mover(self):
        self.x0-= self.velocidade
        self.x1 -= self.velocidade

        if self.x0 + self.largura < 0:
            self.x0 = self.x0 + self.largura
        if self.x1 + self.largura < 0:
            self.x1 = self.x1 + self.largura

    def desenhar(self, tela):
        tela.blit(self.imagem, (self.x0, self.y))
        tela.blit(self.imagem, (self.x1, self.y))


def denhar_tela(tela, passaros, canos, chao, pontos):
    tela.blit(imagem_Background, (0,0))
    for passaro in passaros:
        passaro.desenhar(tela)
    for cano in canos:
        cano.desenhar(tela)
    texto = fonte_Pontos.render(f"Pontuação: {pontos}", 1, (255, 255, 255))

    tela.blit(texto, (tela_Largura - 10 -texto.get_width(), 10))
    chao.desenhar(tela)
    pygame.display.update()