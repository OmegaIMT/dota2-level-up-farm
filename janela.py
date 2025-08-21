# janela.py
# Requisitos: pip install pygetwindow
# Compatível com Windows 10/11

from typing import Optional, Callable
import time
import pygetwindow as gw

import new_game  # vamos manter para chamar direto quando focar

def encontrar_janela(titulo_substr: str, min_largura: int = 300, min_altura: int = 300):
    for w in gw.getWindowsWithTitle(titulo_substr):
        if getattr(w, "visible", False) and not w.isMinimized and w.width >= min_largura and w.height >= min_altura:
            return w
    return None

def janela_em_foco(win) -> bool:
    try:
        ativa = gw.getActiveWindow()
    except Exception:
        return False
    if not ativa or not win:
        return False
    return getattr(ativa, "_hWnd", None) == getattr(win, "_hWnd", None)

def focar_se_preciso(win, timeout: float = 2.0, intervalo: float = 0.05) -> bool:
    if not win:
        raise ValueError("Janela inválida (None).")
    if janela_em_foco(win):
        return False
    win.activate()
    fim = time.time() + timeout
    while time.time() < fim:
        if janela_em_foco(win):
            return True
        time.sleep(intervalo)
    return janela_em_foco(win)

def focar_se_preciso_por_titulo(titulo_substr: str,
                                min_largura: int = 300,
                                min_altura: int = 300,
                                timeout: float = 2.0,
                                intervalo: float = 0.05) -> Optional[bool]:
    win = encontrar_janela(titulo_substr, min_largura, min_altura)
    if not win:
        return None
    return focar_se_preciso(win, timeout, intervalo)

def executar(on_status: Optional[Callable[[str], None]] = None,
             titulo_substr: str = "Dota 2") -> bool:
    """
    1) Atualiza status para 'overlock do painel'
    2) Foca a janela do jogo
    3) Aguarda 3s
    4) Chama new_game.executar_jogo()
    """
    if on_status:
        on_status("Overlock do painel")
    print("Executando etapa: Overlock do painel...")

    if on_status:
        on_status("Iniciando o Jogo")
    focou = focar_se_preciso_por_titulo(titulo_substr)
    if focou is None:
        print("Janela não encontrada.")
        return False

    time.sleep(3)

    try:
        new_game.executar_jogo(on_status=on_status)
        return True
    except Exception as e:
        print(f"Erro ao iniciar new_game: {e}")
        return False

if __name__ == "__main__":
    executar(titulo_substr="Dota 2")