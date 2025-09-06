# farm.py
# Requisitos: pip install pyautogui

import time
import os
import threading
import pyautogui as pg
from typing import Optional, Callable
import config  # para acessar config.seta e config.encerrar

pg.FAILSAFE = True
pg.PAUSE = 0.05

IMG_REFRESH = r"imagens\\buttons\\refresh.png"
IMG_BOSS_ICON = r"imagens\\boss\\boss.png"
DIR_HERO    = r"imagens\\heros_game"
CONFIDENCE = 0.7

ON_STATUS: Optional[Callable[..., None]] = None

# ===== Verificador de interrupção =====
def _verificar_interrupcao_periodica(stop_evt: threading.Event):
    while not stop_evt.is_set():
        for _ in range(190):
            if stop_evt.is_set():
                return
            time.sleep(1)
        if config.seta or config.encerrar:
            if ON_STATUS:
                ON_STATUS(status="Interrupção solicitada — encerrando farm")
            stop_evt.set()
            raise InterruptedError("Interrompido por monitor_seta")

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
    if config.seta or config.encerrar:
        return False
    clicou = False
    for path in _listar_hero_paths():
        if config.seta or config.encerrar:
            return False
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
        if config.seta or config.encerrar:
            return False

        if os.path.isfile(IMG_REFRESH):
            try:
                pos = pg.locateCenterOnScreen(IMG_REFRESH, confidence=0.7)
                if pos:
                    set_status("Buscando Herói")
                    escolher_heroi()
                    return True
            except pg.ImageNotFoundException:
                pass

        if os.path.isfile(IMG_BOSS_ICON):
            try:
                boss_pos = pg.locateCenterOnScreen(IMG_BOSS_ICON, confidence=0.7)
                if boss_pos:
                    set_status("Boss Encontrado — Encerrando")
                    return True
            except pg.ImageNotFoundException:
                pass

        time.sleep(poll)

# ===== Arrastar Itens =====
def arrastar_itens():
    if config.seta or config.encerrar:
        return
    set_status("Arrastando Itens")
    pg.moveTo(1646, 630)
    pg.mouseDown()
    time.sleep(0.5)
    pg.moveTo(1719, 543)
    time.sleep(0.5)
    pg.mouseUp()
    time.sleep(0.5)

    if config.seta or config.encerrar:
        return
    pg.moveTo(1727, 630)
    pg.mouseDown()
    time.sleep(0.5)
    pg.moveTo(1648, 540)
    time.sleep(0.5)
    pg.mouseUp()
    time.sleep(0.5)

# ===== Execução principal =====
def executar(on_status: Optional[Callable[..., None]] = None) -> bool:
    global ON_STATUS
    ON_STATUS = on_status

    stop_evt = threading.Event()
    threading.Thread(target=_verificar_interrupcao_periodica, args=(stop_evt,), daemon=True).start()

    try:
        if config.seta or config.encerrar:
            return False

        set_status("Farmando")
        time.sleep(1)

        if config.seta or config.encerrar:
            return False
        set_status("Automatizando ouro e xp")
        ouro_xp_clicks = [(1301, 912), (1235, 911)]
        for x, y in ouro_xp_clicks:
            if config.seta or config.encerrar:
                return False
            clicar("right", x, y)
            time.sleep(1)

        if config.seta or config.encerrar:
            return False
        set_status("Upando Atributos")
        atributos_clicks = [
            ("left", 1723, 1050),
            *[("left", 1079, 1039)] * 8,
            ("right", 1094, 936)
        ]
        for tipo, x, y in atributos_clicks:
            if config.seta or config.encerrar:
                return False
            clicar(tipo, x, y)
            time.sleep(1)

        arrastar_itens()

        if config.seta or config.encerrar:
            return False
        set_status("Indo para o centro")
        pg.press("f3")
        time.sleep(1)
        clicar_centro(button="right")
        time.sleep(1)
        pg.moveTo(1284, 1052)

        return procurar_refresh_loop()

    except InterruptedError:
        set_status("Interrompido por monitor_seta")
        return False

    except Exception as e:
        set_status(f"Erro: {type(e).__name__}")
        return False

if __name__ == "__main__":
    executar(lambda status: print(f"[STATUS] {status}"))