# kill_boss.py
# Requisitos: pip install pyautogui opencv-python

import os
import time
import threading
from typing import Optional, Callable
import pyautogui as pg
import upgrade

# Imagens
IMG_SUBIR_NIVEL    = r"imagens\\buttons\\subir_nivel.png"
IMG_BOSS_ICON      = r"imagens\\boss\\boss.png"
IMG_FIM_GAME       = r"imagens\\buttons\\fim_game.png"

# Configurações
CONFIDENCE         = 0.7
POLL_LVLUP         = 0.6
POLL_BOSS          = 0.5
PAUSA_KILL_BOSS    = threading.Event()
ON_STATUS: Optional[Callable[..., None]] = None

# Posições fixas
POS_CONFIRMAR_BOSS = (841, 584)
CLICKS_POS_HEROI = [
    ("left", 1723, 1050),   # 0
    ("right", 886, 935),    # 1
    ("right", 953, 944),    # 2
    ("right", 1029, 941),   # 3
    ("right", 1082, 943),   # 4
    ("right", 1159, 940),   # 5
    ("right", 1235, 932),   # 6
    ("right", 884, 1019),   # 7
    ("right", 956, 1018),   # 8
    ("right", 1032, 1015),  # 9
    ("right", 1098, 1015),  # 10
    ("right", 1174, 1017),  # 11
    ("right", 1236, 1022),  # 12
]
BAG_ITEMS = [
    (1276, 966),
    (1343, 963),
    (1209, 1014),
    (1274, 1017),
    (1346, 1016),
    (1276, 966), # Adicional, se quiser expandir
]


POS_ORGANIZAR      = (1657, 974)
POS_ARRASTAR       = (1653, 629)
POS_SOLTAR_BAG     = (1284, 1052)
PAUSA_TEMPORARIA_BOSS = threading.Event()

bag_item_index = 0  # Índice para controle de uso dos itens

# ===== STATUS =====
def _status(msg: str):
    if ON_STATUS:
        try:
            ON_STATUS(status=f"{msg}")
        except Exception:
            pass

def _etapa():
    if ON_STATUS:
        try:
            ON_STATUS(etapa="kill_boss.py")
        except Exception:
            pass

# ===== CLIQUES =====
def _locate_center(path: str):
    try:
        return pg.locateCenterOnScreen(path, confidence=CONFIDENCE)
    except Exception:
        return None

def _image_exists(path: str) -> bool:
    try:
        return pg.locateOnScreen(path, confidence=CONFIDENCE) is not None
    except Exception:
        return False

def _after_click_move():
    try:
        pg.moveTo(POS_SOLTAR_BAG)
    except Exception:
        pass

def _click_point(x: int, y: int, button="left", delay: float = 0.1):
    try:
        pg.moveTo(x, y)
        time.sleep(0.1)  # Aguarda para garantir posicionamento
        atual = pg.position()
        if abs(atual.x - x) <= 5 and abs(atual.y - y) <= 5:
            pg.click(button=button)
        else:
            _status(f"⚠️ Posição incorreta antes do clique: atual={atual}, esperado=({x},{y})")
        time.sleep(delay)
    finally:
        _after_click_move()

