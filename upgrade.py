import os
import time
import pyautogui as pg
import threading
from typing import Optional

# Configurações
CONFIDENCE_SKILL = 0.7  # Confiança para localizar skills
CONFIDENCE_HERO = 0.86   # Confiança para localizar heróis
DELAY_ENTRE = 0.1
DELAY_APOS = 0.8

# Diretórios
DIR_SKILL = r"imagens\\summon_skill"
DIR_HERO = r"imagens\\summon_hero"
IMG_CONFIRM = r"imagens\\buttons\\skill_confirm.png"

# Posições de clique
CLICKS_POS_HEROI = [
    ("left", 1723, 1050), ("right", 886, 935), ("right", 953, 944),
    ("right", 1029, 941), ("right", 1082, 943), ("right", 1159, 940),
    ("right", 1235, 932), ("right", 884, 1019), ("right", 956, 1018),
    ("right", 1032, 1015), ("right", 1098, 1015), ("right", 1174, 1017),
    ("right", 1236, 1022), ("left", 1723, 1050),
]

# Utilitários
def _locate_center(path: str, confidence: float) -> Optional[pg.Point]:
    try:
        return pg.locateCenterOnScreen(path, confidence=confidence)
    except Exception:
        return None

def _after_click_move():
    try:
        pg.moveTo(1284, 1052)
    except Exception:
        pass

def _click_point(x: int, y: int, button="left", delay: float = 0.1):
    pg.moveTo(x, y)
    time.sleep(0.1)
    pg.click(button=button)
    time.sleep(delay)
    _after_click_move()

def _click_center(delay: float = 0.1):
    sw, sh = pg.size()
    _click_point(sw // 2, sh // 2, delay=delay)

def _click_image(path: str, confidence: float, delay: float = 0.1) -> bool:
    pos = _locate_center(path, confidence)
    if pos:
        _click_point(pos.x, pos.y, delay=delay)
        return True
    return False

# Fluxo principal
def upgrade_personagem(on_status=None, origem="desconhecido", resume_event: Optional[threading.Event] = None) -> bool:
    time.sleep(1)
    if on_status:
        on_status("🔧 Iniciando upgrade de personagem")

    try:
        # Escolher skill
        arquivos_skill = sorted(f for f in os.listdir(DIR_SKILL) if f.lower().endswith(".png"))
        if on_status:
            on_status(f"{len(arquivos_skill)} skills disponíveis")

        for nome in arquivos_skill:
            caminho = os.path.join(DIR_SKILL, nome)
            if on_status:
                on_status(f"🔍skill: {nome}")
            pos = _locate_center(caminho, confidence=CONFIDENCE_SKILL)
            if pos:
                on_status(f"✅ Skill encontrada em {pos} — clicando")
                _click_point(pos.x, pos.y, delay=DELAY_APOS)
                time.sleep(DELAY_APOS)
                _click_image(IMG_CONFIRM, confidence=CONFIDENCE_SKILL)
                break
        else:
            if on_status:
                on_status("⚠️ Skill não localizada — confirmando manualmente")
            _click_image(IMG_CONFIRM, confidence=CONFIDENCE_SKILL)
            time.sleep(DELAY_APOS)
            _after_click_move()

        time.sleep(1)

        # Escolher herói
        arquivos_heroi = sorted(os.listdir(DIR_HERO))
        clicou_heroi = False
        for nome in arquivos_heroi:
            caminho = os.path.join(DIR_HERO, nome)
            if os.path.isfile(caminho):
                if on_status:
                    on_status(f"🔍herói: {nome}")
                pos = _locate_center(caminho, confidence=CONFIDENCE_HERO)
                if pos:
                    on_status(f"✅ Herói encontrado em {pos} — clicando")
                    _click_point(pos.x, pos.y, delay=DELAY_APOS)
                    clicou_heroi = True
                    break
                time.sleep(DELAY_ENTRE)

        if not clicou_heroi:
            if on_status:
                on_status("⚠️ Nenhum herói compatível — clicando centro")
            _click_center()

        # Atributos pós-herói
        if on_status:
            on_status("📈 Upando atributos")
        for tipo, x, y in CLICKS_POS_HEROI:
            _click_point(x, y, button=tipo, delay=0.2)

        if on_status:
            on_status(f"✅ Upgrade finalizado — origem: {origem}")
            _after_click_move()

        if resume_event and not resume_event.is_set():
            resume_event.set()
            if on_status:
                on_status("🔄 Retomando módulo kill_boss")

        return True

    except Exception as e:
        if on_status:
            on_status(f"❌ Erro no upgrade: {type(e).__name__}")
        if resume_event and not resume_event.is_set():
            resume_event.set()
            if on_status:
                on_status("⚠️ Retomando módulo kill_boss após erro")
        return False