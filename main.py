"""Ponto de entrada do jogo."""
import sys
import pygame
from config import SCREEN, CLOCK, WIDTH
from game import Game

# LOOP PRINCIPAL
# ============================================================
# Em cada frame o jogo: lê eventos -> atualiza a lógica -> desenha -> espera.
def main():
    game = Game()

    # Loop infinito da partida; termina somente ao fechar a janela/ESC.
    while True:
        # 1) Ler teclado, mouse e eventos da janela.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

                if event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
                    game.flap()
                elif event.key in (pygame.K_x, pygame.K_f):
                    game.shoot()

                if game.state == "upgrade":
                    if event.key == pygame.K_1:
                        game.apply_upgrade(0)
                    elif event.key == pygame.K_2:
                        game.apply_upgrade(1)
                    elif event.key == pygame.K_3:
                        game.apply_upgrade(2)

                elif game.state == "game_over":
                    if event.key == pygame.K_r:
                        game.reset()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if game.state == "playing":
                    game.flap()
                elif game.state == "upgrade":
                    # Click cards as an alternative to 1/2/3.
                    mx, my = event.pos
                    card_w, card_h = 245, 280
                    gap = 25
                    total = card_w * 3 + gap * 2
                    start_x = (WIDTH - total) // 2

                    for i in range(3):
                        rect = pygame.Rect(
                            start_x + i * (card_w + gap),
                            180,
                            card_w,
                            card_h,
                        )
                        if rect.collidepoint(mx, my):
                            game.apply_upgrade(i)

        # 2) Atualizar física, obstáculos, moedas, colisões e progressão.
        game.update()

        # 3) Desenhar o frame atual.
        game.draw(SCREEN)

        # Enviar o frame para a janela e limitar a aproximadamente 60 FPS.
        pygame.display.flip()
        CLOCK.tick(60)


if __name__ == "__main__":
    main()