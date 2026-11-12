"""Configurações, inicialização visual e constantes do jogo."""
from pathlib import Path

import pygame

pygame.init()

pygame.display.set_caption("Pássaro Roguelike")
WIDTH, HEIGHT = 900, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
CLOCK = pygame.time.Clock()

FONT = pygame.font.SysFont("arial", 24)
SMALL = pygame.font.SysFont("arial", 18)
BIG = pygame.font.SysFont("arial", 42, bold=True)
HUGE = pygame.font.SysFont("arial", 64, bold=True)

SPRITE_DIR = Path(__file__).resolve().parent / "sprites"
BIRD_FRAMES = [
    pygame.transform.scale(
        pygame.image.load(str(SPRITE_DIR / f"pinto_{frame:04d}.png")).convert_alpha(),
        (64, 64),
    )
    for frame in range(1, 5)
]
PIPE_SPRITE = pygame.image.load(str(SPRITE_DIR / "cano.png")).convert_alpha()
BACKGROUND_SPRITE = pygame.transform.scale(
    pygame.image.load(str(SPRITE_DIR / "cenario.png")).convert_alpha(),
    (WIDTH, HEIGHT),
)

WHITE = (245, 245, 245)
BLACK = (25, 25, 30)
GREEN = (65, 180, 85)
YELLOW = (255, 220, 65)
RED = (225, 65, 70)
BLUE = (65, 120, 230)
GOLD = (255, 190, 45)
GROUND = (205, 175, 95)

UPGRADE_POOL = [
    ("Asas", "Força de voo +0,18", "flap"),
    ("Penas", "Gravidade -8%", "gravity"),
    ("Coração", "Vida máxima +1 e recupera 1", "hp"),
    ("Armadura", "Reduz em 1 o dano recebido", "armor"),
    ("Ímã", "Atrai moedas de mais longe", "magnet"),
    ("Turbina", "Velocidade de voo +10%", "speed"),
    ("Sorte", "Mais moedas aparecem", "coins"),
    ("Fênix", "Ressuscita uma vez por partida", "revive"),
    ("Pontuação", "Multiplicador de pontos +25%", "score"),
    ("Tiro potente", "Dano dos disparos +1", "weapon_damage"),
    ("Tiro rápido", "Intervalo entre disparos -3 quadros", "weapon_fire_rate"),
    ("Tiro de longo alcance", "Velocidade dos disparos +3", "weapon_speed"),
]
