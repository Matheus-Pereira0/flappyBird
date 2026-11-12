"""Entidades do jogo: pássaro, canos e moedas."""
import math
import random
import pygame
from config import *

# PÁSSARO - jogador
# ============================================================
# Esta classe guarda a posição, física, vida e upgrades do pássaro.
class Bird:
    def __init__(self):
        self.x = 220
        self.y = HEIGHT // 2
        self.vy = 0
        self.radius = 18
        self.animation_timer = 0
        self.animation_frame = 0

        self.base_gravity = 0.43
        self.flap_power = -7.6

        self.max_hp = 3
        self.hp = 3
        self.armor = 0

        self.magnet = 0
        self.speed_bonus = 0
        self.coin_bonus = 0
        self.score_multiplier = 1.0
        self.weapon_damage = 1
        self.weapon_cooldown = 12
        self.weapon_speed = 11

        self.invuln = 0
        self.revive_available = False

    # Calcula a gravidade atual. Cada melhoria reduz a gravidade.
    def gravity(self):
        return self.base_gravity * (0.92 ** getattr(self, "gravity_upgrades", 0))

    # Aplica uma velocidade vertical para fazer o pássaro subir.
    def flap(self):
        self.vy = self.flap_power - (0.18 * getattr(self, "flap_upgrades", 0))

    # Atualiza a física do pássaro a cada quadro.
    def update(self):
        self.vy += self.gravity()
        self.y += self.vy

        if self.invuln > 0:
            self.invuln -= 1

        self.animation_timer += 1
        if self.animation_timer >= 6:
            self.animation_timer = 0
            self.animation_frame = (self.animation_frame + 1) % len(BIRD_FRAMES)

    # Aplica dano e verifica armadura/ressurreição. Retorna True se morrer.
    def hurt(self, incoming_damage=1):
        if self.invuln > 0:
            return False

        damage = max(1, incoming_damage - self.armor)
        self.hp -= damage
        self.invuln = 75

        if self.hp <= 0 and self.revive_available:
            self.revive_available = False
            self.hp = 1
            self.y = HEIGHT // 2
            self.vy = 0
            self.invuln = 150
            return False

        return self.hp <= 0

    # Desenha o quadro atual da animação do pássaro.
    def draw(self, surface):
        if self.invuln > 0 and (self.invuln // 5) % 2 == 0:
            return

        sprite = BIRD_FRAMES[self.animation_frame]
        surface.blit(sprite, sprite.get_rect(center=(int(self.x), int(self.y))))


# PROJÉTIL - disparo do jogador ou dos canos
# ============================================================
class Projectile:
    def __init__(self, x, y, velocity_x, color, damage=1):
        self.x = x
        self.y = y
        self.velocity_x = velocity_x
        self.color = color
        self.damage = damage
        self.radius = 5

    @property
    def rect(self):
        return pygame.Rect(
            int(self.x - self.radius),
            int(self.y - self.radius),
            self.radius * 2,
            self.radius * 2,
        )

    def update(self):
        self.x += self.velocity_x

    def offscreen(self):
        return self.x < -20 or self.x > WIDTH + 20

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), 2)

# ============================================================

# CANO - obstáculo
# ============================================================
# Cada cano representa as duas partes do obstáculo e a abertura entre elas.
class Pipe:
    def __init__(self, x, gap_y, gap_size, width=75, blocked=False, shooter=False, level=1):
        self.x = x
        self.width = width
        self.gap_y = gap_y
        self.gap_size = 0 if blocked else gap_size
        self.blocked = blocked
        self.shooter = shooter
        self.level = level
        base_hp = 3 if blocked else 2
        self.hp = base_hp + max(0, level - 1)
        self.max_hp = self.hp
        self.xp_reward = 20 + (10 if blocked else 0) + (8 if shooter else 0) + level * 2
        self.projectile_damage = 1 + max(0, (level - 1) // 3)
        self.shot_timer = random.randint(75, 125)
        self.scored = False

    @property
    def rect_top(self):
        return pygame.Rect(
            int(self.x),
            0,
            self.width,
            int(self.gap_y - self.gap_size / 2)
        )

    @property
    def rect_bottom(self):
        top = int(self.gap_y + self.gap_size / 2)
        return pygame.Rect(
            int(self.x),
            top,
            self.width,
            HEIGHT - top
        )

    def update(self, speed):
        self.x -= speed
        if self.shooter:
            self.shot_timer -= 1

    def offscreen(self):
        return self.x + self.width < 0

    # Desenha os canos com o sprite orientado para dentro da abertura.
    def draw(self, surface):
        top = self.rect_top
        bottom = self.rect_bottom

        for rect, flip_vertical in ((top, True), (bottom, False)):
            sprite = pygame.transform.scale(PIPE_SPRITE, rect.size)
            if flip_vertical:
                sprite = pygame.transform.flip(sprite, False, True)
            surface.blit(sprite, rect)

        if self.blocked:
            pygame.draw.line(surface, WHITE, (self.x + 12, self.gap_y - 18), (self.x + self.width - 12, self.gap_y + 18), 4)
            pygame.draw.line(surface, WHITE, (self.x + self.width - 12, self.gap_y - 18), (self.x + 12, self.gap_y + 18), 4)
        elif self.shooter:
            pygame.draw.circle(surface, BLUE, (int(self.x + self.width / 2), int(self.gap_y)), 9)

# ============================================================

# MOEDA
# ============================================================
# Moedas dão pontos e podem ser atraídas pela melhoria Ímã.
class Coin:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 10
        self.collected = False
        self.phase = random.random() * math.tau

    def update(self, speed):
        self.x -= speed
        self.phase += 0.08

    # Desenha a moeda pulsante.
    def draw(self, surface):
        if self.collected:
            return

        r = max(3, int(self.radius * (0.75 + 0.25 * abs(math.sin(self.phase)))))
        pygame.draw.circle(surface, GOLD, (int(self.x), int(self.y)), r)
        pygame.draw.circle(surface, (255, 230, 100), (int(self.x), int(self.y)), max(1, r - 4))

    def offscreen(self):
        return self.x < -30

# ============================================================