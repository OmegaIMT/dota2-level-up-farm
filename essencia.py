from typing import Optional, Callable
import time
import pyautogui as pg

# Posições fixas
POS_PROCURAR_FARM = (722, 589)
POS_ESCOLHER_FARM = (961, 516)
POS_INICIAR_FARM  = (961, 696)
POS_FINALIZAR     = (956, 641)

def _click_point(x: int, y: int, delay: float = 0.1):
    pg.moveTo(x, y)
    time.sleep(0.3)
    pg.click()
    time.sleep(delay)

def _click_center_right(delay: float = 0.1):
    sw, sh = pg.size()
    pg.moveTo(sw // 2, sh // 2)
    time.sleep(0.3)
    pg.click(button='right')
    time.sleep(delay)

def executar(on_status: Optional[Callable[..., None]] = None) -> bool:
    if on_status:
        on_status(etapa="essencia.py", status="Iniciando farm de essência")

    _click_point(*POS_PROCURAR_FARM, delay=0.3)
    _click_point(*POS_ESCOLHER_FARM, delay=0.3)
    _click_point(*POS_INICIAR_FARM, delay=0.3)
    _click_center_right(delay=0.3)  # Clique com botão direito no centro

    # Contagem regressiva de 240 segundos
    for i in range(240, 0, -1):
        if on_status:
            on_status(status=f"Finalizando em: {i}s")
        time.sleep(1)

    if on_status:
        on_status(status="Finalizando farm de essência")

    pg.press("f3")
    time.sleep(2)
    _click_point(*POS_FINALIZAR, delay=0.3)
    time.sleep(2)

    return True  # ← Isso permite que o auto_farm saiba que terminou