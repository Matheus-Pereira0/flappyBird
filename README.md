# Pássaro Roguelike

## Como executar

1. Instale a dependência:
   ```bash
   pip install pygame
   ```
2. Execute:
   ```bash
   python3 main.py
   ```

## Como jogar

- **Mover o pássaro:** pressione `ESPAÇO`, `↑` ou `W`, ou clique com o botão esquerdo. Toques repetidos ajudam a controlar a altura.
- **Atirar:** pressione `X` ou `F` para destruir canos.
- **Sobreviver:** atravesse as aberturas e evite os canos, o teto e o chão. Canos vermelhos bloqueiam a passagem e precisam ser destruídos. Canos com marcador azul atiram projéteis.
- **Progredir:** recolha moedas para ganhar pontos. Passar por 12 canos conclui a sala e oferece três melhorias; escolha uma com `1`, `2` ou `3`, ou clique no cartão.
- **Subir de nível:** destruir canos concede EXP. Cada nível aumenta a resistência e o dano dos canos seguintes.
- **Melhorias:** elas podem fortalecer o voo, reduzir a gravidade, aumentar a vida e a armadura, atrair moedas, acelerar os disparos ou melhorar pontuação e velocidade.
- **Fim de jogo:** pressione `R` para iniciar outra partida ou `ESC` para sair.

## Estrutura

- `config.py`: configurações da janela, fontes e constantes.
- `entities.py`: entidades do jogo (`Bird`, `Pipe` e `Coin`).
- `game.py`: lógica principal, colisões, melhorias e desenho.
- `main.py`: ciclo principal e entrada do programa.
- `sprites/`: imagens do cenário, dos canos e quadros de animação do pássaro.
