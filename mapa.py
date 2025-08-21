# mapa.py
# Requisitos: pip install opencv-python pillow numpy pyautogui keyboard

import time
import cv2
import numpy as np
import pyautogui
from PIL import ImageGrab
import os
import keyboard  # para detectar ESC

# =============================
# Configuração da área do minimapa
# =============================
MINIMAPA = (5, 821, 258, 1079)  # (x1, y1, x2, y2)
INTERVALO = 1.0  # intervalo entre buscas
THRESHOLD = 0.6  # precisão mínima para considerar que achou

# Pasta com os ícones para buscar
PASTA_ICONES = "imagens/mapa"

def capturar_minimapa():
    """Captura a região do minimapa e retorna como imagem OpenCV (BGR)."""
    img = ImageGrab.grab(bbox=MINIMAPA)
    frame = np.array(img)
    return cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

def encontrar_icone_no_minimapa(frame, icone_path, threshold=THRESHOLD):
    """Tenta localizar o ícone no minimapa usando matchTemplate."""
    icone = cv2.imread(icone_path, cv2.IMREAD_UNCHANGED)
    if icone is None:
        print(f"Não foi possível carregar: {icone_path}")
        return None

    # Converte para BGR se tiver 4 canais (ex.: PNG com transparência)
    if icone.ndim == 3 and icone.shape[2] == 4:
        icone = cv2.cvtColor(icone, cv2.COLOR_BGRA2BGR)

    try:
        res = cv2.matchTemplate(frame, icone, cv2.TM_CCOEFF_NORMED)
    except cv2.error as e:
        print(f"Erro ao comparar {icone_path}: {e}")
        return None

    loc = np.where(res >= threshold)
    for pt in zip(*loc[::-1]):
        return (MINIMAPA[0] + pt[0] + icone.shape[1] // 2,
                MINIMAPA[1] + pt[1] + icone.shape[0] // 2)
    return None

def loop_teste():
    icones = [os.path.join(PASTA_ICONES, f) for f in os.listdir(PASTA_ICONES)
              if f.lower().endswith((".png", ".jpg", ".jpeg"))]
    if not icones:
        print("Nenhum ícone encontrado na pasta:", PASTA_ICONES)
        return

    print("Iniciando teste... pressione ESC para parar.")
    while True:
        if keyboard.is_pressed("esc"):
            print("Parando execução...")
            break

        frame = capturar_minimapa()
        for icone_path in icones:
            pos = encontrar_icone_no_minimapa(frame, icone_path)
            if pos:
                print(f"Ícone encontrado: {icone_path} em {pos}")
                pyautogui.moveTo(pos[0], pos[1], duration=0.3)
                time.sleep(INTERVALO)
            else:
                print(f"Ícone não encontrado: {icone_path}")
        time.sleep(INTERVALO)

if __name__ == "__main__":
    loop_teste()