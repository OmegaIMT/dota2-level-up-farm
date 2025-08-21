import os
import time
import pyautogui as pg
from typing import Optional

# Configurações
CONFIDENCE_SKILL = 0.65  # Confiança para localizar skills
DELAY_APOS = 0.8

# Diretório de skills
DIR_SKILL = r"imagens\summon_skill"
IMG_CONFIRM = r"imagens\buttons\skill_confirm.png"

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

def _click_image(path: str, confidence: float, delay: float = 0.1) -> bool:
    pos = _locate_center(path, confidence)
    if pos:
        _click_point(pos.x, pos.y, delay=delay)
        return True
    return False

# Teste de seleção de skill
def testar_skill(on_status=None):
    time.sleep(1)
    if on_status:
        on_status("🔧 Testando seleção de skill")

    try:
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

                # Clica no botão de confirmação após selecionar a skill
                if on_status:
                    on_status("🖱️ Clicando botão de confirmação")
                _click_image(IMG_CONFIRM, confidence=CONFIDENCE_SKILL, delay=DELAY_APOS)
                break

        else:
            if on_status:
                on_status("⚠️ Skill não localizada — confirmando manualmente")
            _click_image(IMG_CONFIRM, confidence=CONFIDENCE_SKILL)
            time.sleep(DELAY_APOS)
            _after_click_move()

        if on_status:
            on_status("✅ Teste de skill finalizado")

    except Exception as e:
        if on_status:
            on_status(f"❌ Erro no teste de skill: {type(e).__name__}")

# Exemplo de uso
if __name__ == "__main__":
    testar_skill(print)