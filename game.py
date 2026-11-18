"""Classe principal que controla a partida."""
import math
import random
import pygame
from config import *
from entities import Bird, Pipe, Coin, Projectile

# JOGO - lógica principal
# ============================================================
# Controla a partida: salas, dificuldade, colisões, melhorias,
# pontuação, estados da partida e desenho da interface.
class Game:
    def __init__(self):
        self.best = 0
        self.reset()
        self.state = "tutorial"

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
        self.credits_open = False

    @staticmethod
    def credits_button_rect():
        return pygame.Rect(WIDTH - 170, HEIGHT - 58, 145, 40)

    @staticmethod
    def credits_close_rect():
        return pygame.Rect(WIDTH // 2 - 75, 420, 150, 42)

    def open_credits(self):
        if self.state in ("tutorial", "game_over"):
            self.credits_open = True

    def close_credits(self):
        self.credits_open = False

    # A dificuldade aumenta conforme o jogador avança pelas salas.
    def difficulty(self):
        return min(10, 1 + self.room // 2)

    # Calcula o tamanho da abertura dos canos. Quanto maior a dificuldade,
    # menor é a abertura.
    def current_gap(self):
        # Começa ampla e diminui conforme a dificuldade aumenta.
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

        # Há uma chance de aparecerem moedas.
        coin_chance = min(0.85, 0.42 + self.bird.coin_bonus * 0.08)
        if random.random() < coin_chance:
            # Posiciona a moeda dentro ou perto da abertura.
            cy = center + random.randint(-int(gap * 0.3), int(gap * 0.3))
            self.coins.append(Coin(WIDTH + 68, cy))

    # Entra no estado de escolha de melhoria depois de limpar uma sala.
    def begin_upgrade(self):
        self.state = "upgrade"
        self.upgrade_choices = random.sample(UPGRADE_POOL, 3)

    # Aplica a melhoria escolhida (0, 1 ou 2).
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

        # Remove os obstáculos atuais para diferenciar a nova sala.
        self.pipes.clear()
        self.coins.clear()
        self.spawn_timer = 20
        self.state = "playing"

    # Aplica uma velocidade vertical para fazer o pássaro subir.
    def flap(self):
        if self.state == "playing":
            self.bird.flap()

    def start(self):
        if self.state == "tutorial":
            self.state = "playing"

    # Dispara para frente; o intervalo evita tiros contínuos ao manter a tecla.
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
            self.message = f"Subiu de nível! Nível {self.level}"
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
                # Afasta o pássaro um pouco após a colisão.
                self.bird.vy = -3

    # Coleta moedas dentro do raio normal ou aumentado pela melhoria Ímã.
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

    # Atualiza a física do pássaro a cada quadro.
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
            # Nas salas mais difíceis, os canos ficam um pouco mais próximos.
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

        # Oferece uma melhoria a cada room_length canos ultrapassados.
        if self.room_progress >= self.room_length:
            self.begin_upgrade()

        if self.score > self.best:
            self.best = self.score

        if self.message_timer > 0:
            self.message_timer -= 1

    # Encerra a partida e mostra a tela de fim de jogo.
    def game_over(self):
        self.state = "game_over"
        self.best = max(self.best, self.score)

    # Desenha o cenário e o chão.
    def draw_background(self, surface):
        surface.blit(BACKGROUND_SPRITE, (0, 0))

        # Chão
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

    # Desenha pontuação, vida, sala, progresso e melhorias ativas.
    def draw_hud(self, surface):
        # Canto superior esquerdo
        text = FONT.render(f"Pontuação: {self.score}", True, WHITE)
        surface.blit(text, (18, 15))

        text = SMALL.render(f"Recorde: {self.best}", True, WHITE)
        surface.blit(text, (20, 46))

        text = SMALL.render(f"Sala: {self.room}  |  Nível: {self.level}", True, WHITE)
        surface.blit(text, (20, 70))

        text = SMALL.render(f"EXP: {self.xp}/{self.xp_to_next}", True, WHITE)
        surface.blit(text, (20, 94))

        # Vida
        hp_text = SMALL.render("VIDA:", True, WHITE)
        surface.blit(hp_text, (WIDTH - 175, 18))

        for i in range(self.bird.max_hp):
            x = WIDTH - 125 + i * 25
            color = RED if i < self.bird.hp else (95, 70, 75)
            pygame.draw.circle(surface, color, (x, 29), 8)

        # Progresso da sala
        bar_w = 220
        progress = min(1, self.room_progress / self.room_length)
        pygame.draw.rect(surface, BLACK, (WIDTH - bar_w - 20, 50, bar_w, 16), border_radius=7)
        pygame.draw.rect(
            surface,
            YELLOW,
            (WIDTH - bar_w - 20, 50, int(bar_w * progress), 16),
            border_radius=7,
        )
        label = SMALL.render("Próxima melhoria", True, WHITE)
        surface.blit(label, (WIDTH - bar_w - 20, 70))

        # Indicadores das melhorias ativas
        stats = [
            f"Asas: +{getattr(self.bird, 'flap_upgrades', 0)}",
            f"Grav.: -{getattr(self.bird, 'gravity_upgrades', 0) * 8}%",
            f"Armadura: {self.bird.armor}",
            f"Ímã: {self.bird.magnet}",
            f"Arma: {self.bird.weapon_damage} dano / recarga {self.bird.weapon_cooldown}",
        ]

        x = 18
        y = HEIGHT - 43
        for s in stats:
            txt = SMALL.render(s, True, BLACK)
            surface.blit(txt, (x, y))
            x += txt.get_width() + 18

        if self.message_timer > 0:
            msg = FONT.render(self.message, True, WHITE)
            box = msg.get_rect(center=(WIDTH // 2, 30))
            box.inflate_ip(24, 12)
            pygame.draw.rect(surface, BLACK, box, border_radius=8)
            surface.blit(msg, msg.get_rect(center=box.center))

    # Desenha a partida e a interface.
    def draw(self, surface):
        self.draw_background(surface)

        if self.state == "tutorial":
            self.draw_tutorial(surface)
            self.draw_credits_button(surface)
            if self.credits_open:
                self.draw_credits(surface)
            return

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
            self.draw_credits_button(surface)

        if self.credits_open:
            self.draw_credits(surface)

    def draw_overlay(self, surface):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 155))
        surface.blit(overlay, (0, 0))

    def draw_tutorial(self, surface):
        self.draw_overlay(surface)

        panel = pygame.Rect(75, 55, WIDTH - 150, HEIGHT - 110)
        pygame.draw.rect(surface, (40, 45, 60), panel, border_radius=16)
        pygame.draw.rect(surface, YELLOW, panel, 3, border_radius=16)

        title = HUGE.render("COMO JOGAR", True, YELLOW)
        surface.blit(title, title.get_rect(center=(WIDTH // 2, 112)))

        instructions = [
            "ESPAÇO, ↑, W ou clique: bata as asas para subir; solte para descer.",
            "X ou F: dispare para destruir canos. Os vermelhos bloqueiam a passagem.",
            "Evite os canos, o teto e o chão; colisões fazem você perder vida.",
            "Canos com marcador azul atiram projéteis contra você.",
            "Recolha moedas para ganhar pontos. Passe por 12 canos para avançar de sala.",
            "Destruir canos dá EXP; subir de nível deixa os próximos canos mais fortes.",
            "Ao concluir uma sala, escolha uma melhoria com 1, 2 ou 3 ou clique nela.",
        ]
        for index, instruction in enumerate(instructions):
            text = SMALL.render(instruction, True, WHITE)
            surface.blit(text, (panel.x + 30, 190 + index * 42))

        prompt = FONT.render(
            "Pressione ENTER ou ESPAÇO (ou clique) para começar",
            True,
            YELLOW,
        )
        surface.blit(prompt, prompt.get_rect(center=(WIDTH // 2, 500)))

    def draw_credits_button(self, surface):
        rect = self.credits_button_rect()
        pygame.draw.rect(surface, (40, 45, 60), rect, border_radius=8)
        pygame.draw.rect(surface, YELLOW, rect, 2, border_radius=8)
        label = SMALL.render("Créditos", True, WHITE)
        surface.blit(label, label.get_rect(center=rect.center))

    def draw_credits(self, surface):
        self.draw_overlay(surface)

        panel = pygame.Rect(150, 155, WIDTH - 300, 310)
        pygame.draw.rect(surface, (40, 45, 60), panel, border_radius=16)
        pygame.draw.rect(surface, YELLOW, panel, 3, border_radius=16)

        title = HUGE.render("CRÉDITOS", True, YELLOW)
        surface.blit(title, title.get_rect(center=(WIDTH // 2, 220)))

        lines = [
            "Flappy Bird Roguelike",
            "Desenvolvido por Abner Chub, Davi Willian, ",
            "Lucas Coleti e Matheus Pereira",
        ]
        for index, line in enumerate(lines):
            text = FONT.render(line, True, WHITE)
            surface.blit(text, text.get_rect(center=(WIDTH // 2, 295 + index * 38)))

        rect = self.credits_close_rect()
        pygame.draw.rect(surface, (40, 45, 60), rect, border_radius=8)
        pygame.draw.rect(surface, YELLOW, rect, 2, border_radius=8)
        label = SMALL.render("Voltar", True, WHITE)
        surface.blit(label, label.get_rect(center=rect.center))

    # Desenha as três opções de melhoria.
    def draw_upgrade(self, surface):
        self.draw_overlay(surface)

        title = HUGE.render("SALA CONCLUÍDA!", True, YELLOW)
        surface.blit(title, title.get_rect(center=(WIDTH // 2, 85)))

        subtitle = FONT.render(
            "Escolha uma melhoria: pressione 1, 2 ou 3",
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

            # Quebra a descrição em linhas para caber no cartão.
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

            # Ícone decorativo
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

    # Desenha a tela de fim de jogo.
    def draw_game_over(self, surface):
        self.draw_overlay(surface)

        title = HUGE.render("FIM DE JOGO", True, RED)
        surface.blit(title, title.get_rect(center=(WIDTH // 2, 180)))

        lines = [
            f"Pontuação: {self.score}",
            f"Recorde: {self.best}",
            f"Sala alcançada: {self.room}",
            f"Moedas: {self.coins_collected}",
        ]

        for i, line in enumerate(lines):
            t = FONT.render(line, True, WHITE)
            surface.blit(t, t.get_rect(center=(WIDTH // 2, 260 + i * 38)))

        restart = BIG.render("Pressione R para jogar novamente", True, YELLOW)
        surface.blit(restart, restart.get_rect(center=(WIDTH // 2, 455)))

        quit_t = SMALL.render("ESC para sair", True, WHITE)
        surface.blit(quit_t, quit_t.get_rect(center=(WIDTH // 2, 505)))


# ============================================================