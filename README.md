# Flappy Roguelike organizado

## Como executar

1. Instale a dependência:
   ```bash
   pip install pygame
   ```
2. Execute:
   ```bash
   python3 main.py
   ```

## Controles e canos

- `SPACE`, `UP` ou `W`: faz o pássaro subir.
- `X` ou `F`: dispara a arma para destruir canos.
- Canos vermelhos são bloqueados e só podem ser atravessados depois de destruídos.
- Canos azuis atiram projéteis no pássaro.
- Canos vermelhos/azuis podem combinar as duas características.
- Destruir canos concede XP; ao subir de nível, os novos canos ficam mais resistentes e causam mais dano.
- As opções `Power Shot`, `Rapid Fire` e `Long Shot` melhoram dano, cadência e velocidade dos disparos.

## Estrutura

- `config.py`: configurações da janela, fontes e constantes.
- `entities.py`: classes `Bird`, `Pipe` e `Coin`.
- `game.py`: lógica principal, colisões, upgrades e desenho.
- `main.py`: loop principal e entrada do programa.
