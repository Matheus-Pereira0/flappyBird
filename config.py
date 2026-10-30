"""Configurações, inicialização visual e constantes do jogo."""
import pygame

pygame.init()

pygame.display.set_caption("Flappy Roguelike")
WIDTH, HEIGHT = 900, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
CLOCK = pygame.time.Clock()

FONT = pygame.font.SysFont("arial", 24)
SMALL = pygame.font.SysFont("arial", 18)
BIG = pygame.font.SysFont("arial", 42, bold=True)
HUGE = pygame.font.SysFont("arial", 64, bold=True)

SKY = (110, 195, 235)
SKY_DARK = (60, 140, 190)
WHITE = (245, 245, 245)
BLACK = (25, 25, 30)
GREEN = (65, 180, 85)
GREEN_DARK = (35, 125, 55)
YELLOW = (255, 220, 65)
ORANGE = (245, 150, 45)
RED = (225, 65, 70)
PURPLE = (145, 85, 210)
BLUE = (65, 120, 230)
GOLD = (255, 190, 45)
GROUND = (205, 175, 95)

UPGRADE_POOL = [
    ("Wings", "Flap strength +18", "flap"),
    ("Feathers", "Gravity -8%", "gravity"),
    ("Heart", "Max HP +1 and heal 1", "hp"),
    ("Armor", "Take 1 less damage", "armor"),
    ("Magnet", "Coins attract from farther away", "magnet"),
    ("Turbo", "Horizontal speed +10%", "speed"),
    ("Fortune", "More coins appear", "coins"),
    ("Phoenix", "One automatic revive per run", "revive"),
    ("Score", "Score multiplier +25%", "score"),
    ("Power Shot", "Weapon damage +1", "weapon_damage"),
    ("Rapid Fire", "Weapon cooldown -3", "weapon_fire_rate"),
    ("Long Shot", "Projectile speed +3", "weapon_speed"),
]
