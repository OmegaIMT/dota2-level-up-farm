# new_game.py
# Requisitos: pip install pyautogui opencv-python

import time
import os
import argparse
from typing import Optional, Callable
import pyautogui as pg
import config  # precisa do config.mapa e config.ESCOLHER_MAPA

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

# ===== Funções auxiliares =====
def set_status(etapa: str):
    if ON_STATUS:
        try:
            ON_STATUS(etapa=etapa)
        except Exception:
            pass

def procurar_imagem(caminho_img, conf=0.8):
    try:
        pos = pg.locateOnScreen(caminho_img, confidence=conf)
    except pg.ImageNotFoundException:
        pos = None
    return pos

def listar_mapas_visiveis(pasta, conf=0.8):
    visiveis = []
    for arquivo in os.listdir(pasta):
        if arquivo.lower().endswith(".png"):
            caminho = os.path.join(pasta, arquivo)
            pos = procurar_imagem(caminho, conf=conf)
            if pos:
                visiveis.append((arquivo, pos))
    return visiveis

def numero_mapa(nome_arquivo):
    try:
        return int(os.path.splitext(nome_arquivo)[0])
    except ValueError:
        return None

def escolher_mapa(conf=0.8):
    """Seleciona o mapa desejado clicando nele ou no mais próximo até achar."""
    pasta_mapas = os.path.dirname(config.ESCOLHER_MAPA)
    mapa_desejado = numero_mapa(f"{config.mapa}.png")

    while True:
        pos = procurar_imagem(config.ESCOLHER_MAPA, conf=conf)
        if pos:
            x, y = pg.center(pos)
            # Move primeiro
            pg.moveTo(x, y)
            time.sleep(0.2)
            # Depois clica
            pg.click()
            print(f"[Mapa] Mapa {config.mapa} encontrado e clicado em ({x}, {y})")
            # Depois move para baixo
            pg.moveTo(1312, 1053)
            break

        visiveis = listar_mapas_visiveis(pasta_mapas, conf=conf)
        if not visiveis:
            print("[Mapa] Nenhum mapa visível, tentando novamente...")
            time.sleep(1)
            continue

        visiveis_numerados = [(nome, pos, numero_mapa(nome)) for nome, pos in visiveis if numero_mapa(nome) is not None]
        if not visiveis_numerados:
            print("[Mapa] Nenhum mapa visível com número válido.")
            time.sleep(1)
            continue

        mais_proximo = min(visiveis_numerados, key=lambda x: abs(x[2] - mapa_desejado))
        nome, pos, num = mais_proximo
        x, y = pg.center(pos)
        # Move primeiro
        pg.moveTo(x, y)
        time.sleep(0.2)
        # Depois clica
        pg.click()
        print(f"[Mapa] Cliquei no mapa {nome} ({num}) para aproximar do {mapa_desejado}")
        # Depois move para baixo
        pg.moveTo(1312, 1053)
        time.sleep(1)

def clicar_imagem(caminho: str, confidence: float = CONFIDENCE, delay: float = CLICK_DELAY) -> bool:
    if not os.path.isfile(caminho):
        return False
    try:
        pos = pg.locateCenterOnScreen(caminho, confidence=confidence)
    except Exception:
        pos = None

    if pos:
        try:
            pg.moveTo(pos.x, pos.y)
            time.sleep(0.5)
            pg.click()
            time.sleep(delay)
            return True
        except Exception:
            return False
    return False

def clicar_varias_vezes(caminho: str, vezes: int = 3, confidence: float = CONFIDENCE, delay: float = CLICK_DELAY):
    for _ in range(vezes):
        if not clicar_imagem(caminho, confidence=confidence, delay=delay):
            time.sleep(RETRY_DELAY / 2)

# ===== Fluxo principal =====
def executar_jogo(
    max_retries: int = 5,
    delay_after_click: float = CLICK_DELAY,
    on_status: Optional[Callable[..., None]] = None
) -> bool:
    global ON_STATUS
    ON_STATUS = on_status

    set_status("iniciando")
    tentativas = 0

    try:
        # 0) Escolher o mapa antes de iniciar
        set_status("escolhendo_mapa")
        escolher_mapa(conf=0.9)

        while tentativas < max_retries:
            set_status("Esperando para Iniciar")
            time.sleep(3)
            set_status("Buscando iniciar")

            if not clicar_imagem(IMG_INICIAR, delay=delay_after_click):
                tentativas += 1
                time.sleep(2)
                continue

            set_status("clicou_iniciar")

            set_status("confirmando")
            clicar_varias_vezes(IMG_INICIAR2, vezes=3, delay=delay_after_click)

            set_status("carregando")
            time.sleep(10)

            # 5) No final, clicar no mapa desejado novamente
            set_status("clicando_mapa_final")
            escolher_mapa(conf=0.9)

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

# Execução standalone
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--delay", type=float, default=0.0)
    parser.add_argument("--retries", type=int, default=5)
    parser.add_argument("--click-delay", type=float, default=CLICK_DELAY)
    args = parser.parse_args()

    if args.delay > 0:
        time.sleep(args.delay)

    executar_jogo(max_retries=args.retries, delay_after_click=args.click_delay)