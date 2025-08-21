# fim_game.py
# Requisitos: pip install pyautogui

import time
import pyautogui as pg

# Posições dos cliques
POS1 = (1131, 643)
POS2 = (836, 578)
POS3 = (1133, 646)

def clicar_posicao(x, y, delay=0.5):
    """Move o mouse instantaneamente e clica após um pequeno delay."""
    pg.moveTo(x, y)
    time.sleep(delay)
    pg.click()

def executar(on_status=None):
    def status(msg):
        if on_status:
            on_status(status=msg)

    status("Iniciando fim_game")
    time.sleep(1)

    status("Executando clique 1")
    clicar_posicao(*POS1)
    time.sleep(1)

    status("Executando clique 2")
    clicar_posicao(*POS2)
    time.sleep(13)

    status("Executando clique 3")
    clicar_posicao(*POS3)

    status("fim_game concluído")

if __name__ == "__main__":
    executar()