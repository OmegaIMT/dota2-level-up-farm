import time
import config
import pyautogui

def esperar_imagem_sem_timeout(caminho_img, conf=0.8):
    """Fica procurando indefinidamente até encontrar a imagem na tela."""
    tentativas = 0
    while True:
        try:
            pos = pyautogui.locateOnScreen(caminho_img, confidence=conf)
        except pyautogui.ImageNotFoundException:
            pos = None

        if pos:
            return pos

        tentativas += 1
        if tentativas % 10 == 0:
            print(f"Aguardando imagem: {caminho_img}")
        time.sleep(1)

# --- Execução ---
print(f"Procurando mapa: {config.ESCOLHER_MAPA}")
pos = esperar_imagem_sem_timeout(config.ESCOLHER_MAPA, conf=0.96)
x, y = pyautogui.center(pos)
pyautogui.moveTo(x, y)
print(f"Mouse movido para o mapa {config.mapa} em ({x}, {y})")