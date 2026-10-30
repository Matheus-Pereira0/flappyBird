"""Classe principal que controla a partida."""
import math
import random
import pygame
from config import *
from entities import Bird, Pipe, Coin, Projectile

# GAME - lógica principal
# ============================================================
# Controla a run inteira: salas, dificuldade, colisões, upgrades,
# pontuação, estados da partida e desenho da interface.
class Game:
    def __init__(self):
        self.best = 0
        self.reset()

    def reset(self):
        self.bird = Bird()

        self.pipes = []
        self.coins = []
        self.projectiles = []
        self.enemy_projectiles = []
        self.weapon_cooldown = 0

        self.score = 0
        self.coins_collected = 0
        self.distance = 0
        self.xp = 0
        self.xp_to_next = 100

        self.level = 1
        self.room = 1
        self.room_progress = 0
        self.room_length = 12

        self.scroll_speed = 4.2
        self.spawn_timer = 0
        self.spawn_interval = 95

        self.state = "playing"
        self.upgrade_choices = []

        self.message = ""
        self.message_timer = 0

        self.ground_scroll = 0
        self.clouds = [
            [random.randint(0, WIDTH), random.randint(50, 250), random.randint(40, 90)]
            for _ in range(7)
        ]

    # A dificuldade aumenta conforme o jogador avança pelas salas.
    def difficulty(self):
        return min(10, 1 + self.room // 2)

    # Calcula o tamanho da abertura dos canos. Quanto maior a dificuldade,
    # menor é a abertura.
    def current_gap(self):
        # Starts generous, then narrows.
        return max(118, 205 - self.difficulty() * 9)

    def current_speed(self):
        return self.scroll_speed * (1 + self.speed_multiplier_from_level())

    def speed_multiplier_from_level(self):
        return min(0.55, (self.level - 1) * 0.035)

    # Gera um novo obstáculo e, ocasionalmente, uma moeda.
    def spawn_pipe(self):
        gap = self.current_gap()
        margin = 70 + gap / 2
        center = random.randint(int(margin), int(HEIGHT - margin))

        blocked = random.random() < min(0.24, 0.10 + self.difficulty() * 0.015)
        shooter = random.random() < min(0.32, 0.16 + self.difficulty() * 0.02)
        pipe = Pipe(
            WIDTH + 30,
            center,
            gap,
            blocked=blocked,
            shooter=shooter,
            level=self.level,
        )
        self.pipes.append(pipe)

        # Coins have a chance to appear.
        coin_chance = min(0.85, 0.42 + self.bird.coin_bonus * 0.08)
        if random.random() < coin_chance:
            # Put the coin in or near the gap.
            cy = center + random.randint(-int(gap * 0.3), int(gap * 0.3))
            self.coins.append(Coin(WIDTH + 68, cy))

    # Entra no estado de escolha de upgrade depois de limpar uma sala.
    def begin_upgrade(self):
        self.state = "upgrade"
        self.upgrade_choices = random.sample(UPGRADE_POOL, 3)

    # Aplica o upgrade escolhido (0, 1 ou 2).
    def apply_upgrade(self, index):
        if not (0 <= index < len(self.upgrade_choices)):
            return

        name, description, key = self.upgrade_choices[index]

        if key == "flap":
            self.bird.flap_upgrades = getattr(self.bird, "flap_upgrades", 0) + 1
        elif key == "gravity":
            self.bird.gravity_upgrades = getattr(self.bird, "gravity_upgrades", 0) + 1
        elif key == "hp":
            self.bird.max_hp += 1
            self.bird.hp = min(self.bird.max_hp, self.bird.hp + 1)
        elif key == "armor":
            self.bird.armor += 1
        elif key == "magnet":
            self.bird.magnet += 1
        elif key == "speed":
            self.bird.speed_bonus += 1
            self.scroll_speed += 0.35
        elif key == "coins":
            self.bird.coin_bonus += 1
        elif key == "revive":
            self.bird.revive_available = True
        elif key == "score":
            self.bird.score_multiplier += 0.25
        elif key == "weapon_damage":
            self.bird.weapon_damage += 1
        elif key == "weapon_fire_rate":
            self.bird.weapon_cooldown = max(5, self.bird.weapon_cooldown - 3)
        elif key == "weapon_speed":
            self.bird.weapon_speed += 3

        self.message = f"{name}: {description}"
        self.message_timer = 140

        self.room += 1
        self.room_progress = 0

        # Clear the current obstacles so the new room feels distinct.
        self.pipes.clear()
        self.coins.clear()
        self.spawn_timer = 20
        self.state = "playing"

    # Aplica uma velocidade vertical para fazer o pássaro subir.
    def flap(self):
        if self.state == "playing":
            self.bird.flap()

    # Dispara para frente; o cooldown evita que a tecla vire um tiro contínuo.
    def shoot(self):
        if self.state == "playing" and self.weapon_cooldown <= 0:
            self.projectiles.append(
                Projectile(
                    self.bird.x + 28,
                    self.bird.y,
                    self.bird.weapon_speed,
                    YELLOW,
                    damage=self.bird.weapon_damage,
                )
            )
            self.weapon_cooldown = self.bird.weapon_cooldown

    def gain_xp(self, amount):
        self.xp += amount
        leveled_up = False
        while self.xp >= self.xp_to_next:
            self.xp -= self.xp_to_next
            self.level += 1
            self.xp_to_next = int(self.xp_to_next * 1.25)
            leveled_up = True

        if leveled_up:
            self.message = f"Level up! Level {self.level}"
            self.message_timer = 140

    def update_projectiles(self):
        for projectile in self.projectiles:
            projectile.update()
        for projectile in self.enemy_projectiles:
            projectile.update()

        for projectile in self.projectiles:
            if projectile.offscreen():
                continue
            for pipe in self.pipes:
                if pipe.rect_top.colliderect(projectile.rect) or pipe.rect_bottom.colliderect(projectile.rect):
                    pipe.hp -= projectile.damage
                    projectile.x = WIDTH + 100
                    if pipe.hp <= 0:
                        pipe.destroyed = True
                        self.gain_xp(pipe.xp_reward)
                        self.score += int(15 * self.bird.score_multiplier)
                    break

        bird_rect = pygame.Rect(
            int(self.bird.x - self.bird.radius),
            int(self.bird.y - self.bird.radius),
            self.bird.radius * 2,
            self.bird.radius * 2,
        )
        for projectile in self.enemy_projectiles:
            if not projectile.offscreen() and bird_rect.colliderect(projectile.rect):
                projectile.x = -100
                if self.bird.hurt(projectile.damage):
                    self.game_over()

        self.projectiles = [p for p in self.projectiles if not p.offscreen()]
        self.enemy_projectiles = [p for p in self.enemy_projectiles if not p.offscreen()]
        self.pipes = [p for p in self.pipes if not getattr(p, "destroyed", False)]

    # Verifica colisões com canos, teto e chão.
    def handle_collision(self):
        bird_rect = pygame.Rect(
            int(self.bird.x - self.bird.radius + 3),
            int(self.bird.y - self.bird.radius + 3),
            self.bird.radius * 2 - 6,
            self.bird.radius * 2 - 6,
        )

        collided = False

        for pipe in self.pipes:
            if bird_rect.colliderect(pipe.rect_top) or bird_rect.colliderect(pipe.rect_bottom):
                collided = True
                break

        if self.bird.y - self.bird.radius <= 0 or self.bird.y + self.bird.radius >= HEIGHT - 55:
            collided = True

        if collided:
            if self.bird.hurt():
                self.game_over()
            else:
                # Push away from the collision slightly.
                self.bird.vy = -3

    # Coleta moedas dentro do raio normal ou aumentado pelo Magnet.
    def collect_coins(self):
        for coin in self.coins:
            if coin.collected:
                continue

            dx = coin.x - self.bird.x
            dy = coin.y - self.bird.y
            dist = math.hypot(dx, dy)

            pickup_radius = 30 + self.bird.magnet * 38

            if dist < pickup_radius:
                coin.collected = True
                self.coins_collected += 1
                self.score += int(25 * self.bird.score_multiplier)

    # Atualiza a física do pássaro a cada frame.
    def update(self):
        if self.state != "playing":
            return

        self.bird.update()

        if self.weapon_cooldown > 0:
            self.weapon_cooldown -= 1

        speed = self.current_speed()

        self.spawn_timer -= 1
        if self.spawn_timer <= 0:
            self.spawn_pipe()
            # Harder rooms have pipes slightly closer together.
            self.spawn_interval = max(63, 96 - self.difficulty() * 3)
            self.spawn_timer = self.spawn_interval

        for pipe in self.pipes:
            pipe.update(speed)

            if pipe.shooter and pipe.shot_timer <= 0:
                self.enemy_projectiles.append(
                    Projectile(pipe.x, pipe.gap_y, -7, RED, pipe.projectile_damage)
                )
                pipe.shot_timer = random.randint(90, 145)

            if not pipe.scored and pipe.x + pipe.width < self.bird.x:
                pipe.scored = True
                self.score += int(10 * self.bird.score_multiplier)
                self.room_progress += 1

        for coin in self.coins:
            coin.update(speed)

        self.update_projectiles()
        self.collect_coins()
        self.handle_collision()

        self.pipes = [p for p in self.pipes if not p.offscreen()]
        self.coins = [c for c in self.coins if not c.offscreen() and not c.collected]

        self.distance += speed

        # Every room_length passed pipes, offer an upgrade.
        if self.room_progress >= self.room_length:
            self.begin_upgrade()

        if self.score > self.best:
            self.best = self.score

        if self.message_timer > 0:
            self.message_timer -= 1

    # Encerra a run e mostra a tela de Game Over.
    def game_over(self):
        self.state = "game_over"
        self.best = max(self.best, self.score)

    # Desenha o céu, nuvens e chão.
    def draw_background(self, surface):
        # Simple vertical sky gradient.
        for y in range(HEIGHT):
            t = y / HEIGHT
            c = (
                int(SKY[0] * (1 - t) + SKY_DARK[0] * t),
                int(SKY[1] * (1 - t) + SKY_DARK[1] * t),
                int(SKY[2] * (1 - t) + SKY_DARK[2] * t),
            )
            pygame.draw.line(surface, c, (0, y), (WIDTH, y))

        # Clouds
        for cloud in self.clouds:
            x, y, size = cloud
            pygame.draw.circle(surface, WHITE, (int(x), int(y)), size // 3)
            pygame.draw.circle(surface, WHITE, (int(x + size // 3), int(y - 10)), size // 2)
            pygame.draw.circle(surface, WHITE, (int(x + size * 0.65), int(y)), size // 3)
            pygame.draw.rect(
                surface,
                WHITE,
                (int(x - size // 3), int(y), int(size), int(size // 4))
            )

            cloud[0] -= 0.35
            if cloud[0] < -150:
                cloud[0] = WIDTH + random.randint(20, 200)
                cloud[1] = random.randint(50, 250)

        # Ground
        pygame.draw.rect(surface, GROUND, (0, HEIGHT - 55, WIDTH, 55))
        pygame.draw.rect(surface, GREEN, (0, HEIGHT - 55, WIDTH, 8))

        self.ground_scroll = (self.ground_scroll + self.current_speed()) % 40
        for x in range(-40, WIDTH + 40, 40):
            xx = x - int(self.ground_scroll)
            pygame.draw.line(
                surface,
                (175, 145, 70),
                (xx, HEIGHT - 35),
                (xx + 18, HEIGHT - 15),
                3,
            )

    # Desenha pontuação, HP, sala, progresso e alguns upgrades.
    def draw_hud(self, surface):
        # Top-left
        text = FONT.render(f"Score: {self.score}", True, WHITE)
        surface.blit(text, (18, 15))

        text = SMALL.render(f"Best: {self.best}", True, WHITE)
        surface.blit(text, (20, 46))

        text = SMALL.render(f"Room: {self.room}  |  Level: {self.level}", True, WHITE)
        surface.blit(text, (20, 70))

        text = SMALL.render(f"XP: {self.xp}/{self.xp_to_next}", True, WHITE)
        surface.blit(text, (20, 94))

        # HP
        hp_text = SMALL.render("HP:", True, WHITE)
        surface.blit(hp_text, (WIDTH - 175, 18))

        for i in range(self.bird.max_hp):
            x = WIDTH - 125 + i * 25
            color = RED if i < self.bird.hp else (95, 70, 75)
            pygame.draw.circle(surface, color, (x, 29), 8)

        # Room progress
        bar_w = 220
        progress = min(1, self.room_progress / self.room_length)
        pygame.draw.rect(surface, BLACK, (WIDTH - bar_w - 20, 50, bar_w, 16), border_radius=7)
        pygame.draw.rect(
            surface,
            YELLOW,
            (WIDTH - bar_w - 20, 50, int(bar_w * progress), 16),
            border_radius=7,
        )
        label = SMALL.render("Next upgrade", True, WHITE)
        surface.blit(label, (WIDTH - bar_w - 20, 70))

        # Active upgrade stats
        stats = [
            f"Coins: {self.coins_collected}",
            f"Flap: +{getattr(self.bird, 'flap_upgrades', 0)}",
            f"Gravity: -{getattr(self.bird, 'gravity_upgrades', 0) * 8}%",
            f"Armor: {self.bird.armor}",
            f"Magnet: {self.bird.magnet}",
            f"Weapon: {self.bird.weapon_damage} dmg / {self.bird.weapon_cooldown} cd",
        ]

        x = 18
        y = HEIGHT - 43
        for i, s in enumerate(stats):
            if i == 0:
                continue
            txt = SMALL.render(s, True, BLACK)
            surface.blit(txt, (x, y))
            x += txt.get_width() + 18

        if self.message_timer > 0:
            msg = FONT.render(self.message, True, WHITE)
            box = msg.get_rect(center=(WIDTH // 2, 30))
            box.inflate_ip(24, 12)
            pygame.draw.rect(surface, BLACK, box, border_radius=8)
            surface.blit(msg, msg.get_rect(center=box.center))

    # Desenha o pássaro usando apenas formas do Pygame.
    def draw(self, surface):
        self.draw_background(surface)

        for pipe in self.pipes:
            pipe.draw(surface)

        for projectile in self.projectiles:
            projectile.draw(surface)
        for projectile in self.enemy_projectiles:
            projectile.draw(surface)

        for coin in self.coins:
            coin.draw(surface)

        self.bird.draw(surface)
        self.draw_hud(surface)

        if self.state == "upgrade":
            self.draw_upgrade(surface)
        elif self.state == "game_over":
            self.draw_game_over(surface)

    def draw_overlay(self, surface):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 155))
        surface.blit(overlay, (0, 0))

    # Desenha as três opções de upgrade.
    def draw_upgrade(self, surface):
        self.draw_overlay(surface)

        title = HUGE.render("ROOM CLEARED!", True, YELLOW)
        surface.blit(title, title.get_rect(center=(WIDTH // 2, 85)))

        subtitle = FONT.render(
            "Choose an upgrade: press 1, 2 or 3",
            True,
            WHITE,
        )
        surface.blit(subtitle, subtitle.get_rect(center=(WIDTH // 2, 135)))

        card_w, card_h = 245, 280
        gap = 25
        total = card_w * 3 + gap * 2
        start_x = (WIDTH - total) // 2

        for i, (name, desc, key) in enumerate(self.upgrade_choices):
            x = start_x + i * (card_w + gap)
            y = 180

            pygame.draw.rect(
                surface,
                (40, 45, 60),
                (x, y, card_w, card_h),
                border_radius=16,
            )
            pygame.draw.rect(
                surface,
                YELLOW,
                (x, y, card_w, card_h),
                3,
                border_radius=16,
            )

            num = BIG.render(str(i + 1), True, YELLOW)
            surface.blit(num, (x + 18, y + 15))

            name_s = FONT.render(name, True, WHITE)
            surface.blit(
                name_s,
                name_s.get_rect(center=(x + card_w // 2, y + 65))
            )

            # Word-wrap description.
            words = desc.split()
            lines = []
            line = ""
            for word in words:
                test = (line + " " + word).strip()
                if SMALL.size(test)[0] <= card_w - 35:
                    line = test
                else:
                    lines.append(line)
                    line = word
            if line:
                lines.append(line)

            for j, ln in enumerate(lines):
                ds = SMALL.render(ln, True, (220, 220, 230))
                surface.blit(
                    ds,
                    ds.get_rect(center=(x + card_w // 2, y + 125 + j * 25))
                )

            # Flavor icon
            pygame.draw.circle(
                surface,
                BLUE,
                (x + card_w // 2, y + 220),
                32,
            )
            pygame.draw.circle(
                surface,
                WHITE,
                (x + card_w // 2, y + 220),
                26,
                3,
            )

    # Desenha a tela de Game Over.
    def draw_game_over(self, surface):
        self.draw_overlay(surface)

        title = HUGE.render("GAME OVER", True, RED)
        surface.blit(title, title.get_rect(center=(WIDTH // 2, 180)))

        lines = [
            f"Score: {self.score}",
            f"Best: {self.best}",
            f"Room reached: {self.room}",
            f"Coins: {self.coins_collected}",
        ]

        for i, line in enumerate(lines):
            t = FONT.render(line, True, WHITE)
            surface.blit(t, t.get_rect(center=(WIDTH // 2, 260 + i * 38)))

        restart = BIG.render("Press R to play again", True, YELLOW)
        surface.blit(restart, restart.get_rect(center=(WIDTH // 2, 455)))

        quit_t = SMALL.render("ESC to quit", True, WHITE)
        surface.blit(quit_t, quit_t.get_rect(center=(WIDTH // 2, 505)))


# ============================================================