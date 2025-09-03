# abrir_steam.py
import os
import subprocess
import time
import config
import pyautogui
import psutil  # pip install psutil

ETAPA_NOME = "abrir_steam.py"

def is_steam_running():
    """Verifica se a Steam já está aberta."""
    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'] and "steam" in proc.info['name'].lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return False

def esperar_imagem(nome_arquivo, timeout=30, conf=0.8):
    """Espera até encontrar a imagem na tela e retorna o box."""
    caminho_img = os.path.join(config.INICIAR_JOGO, nome_arquivo)
    inicio = time.time()
    while time.time() - inicio < timeout:
        try:
            pos = pyautogui.locateOnScreen(caminho_img, confidence=conf)
        except pyautogui.ImageNotFoundException:
            pos = None
        if pos:
            return pos
        time.sleep(1)
    return None

def clicar_extremo_direito(box, recuo=10):
    """Move instantaneamente o mouse um pouco antes do extremo direito e clica."""
    x = box.left + box.width - recuo
    y = box.top + box.height // 2
    pyautogui.moveTo(x, y)  # movimento instantâneo
    time.sleep(0.05)        # pequena pausa para segurança
    pyautogui.click()

def clicar_centro(box):
    """Move instantaneamente o mouse até o centro da imagem e clica."""
    x, y = pyautogui.center(box)
    pyautogui.moveTo(x, y)  # movimento instantâneo
    time.sleep(0.05)
    pyautogui.click()

def executar(on_status=None):
    # 1. Verifica se a Steam já está aberta
    if is_steam_running():
        if on_status:
            on_status(etapa=ETAPA_NOME, status="Steam já está aberta")
        else:
            print("Steam já está aberta")
        return True

    # 2. Abre a Steam
    caminho = config.steam_exe
    if not os.path.isfile(caminho):
        if on_status:
            on_status(etapa=ETAPA_NOME, status=f"Steam não encontrada em {caminho}")
        else:
            print(f"Steam não encontrada em {caminho}")
        return False

    # Apenas uma atualização no painel
    if on_status:
        on_status(etapa=ETAPA_NOME, status="Abrindo Steam...")
    else:
        print("Abrindo Steam...")

    subprocess.Popen([caminho], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(5)

    # 3. Espera a tela de conta (omega.png)
    pos_conta = esperar_imagem("omega.png", timeout=30)
    if not pos_conta:
        print("Conta não encontrada")
        return False
    clicar_centro(pos_conta)
    time.sleep(2)

    # 4. Espera Steam carregar (steam_carregada.png)
    pos_carregada = esperar_imagem("steam_carregada.png", timeout=60)
    if not pos_carregada:
        print("Não encontrou steam_carregada.png")
        return False

    # 5. Clica no botão "Ficar Off" (extremo direito)
    pos_ficar_off = esperar_imagem("ficar_off.png", timeout=20)
    if not pos_ficar_off:
        print("Não encontrou ficar_off.png")
        return False
    clicar_extremo_direito(pos_ficar_off, recuo=10)
    time.sleep(1)

    # 6. Clica no botão "Off"
    pos_off = esperar_imagem("off.png", timeout=20)
    if not pos_off:
        print("Não encontrou off.png")
        return False
    clicar_centro(pos_off)
    time.sleep(2)

    print("Steam iniciada no modo offline")
    return True

if __name__ == "__main__":
    executar()