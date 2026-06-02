import os
import subprocess
import time
import config
import pyautogui

ETAPA_NOME = "abrir_dota.py"


def esperar_abertura_e_clicar(nome_arquivo="abriu.png", conf=0.8):
    """Espera a imagem de abertura aparecer, depois espera ela sumir,
    aguarda 3 segundos e clica no centro da tela."""
    caminho_img = os.path.join(config.INICIAR_JOGO, nome_arquivo)

    # 1. Espera a imagem 'abriu.png' aparecer
    print("Aguardando a tela de abertura (abriu.png) aparecer...")
    while True:
        try:
            pos = pyautogui.locateOnScreen(caminho_img, confidence=conf)
        except pyautogui.ImageNotFoundException:
            pos = None
        if pos:
            break
        time.sleep(0.5)

    # 2. Espera a imagem 'abriu.png' sumir da tela
    print("Tela de abertura detectada. Aguardando ela sumir...")
    while True:
        try:
            pos = pyautogui.locateOnScreen(caminho_img, confidence=conf)
        except pyautogui.ImageNotFoundException:
            pos = None

        # Se pos for None, significa que a imagem sumiu
        if pos is None:
            break
        time.sleep(0.5)

    # 3. Espera 3 segundos após sumir
    print("Abertura sumiu. Aguardando 3 segundos...")
    time.sleep(3)

    # 4. Dá um clique no meio da tela
    largura, altura = pyautogui.size()
    centro_x, centro_y = largura // 2, altura // 2
    pyautogui.moveTo(centro_x, centro_y)
    time.sleep(0.05)
    pyautogui.click()
    print("Clique de foco no centro da tela executado.")


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
        subprocess.Popen(
            [steam_exe, "-applaunch", "570"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception as e:
        if on_status:
            on_status(
                etapa=ETAPA_NOME, status=f"Erro ao abrir Dota 2: {type(e).__name__}"
            )
        else:
            print(f"Erro ao abrir Dota 2: {e}")
        return False

    # Monitora a animação de abertura e foca a tela
    esperar_abertura_e_clicar("abriu.png")
    
    print("Dota iniciado com sucesso. Encerrando abrir_dota.py")
    return True


if __name__ == "__main__":
    executar()