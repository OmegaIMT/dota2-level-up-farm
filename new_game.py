# new_game.py
# Requisitos: pip install pyautogui opencv-python

import time
import os
import argparse
from typing import Optional, Callable
import pyautogui as pg
import config  # precisa do config.mapa e config.ESCOLHER_MAPA

pg.FAILSAFE = True
pg.PAUSE = 0.05

# Imagens dos botões
IMG_INICIAR = r"imagens\\buttons\\iniciar.png"
IMG_INICIAR2 = r"imagens\\buttons\\iniciar2.png"

# Parâmetros de detecção e timing (Otimizados)
CONFIDENCE_BOTAO = 0.95
CONFIDENCE_MAPA = 0.93  # Evita confundir fontes parecidas (ex: 13 e 15)
RETRY_DELAY = 1.0
CLICK_DELAY = 1.0

# Callback de status
ON_STATUS: Optional[Callable[..., None]] = None


# ===== Funções auxiliares =====
def set_status(status: str):
    if ON_STATUS:
        try:
            ON_STATUS(etapa="new_game.py", status=status)
        except Exception:
            pass


def procurar_imagem(caminho_img, conf=CONFIDENCE_MAPA):
    try:
        return pg.locateOnScreen(caminho_img, confidence=conf)
    except Exception:
        return None


def listar_mapas_visiveis(pasta, conf=CONFIDENCE_MAPA):
    visiveis = []
    if not os.path.exists(pasta):
        return visiveis
    for arquivo in os.listdir(pasta):
        if arquivo.lower().endswith(".png"):
            caminho = os.path.join(pasta, arquivo)
            pos = procurar_imagem(caminho, conf=conf)
            if pos:
                visiveis.append((arquivo, pos))
    return visiveis


def numero_mapa(nome_arquivo):
    """Filtra apenas dígitos do nome do arquivo, evitando erros de tipo (None/String)."""
    try:
        nome_limpo = os.path.splitext(os.path.basename(nome_arquivo))[0]
        digits = "".join(c for c in nome_limpo if c.isdigit())
        return int(digits) if digits else 0
    except Exception:
        return 0


def escolher_mapa(conf=CONFIDENCE_MAPA):
    pasta_mapas = os.path.dirname(config.ESCOLHER_MAPA)
    
    # Extração segura do número do mapa desejado
    try:
        mapa_desejado = int("".join(c for c in str(config.mapa) if c.isdigit()))
    except Exception:
        mapa_desejado = 15  # Fallback seguro de sistema

    tentativas_scroll = 0
    while tentativas_scroll < 15:
        # 1. Tenta achar o arquivo exato correspondente ao mapa
        pos = procurar_imagem(config.ESCOLHER_MAPA, conf=conf)
        if pos:
            x, y = pg.center(pos)
            pg.moveTo(x, y)
            time.sleep(0.2)
            pg.click()
            set_status(f"Mapa {mapa_desejado} clicado")
            pg.moveTo(1312, 1053)
            return True

        # 2. Se não achar, lista os vizinhos para calcular aproximação
        visiveis = listar_mapas_visiveis(pasta_mapas, conf=conf)
        if not visiveis:
            set_status("Nenhum mapa visível - buscando...")
            time.sleep(1)
            tentativas_scroll += 1
            continue

        # Filtra a lista garantindo que não existam valores nulos ou falsos
        visiveis_numerados = []
        for nome, pos_mapa in visiveis:
            num = numero_mapa(nome)
            if num > 0:
                visiveis_numerados.append((nome, pos_mapa, num))

        if not visiveis_numerados:
            set_status("Mapas sem identificação válida")
            time.sleep(1)
            tentativas_scroll += 1
            continue

        # Cálculo matemático estritamente tipado contra int - None
        mais_proximo = min(visiveis_numerados, key=lambda x: abs(x[2] - mapa_desejado))
        nome, pos, num = mais_proximo
        
        x, y = pg.center(pos)
        pg.moveTo(x, y)
        time.sleep(0.2)
        pg.click()
        set_status(f"Clicando mapa {num} (prox. de {mapa_desejado})")
        pg.moveTo(1312, 1053)
        time.sleep(1.2)
        tentativas_scroll += 1

    set_status("Falha ao selecionar mapa após várias tentativas")
    return False


def clicar_imagem(caminho: str, confidence: float = CONFIDENCE_BOTAO, delay: float = CLICK_DELAY) -> bool:
    if not os.path.isfile(caminho):
        return False
    try:
        pos = pg.locateCenterOnScreen(caminho, confidence=confidence)
        if pos:
            pg.moveTo(pos.x, pos.y)
            time.sleep(0.3)
            pg.click()
            time.sleep(delay)
            return True
    except Exception:
        return False
    return False


def clicar_varias_vezes(caminho: str, vezes: int = 3, confidence: float = CONFIDENCE_BOTAO, delay: float = CLICK_DELAY):
    for _ in range(vezes):
        if not clicar_imagem(caminho, confidence=confidence, delay=delay):
            time.sleep(RETRY_DELAY / 2)


# ===== Fluxo principal =====
def executar_jogo(max_retries: int = 5, delay_after_click: float = CLICK_DELAY, on_status: Optional[Callable[..., None]] = None) -> bool:
    global ON_STATUS
    ON_STATUS = on_status

    set_status("iniciando")
    tentativas = 0

    try:
        set_status("escolhendo mapa")
        escolher_mapa()

        while tentativas < max_retries:
            set_status("esperando iniciar")
            time.sleep(3)
            set_status("buscando botão")

            if not clicar_imagem(IMG_INICIAR, confidence=CONFIDENCE_BOTAO, delay=delay_after_click):
                tentativas += 1
                set_status(f"botão não achado ({tentativas}/{max_retries})")
                time.sleep(2)
                continue

            set_status("clicou iniciar")
            set_status("confirmando")
            clicar_varias_vezes(IMG_INICIAR2, vezes=3, confidence=CONFIDENCE_BOTAO, delay=delay_after_click)

            set_status("carregando")
            time.sleep(6)

            set_status("finalizado")
            return True

        set_status("falha iniciar")
        return False

    except pg.FailSafeException:
        set_status("interrompido")
        return False
    except Exception as e:
        set_status(f"erro: {type(e).__name__}")
        return False


# Execução standalone
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--delay", type=float, default=0.0)
    parser.add_argument("--retries", type=int, default=5)
    parser.add_argument("--click-delay", type=float, default=CLICK_DELAY)
    args = parser.parse_args()

    if args.delay > 0:
        time.sleep(args.delay)

    executar_jogo(max_retries=args.retries, delay_after_click=args.click_delay)