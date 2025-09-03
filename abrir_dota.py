# abrir_dota.py
import os
import subprocess
import time
import config
import pyautogui

ETAPA_NOME = "abrir_dota.py"

def esperar_imagem_sem_timeout(nome_arquivo, pasta_base=None, conf=0.8):
    """Espera indefinidamente até encontrar a imagem na tela."""
    if pasta_base:
        caminho_img = os.path.join(pasta_base, nome_arquivo)
    else:
        caminho_img = os.path.join(config.INICIAR_JOGO, nome_arquivo)

    while True:
        try:
            pos = pyautogui.locateOnScreen(caminho_img, confidence=conf)
        except pyautogui.ImageNotFoundException:
            pos = None
        if pos:
            return pos
        time.sleep(1)

def clicar_centro(box):
    """Move o mouse até o centro da imagem e clica."""
    x, y = pyautogui.center(box)
    pyautogui.moveTo(x, y)  # movimento instantâneo
    time.sleep(0.05)
    pyautogui.click()

def executar_atalho_config():
    """Pressiona e solta a tecla/botão definido em config.auto_ataque."""
    if not hasattr(config, "auto_ataque"):
        return
    tecla = config.auto_ataque
    if not isinstance(tecla, str):
        return

    try:
        if tecla.startswith("x"):  # botão lateral do mouse
            pyautogui.mouseDown(button=tecla)
            time.sleep(0.05)
            pyautogui.mouseUp(button=tecla)
        else:  # tecla normal do teclado
            pyautogui.keyDown(tecla)
            time.sleep(0.05)
            pyautogui.keyUp(tecla)
    except Exception as e:
        print(f"Erro ao executar atalho: {e}")

def executar(on_status=None):
    if on_status:
        on_status(etapa=ETAPA_NOME, status="Abrindo Dota 2...")
    else:
        print("Abrindo Dota 2...")

    steam_exe = config.steam_exe
    if not os.path.isfile(steam_exe):
        if on_status:
            on_status(etapa=ETAPA_NOME, status=f"Steam não encontrada em {steam_exe}")
        else:
            print(f"Steam não encontrada em {steam_exe}")
        return False

    try:
        subprocess.Popen([steam_exe, "-applaunch", "570"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        if on_status:
            on_status(etapa=ETAPA_NOME, status=f"Erro ao abrir Dota 2: {type(e).__name__}")
        else:
            print(f"Erro ao abrir Dota 2: {e}")
        return False

    time.sleep(5)

    # Espera carregamento
    esperar_imagem_sem_timeout("carregado.png")

    # Sequência inicial de cliques
    for img in ["salao.png", "biblioteca.png", "jogo.png", "jogar.png", "aceitar.png", "mode.png"]:
        pos = esperar_imagem_sem_timeout(img)
        clicar_centro(pos)
        time.sleep(1)

    # Espera a imagem 'iniciar.png' na pasta BUTTONS
    pos_iniciar = esperar_imagem_sem_timeout("iniciar.png", pasta_base=config.BUTTONS)

    # Ao encontrar, executa o atalho e encerra
    executar_atalho_config()
    print("Atalho executado. Encerrando abrir_dota.py")
    return True

if __name__ == "__main__":
    executar()