def _click_center(button="left", delay: float = 0.1):
    sw, sh = pg.size()
    _click_point(sw // 2, sh // 2, button=button, delay=delay)

def _click_image(path: str, button="left", delay: float = 0.1) -> bool:
    pos = _locate_center(path)
    if pos:
        _click_point(pos.x, pos.y, button=button, delay=delay)
        return True
    return False

def usar_item_bag():
    global bag_item_index

    if bag_item_index >= len(BAG_ITEMS):
        _status("⚠️ Todos os itens da bag já foram usados")
        return

    item_pos = BAG_ITEMS[bag_item_index]
    _status(f"Usando item da bag na posição {bag_item_index + 1}: {item_pos}")

    # Clica para abrir envio de item
    for _ in range(2):
        _click_point(*item_pos, delay=0.1)
    time.sleep(0.4)

    # Organiza a bag
    _click_point(*POS_ORGANIZAR, delay=0.2)
    time.sleep(0.4)

    # Arrasta o item da posição atual para a área de soltura
    pg.moveTo(*POS_ARRASTAR)
    time.sleep(0.1)
    if pg.position() != pg.Point(*POS_ARRASTAR):
        _status("⚠️ Posição incorreta antes de arrastar")

    pg.mouseDown()
    time.sleep(0.2)
    pg.moveTo(*item_pos)
    time.sleep(0.1)
    if pg.position() != pg.Point(*item_pos):
        _status("⚠️ Posição incorreta antes de soltar")

    pg.mouseUp()
    time.sleep(0.2)
    _after_click_move()

    bag_item_index += 1


# ===== WATCHERS =====
def _lvlup_watcher(stop_evt: threading.Event):
    global PAUSA_KILL_BOSS, PAUSA_TEMPORARIA_BOSS
    _status("observando subir_nivel")
    estava_visivel = False

    while not stop_evt.is_set():
        visivel = _locate_center(IMG_SUBIR_NIVEL) is not None
        if visivel and not estava_visivel:
            _status("Herói upado — pausando fluxo do boss")
            PAUSA_TEMPORARIA_BOSS.set()
            PAUSA_KILL_BOSS.clear()
            upgrade.upgrade_personagem(on_status=ON_STATUS, origem="kill_boss", resume_event=PAUSA_KILL_BOSS)
            PAUSA_TEMPORARIA_BOSS.clear()
            _status("Upgrade concluído — retomando fluxo do boss")
        estava_visivel = visivel
        time.sleep(POLL_LVLUP)

def _boss_watcher(stop_evt: threading.Event):    
    global bag_item_index
    _status("boss watcher ativo — aguardando fim_game.png")
    estava_visivel = False

    while not stop_evt.is_set():
        PAUSA_KILL_BOSS.wait()
        if PAUSA_TEMPORARIA_BOSS.is_set():
            _status("⏸️ Pausa temporária para upgrade — aguardando liberação")
            PAUSA_TEMPORARIA_BOSS.wait()

        if _image_exists(IMG_FIM_GAME):
            _status("fim_game.png detectado — encerrando watcher")
            bag_item_index = 0
            break

        visivel = _locate_center(IMG_BOSS_ICON) is not None

        if visivel and not estava_visivel:
            _status("Boss visível — atacando")
            try:
                pg.press("f3")
                _click_center(button="right")
            except Exception:
                pass

        if not visivel and estava_visivel:
            _status("Boss morto — adiantando próximo")
            try:
                pg.press("f3")
                _click_center(button="right")

                # Verifica se houve pausa temporária antes de continuar
                if PAUSA_TEMPORARIA_BOSS.is_set():
                    _status("⏸️ Pausa temporária detectada — aguardando upgrade")
                    PAUSA_TEMPORARIA_BOSS.wait()

                _status("Upando Atributos")
                for tipo, x, y in CLICKS_POS_HEROI:
                    _click_point(x, y, button=tipo, delay=0.5)
                time.sleep(0.5)
                for _ in range(3):
                    _click_point(1539, 482, button="left", delay=0.5)
                time.sleep(0.5)
                _click_point(*POS_CONFIRMAR_BOSS, delay=0.2)
                usar_item_bag()
            except Exception as e:
                _status(f"Erro ao adiantar boss: {e}")
                raise

        estava_visivel = visivel
        time.sleep(POLL_BOSS)

# ===== EXECUÇÃO =====
def executar(on_status: Optional[Callable[..., None]] = None) -> tuple[bool, None]:
    global ON_STATUS
    ON_STATUS = on_status

    _etapa()

    try:
        _status("adiantando boss inicial")
        pg.press("f3")
        _click_center(button="right")
        time.sleep(0.5)
        _click_point(1539, 482, button="left", delay=0.5)
        _click_point(1539, 482, button="left", delay=0.5)
        _click_point(1539, 482, button="left", delay=0.5)
        time.sleep(0.5)
        _click_point(*POS_CONFIRMAR_BOSS, delay=0.2)
        usar_item_bag()

        stop_evt = threading.Event()
        threading.Thread(target=_lvlup_watcher, args=(stop_evt,), daemon=True).start()
        PAUSA_KILL_BOSS.set()
        _boss_watcher(stop_evt)
        stop_evt.set()
        
        _status("finalizado — fim_game.png encontrado")

        return True, None

    except pg.FailSafeException:
        _status("interrompido (failsafe)")
        return False, None
    except Exception as e:
        _status(f"erro: {type(e).__name__}")
        return False, None
        _status("finalizado — reiniciando fluxo")
        time.sleep(0.2)
        return executar(on_status=ON_STATUS)