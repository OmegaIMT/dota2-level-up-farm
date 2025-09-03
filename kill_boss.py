# kill_boss.py
# Requisitos: pip install pyautogui opencv-python

import time
import threading
from typing import Optional, Callable
import pyautogui as pg
import upgrade

# Imagens
IMG_SUBIR_NIVEL = r"imagens\\buttons\\subir_nivel.png"
IMG_BOSS_ICON = r"imagens\\boss\\boss.png"
IMG_FIM_GAME = r"imagens\\buttons\\fim_game.png"

# Configurações
CONFIDENCE = 0.7
POLL_LVLUP = 0.6
POLL_BOSS = 0.5
PAUSA_KILL_BOSS = threading.Event()
PAUSA_TEMPORARIA_BOSS = threading.Event()
ON_STATUS: Optional[Callable[..., None]] = None

# Posições fixas
POS_CONFIRMAR_BOSS = (841, 584)
CLICKS_POS_HEROI = [
    ("left", 1723, 1050),
    ("right", 886, 935),
    ("right", 953, 944),
    ("right", 1029, 941),
    ("right", 1082, 943),
    ("right", 1159, 940),
    ("right", 1235, 932),
    ("right", 884, 1019),
    ("right", 956, 1018),
    ("right", 1032, 1015),
    ("right", 1098, 1015),
    ("right", 1174, 1017),
    ("right", 1236, 1022),
]
BAG_ITEMS = [
    (1314, 960),  # index 0
    (1314, 960),  # index 1
    (1375, 960),  # index 2
    (1251, 1009), # index 3
    (1313, 1009), # index 4
    (1382, 1009)  # index 5
]
POS_ORGANIZAR = (1657, 974)


# ===== STATUS =====
def _status(msg: str):
    if ON_STATUS:
        try:
            ON_STATUS(status=msg)
        except Exception:
            pass


def _etapa():
    if ON_STATUS:
        try:
            ON_STATUS(etapa="kill_boss.py")
        except Exception:
            pass


def _atualizar_bag_index(index: int):
    if ON_STATUS:
        try:
            ON_STATUS(bag=index)
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
        pg.moveTo(1312, 1053)
    except Exception:
        pass


def _click_point(x: int, y: int, button="left", delay: float = 0.1):
    try:
        pg.moveTo(x, y)
        time.sleep(0.1)
        atual = pg.position()
        if abs(atual.x - x) <= 5 and abs(atual.y - y) <= 5:
            pg.click(button=button)
        else:
            _status(
                f"⚠️ Posição incorreta antes do clique: atual={atual}, esperado=({x},{y})"
            )
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


def usar_item_bag(index: int) -> int:
    if index >= len(BAG_ITEMS):
        _status("⚠️ Bag Cheia")
        return index

    item_pos = BAG_ITEMS[index]
    _status(f"Usando Item {index + 1}: {item_pos}")

    # Clique duplo no slot da bag
    for _ in range(2):
        _click_point(*item_pos, delay=0.1)
    time.sleep(0.5)

    # Organiza os itens
    _click_point(*POS_ORGANIZAR, delay=0.3)
    time.sleep(0.5)

    # Arrasta da posição fixa para o slot da bag
    pg.moveTo(1640, 627)
    time.sleep(0.5)
    pg.mouseDown()
    time.sleep(0.5)
    pg.moveTo(*item_pos)
    time.sleep(0.5)
    pg.mouseUp()
    time.sleep(0.5)
    pg.moveTo(1284, 1052)

    index += 1
    _atualizar_bag_index(index)
    return index


# ===== WATCHERS =====
def _lvlup_watcher(stop_evt: threading.Event):
    _status("observando subir_nivel")
    estava_visivel = False

    while not stop_evt.is_set():
        visivel = _locate_center(IMG_SUBIR_NIVEL) is not None
        if visivel and not estava_visivel:
            _status("Herói upado — pausando fluxo do boss")
            PAUSA_TEMPORARIA_BOSS.set()
            PAUSA_KILL_BOSS.clear()
            upgrade.upgrade_personagem(
                on_status=ON_STATUS, origem="kill_boss", resume_event=PAUSA_KILL_BOSS
            )
            PAUSA_TEMPORARIA_BOSS.clear()
            _status("Upgrade concluído")
        estava_visivel = visivel
        time.sleep(POLL_LVLUP)


def _boss_watcher(stop_evt: threading.Event, index: int) -> int:
    _status("Aguardadno Boss")
    estava_visivel = False

    while not stop_evt.is_set():
        PAUSA_KILL_BOSS.wait()
        if PAUSA_TEMPORARIA_BOSS.is_set():
            _status("Upando Heroi")
            PAUSA_TEMPORARIA_BOSS.wait()

        if _image_exists(IMG_FIM_GAME):
            _status("Fim de Jogo")
            _atualizar_bag_index(index)
            break

        visivel = _locate_center(IMG_BOSS_ICON) is not None

        if visivel and not estava_visivel:
            _status("Atacando Boss")
            try:
                pg.press("f3")
                _click_center(button="right")
            except Exception:
                pass

        if not visivel and estava_visivel:
            _status("Evoncando Boss")
            try:
                pg.press("f3")
                _click_center(button="right")

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
                index = usar_item_bag(index)
            except Exception as e:
                _status(f"Erro ao adiantar boss: {e}")
                raise

        estava_visivel = visivel
        time.sleep(POLL_BOSS)

    return index


def executar(on_status: Optional[Callable[..., None]] = None) -> tuple[bool, int]:
    global ON_STATUS
    ON_STATUS = on_status

    _etapa()
    bag_index = 0

    try:
        _status("adiantando boss inicial")
        pg.press("f3")
        _click_center(button="right")
        time.sleep(0.5)
        for _ in range(3):
            _click_point(1539, 482, button="left", delay=0.5)
        time.sleep(0.5)
        _click_point(*POS_CONFIRMAR_BOSS, delay=0.2)
        bag_index = usar_item_bag(bag_index)

        stop_evt = threading.Event()
        threading.Thread(target=_lvlup_watcher, args=(stop_evt,), daemon=True).start()
        PAUSA_KILL_BOSS.set()
        bag_index = _boss_watcher(stop_evt, bag_index)
        stop_evt.set()

        _status("finalizado — fim_game.png encontrado")
        return True, bag_index

    except pg.FailSafeException:
        _status("interrompido (failsafe)")
        return False, bag_index

    except Exception as e:
        _status(f"erro: {type(e).__name__}")
        return False, bag_index
