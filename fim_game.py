# fim_game.py
# Requisitos: pip install pyautogui

import time
import threading
import pyautogui as pg
import config  # para acessar config.seta e config.encerrar

# Posições dos cliques
POS1 = (1131, 643)
POS2 = (836, 578)
POS3 = (1133, 646)

def clicar_posicao(x, y, delay=0.5):
    """Move o mouse instantaneamente e clica após um pequeno delay."""
    if config.seta or config.encerrar:
        raise InterruptedError
    pg.moveTo(x, y)
    time.sleep(delay)
    pg.click()

def _verificar_interrupcao_periodica(stop_evt: threading.Event):
    while not stop_evt.is_set():
        for _ in range(190):
            if stop_evt.is_set():
                return
            time.sleep(1)
        if config.seta or config.encerrar:
            stop_evt.set()
            raise InterruptedError("Interrompido por monitor_seta")

def executar(on_status=None):
    def status(msg):
        if on_status:
            on_status(status=msg)

    stop_evt = threading.Event()
    threading.Thread(target=_verificar_interrupcao_periodica, args=(stop_evt,), daemon=True).start()

    try:
        if config.seta or config.encerrar:
            status("Interrompido antes de iniciar")
            return

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

    except InterruptedError:
        status("Interrompido por monitor_seta")

    except Exception as e:
        status(f"Erro: {type(e).__name__}")

if __name__ == "__main__":
    executar()