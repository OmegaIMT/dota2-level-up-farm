# farm.py
# Requisitos: pip install pyautogui

import time
import os
import pyautogui as pg
from typing import Optional, Callable

pg.FAILSAFE = True
pg.PAUSE = 0.05

IMG_REFRESH = r"imagens\\buttons\\refresh.png"
DIR_HERO    = r"imagens\\summon_hero"
CONFIDENCE = 0.86

ON_STATUS: Optional[Callable[..., None]] = None

# ===== Funções auxiliares =====
def set_status(status: str):
    if ON_STATUS:
        try:
            ON_STATUS(status=status)
        except Exception:
            pass

def clicar(tipo: str, x: int, y: int, delay: float = 0.3):
    pg.moveTo(x, y)
    pg.click(button=tipo)
    time.sleep(delay)

def clicar_centro(button="right", delay: float = 0.3):
    sw, sh = pg.size()
    clicar(button, sw // 2, sh // 2, delay=delay)

def _locate_center(path: str):
    try:
        return pg.locateCenterOnScreen(path, confidence=CONFIDENCE)
    except Exception:
        return None

# ===== Herói =====
def _listar_hero_paths():
    arquivos = sorted(os.listdir(DIR_HERO))
    for nome in arquivos:
        caminho = os.path.join(DIR_HERO, nome)
        if os.path.isfile(caminho):
            yield caminho

def escolher_heroi():
    clicou = False
    for path in _listar_hero_paths():
        set_status(f"{os.path.basename(path)}")
        pos = _locate_center(path)
        if pos:
            pg.moveTo(pos.x, pos.y)
            pg.click()
            time.sleep(0.8)
            clicou = True
            break
    if not clicou:
        set_status("Nenhum Herói Encontrado")
        clicar_centro(button="left")
    return clicou

# ===== Refresh =====
def procurar_refresh_loop(poll: float = 0.5) -> bool:
    while True:
        if os.path.isfile(IMG_REFRESH):
            try:
                pos = pg.locateCenterOnScreen(IMG_REFRESH, confidence=0.7)
                if pos:
                    set_status("Buscando Heroi")
                    escolher_heroi()
                    return True
            except pg.ImageNotFoundException:
                pass
        time.sleep(poll)

# ===== Execução principal =====
def executar(on_status: Optional[Callable[..., None]] = None) -> bool:
    global ON_STATUS
    ON_STATUS = on_status

    set_status("Farmando")
    time.sleep(1)

    set_status("Automatizando ouro e xp")
    ouro_xp_clicks = [(1267, 912), (1212, 914)]
    for x, y in ouro_xp_clicks:
        clicar("right", x, y)
        time.sleep(1)

    set_status("Upando Atributos")

    atributos_clicks = [
        ("left", 1723, 1050),              # 1
        *[("left", 1079, 1039)] * 8,       # 2–9
        ("right", 1094, 936)              # 10
    ]

    for tipo, x, y in atributos_clicks:
        clicar(tipo, x, y)
        time.sleep(1)

    set_status("Indo para o centro")
    pg.press("f3")
    time.sleep(1)
    clicar_centro(button="right")
    time.sleep(1)
    pg.moveTo(1284, 1052)

    return procurar_refresh_loop()

if __name__ == "__main__":
    executar(lambda status: print(f"[STATUS] {status}"))