import os
import time
import config
import pyautogui
import pygetwindow as gw  # <-- Importado para focar de forma independente

ETAPA_NOME = "iniciando_jogo.py"


def focar_janela_jogo(titulo_substr: str = "Dota 2") -> bool:
    """Procura a janela visível do jogo e traz para o primeiro plano."""
    try:
        for w in gw.getWindowsWithTitle(titulo_substr):
            if getattr(w, "visible", False) and not w.isMinimized and w.width >= 300:
                w.activate()
                print(f"[{ETAPA_NOME}] Janela '{titulo_substr}' focada com sucesso.")
                return True
    except Exception as e:
        print(f"[{ETAPA_NOME}] Erro ao tentar focar janela: {e}")
    return False


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


def ejecutar_atalho_config():
    """Pressiona e solta a tecla/botão definido in config.auto_ataque."""
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
        on_status(etapa=ETAPA_NOME, status="Focando janela do jogo...")
    else:
        print("Focando janela do jogo...")

    # ======= Garante o foco aqui dentro antes de interagir =======
    focar_janela_jogo("Dota 2")
    time.sleep(1.5)  # Tempo de resposta para o Windows processar o foco
    # ==================================================================

    if on_status:
        on_status(etapa=ETAPA_NOME, status="Aguardando menu carregado...")
    else:
        print("Aguardando menu carregado...")

    # Espera o carregamento do menu principal do jogo
    esperar_imagem_sem_timeout("carregado.png")

    if on_status:
        on_status(etapa=ETAPA_NOME, status="Navegando pelos menus...")

    # Sequência inicial de cliques
    for img in [
        "salao.png",
        "biblioteca.png",
        "jogo.png",
        "jogar.png",
        "aceitar.png",
        "mode.png",
    ]:
        pos = esperar_imagem_sem_timeout(img)
        clicar_centro(pos)
        time.sleep(1)

    # ======= MODIFICADO: Busca na pasta exata imagens\buttons\Iniciar.png =======
    if on_status:
        on_status(etapa=ETAPA_NOME, status="Aguardando botão Iniciar...")
    else:
        print("Aguardando botão Iniciar...")

    pasta_buttons = os.path.join("imagens", "buttons")
    pos_iniciar = esperar_imagem_sem_timeout("Iniciar.png", pasta_base=pasta_buttons)

    # Ao encontrar a imagem, executa o atalho e encerra a etapa imediatamente
    ejecutar_atalho_config()
    print(f"[{ETAPA_NOME}] Imagem 'Iniciar.png' encontrada. Atalho executado. Encerrando etapa.")
    return True


if __name__ == "__main__":
    executar()