# new_game.py
# Requisitos: pip install pyautogui opencv-python

import time
import os
import argparse
from typing import Optional, Callable

import pyautogui as pg

pg.FAILSAFE = True
pg.PAUSE = 0.05

# Imagens dos botões
IMG_INICIAR  = r"imagens\\buttons\\iniciar.png"
IMG_INICIAR2 = r"imagens\\buttons\\iniciar2.png"

# Parâmetros de detecção e timing
CONFIDENCE   = 0.86
RETRY_DELAY  = 1.0
CLICK_DELAY  = 1.0

# Callback de status (opcional), usado pelo overlay/log
ON_STATUS: Optional[Callable[..., None]] = None

def set_status(etapa: str):
    """
    Publica o status atual para quem estiver assinando (overlay, logs, etc.)
    """
    if ON_STATUS:
        try:
            ON_STATUS(etapa=etapa)
        except Exception:
            pass

def clicar_imagem(caminho: str, confidence: float = CONFIDENCE, delay: float = CLICK_DELAY) -> bool:
    if not os.path.isfile(caminho):
        return False
    try:
        pos = pg.locateCenterOnScreen(caminho, confidence=confidence)
    except Exception:
        pos = None

    if pos:
        try:
            # Move instantaneamente para a posição
            pg.moveTo(pos.x, pos.y)  
            # Garante um pequeno tempo para o cursor "assentar"
            time.sleep(0.5)
            # Agora clica
            pg.click()
            time.sleep(delay)
            return True
        except Exception:
            return False
    return False

def clicar_varias_vezes(caminho: str, vezes: int = 3, confidence: float = CONFIDENCE, delay: float = CLICK_DELAY):
    """
    Clica na mesma imagem até 'vezes' tentativas (útil para confirmar diálogos em sequência).
    Ignora silenciosamente quando não encontra.
    """
    for _ in range(vezes):
        if not clicar_imagem(caminho, confidence=confidence, delay=delay):
            time.sleep(RETRY_DELAY / 2)

def executar_jogo(
    max_retries: int = 5,
    delay_after_click: float = CLICK_DELAY,
    on_status: Optional[Callable[..., None]] = None
) -> bool:
    """
    Fluxo:
    1) Busca e clica no botão 'Iniciar'
    2) Confirmações subsequentes ('iniciar2')
    3) Aguarda um curto período para carregar a partida
    4) Retorna True/False sem chamar outros módulos (orquestração externa)
    """
    global ON_STATUS
    ON_STATUS = on_status

    set_status("iniciando")
    tentativas = 0

    try:
        while tentativas < max_retries:
            set_status("Esperando para Iniciar")
            time.sleep(3)            
            set_status("Buscando inicar")

            if not clicar_imagem(IMG_INICIAR, delay=delay_after_click):
                tentativas += 1
                time.sleep(2)
                continue

            set_status("clicou_iniciar")

            # Confirma diálogos/etapas adicionais
            set_status("confirmando")
            clicar_varias_vezes(IMG_INICIAR2, vezes=3, delay=delay_after_click)

            # Aguarda carregamento inicial
            set_status("carregando")
            time.sleep(10)

            # Finaliza aqui — quem orquestra chamará o próximo passo
            set_status("finalizado")
            return True

        set_status("falha_iniciar")
        return False

    except pg.FailSafeException:
        set_status("interrompido_failsafe")
        return False
    except Exception:
        set_status("erro")
        return False

# Execução standalone opcional (útil para testes)
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--delay", type=float, default=0.0, help="Atraso inicial antes de começar (segundos)")
    parser.add_argument("--retries", type=int, default=5, help="Número máximo de tentativas para encontrar 'Iniciar'")
    parser.add_argument("--click-delay", type=float, default=CLICK_DELAY, help="Delay após cada clique (segundos)")
    args = parser.parse_args()

    if args.delay > 0:
        time.sleep(args.delay)

    executar_jogo(max_retries=args.retries, delay_after_click=args.click_delay)