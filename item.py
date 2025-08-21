# item.py
# Requisitos: pip install pyautogui opencv-python

import os
import time
from typing import List, Tuple, Optional
import pyautogui as pg

# ================== CONFIGURAÇÕES ==================

# Nível de confiança para localizar imagens na tela
CONFIDENCE = 0.86
# Delay após arrastar um item (para evitar falhas de input)
DELAY_APOS_ARRASTAR = 0.2

# Coordenadas de cada um dos 6 slots de uso (na ordem solicitada)
USO_COORDS: List[Tuple[int, int]] = [
    (1207, 963),  # Slot uso1
    (1270, 960),  # Slot uso2
    (1346, 960),  # Slot uso3
    (1213, 1009), # Slot uso4
    (1268, 1007), # Slot uso5
    (1328, 1011), # Slot uso6
]

# Área da BAG (canto superior esquerdo X/Y, largura e altura)
BAG_X, BAG_Y, BAG_W, BAG_H = 1614, 602, 296, 424
# Pasta onde ficam as imagens da bag
BAG_DIR = r"imagens/item"

# Subpastas para cada uso com imagens de prioridade
USO_DIRS = [
    os.path.join(BAG_DIR, "uso1"),
    os.path.join(BAG_DIR, "uso2"),
    os.path.join(BAG_DIR, "uso3"),
    os.path.join(BAG_DIR, "uso4"),
    os.path.join(BAG_DIR, "uso5"),
    os.path.join(BAG_DIR, "uso6"),
]

# ================== FUNÇÕES INTERNAS ==================

def _listar_imgs(diretorio: str):
    """
    Lista caminhos de imagens no diretório informado.
    Retorna lista vazia se a pasta não existir ou estiver vazia.
    """
    if not os.path.exists(diretorio):
        return []
    try:
        arquivos = sorted(os.listdir(diretorio))
    except Exception:
        return []
    return [
        os.path.join(diretorio, arq)
        for arq in arquivos
        if os.path.isfile(os.path.join(diretorio, arq))
    ]

def _locate_center(path: str) -> Optional[pg.Point]:
    """
    Localiza o centro de uma imagem na tela.
    Retorna None se não encontrar ou em caso de erro.
    """
    try:
        return pg.locateCenterOnScreen(path, confidence=CONFIDENCE)
    except Exception:
        return None

def _image_exists(path: str) -> bool:
    """
    Verifica se a imagem existe na tela.
    Retorna False em caso de erro.
    """
    try:
        return pg.locateOnScreen(path, confidence=CONFIDENCE) is not None
    except Exception:
        return False

def _arrastar(origem: Tuple[int, int], destino: Tuple[int, int]):
    """
    Arrasta o item da posição 'origem' até a posição 'destino'.
    Protege contra exceções para não travar a execução.
    """
    try:
        pg.moveTo(origem[0], origem[1])
        pg.mouseDown()
        time.sleep(0.05)
        pg.moveTo(destino[0], destino[1])
        pg.mouseUp()
        time.sleep(DELAY_APOS_ARRASTAR)
    except Exception:
        pass

# ================== FUNÇÃO PRINCIPAL ==================

def organizar_usos():
    """
    Para cada slot de uso (1 a 6), verifica se já existe um item válido.
    Caso não exista, procura na bag o item correto (prioridade definida na pasta usoX)
    e arrasta para o slot.
    """
    # Percorre cada slot de uso e sua pasta de prioridade
    for idx, uso_dir in enumerate(USO_DIRS):
        imagens_prioridade = _listar_imgs(uso_dir)
        if not imagens_prioridade:
            continue  # Não existe pasta ou está vazia

        slot_coord = USO_COORDS[idx]

        # Se já existe um item válido no slot, pula para o próximo
        if any(_image_exists(img) for img in imagens_prioridade):
            continue

        # Caso contrário, procura o item na tela (na bag) e arrasta
        for img in imagens_prioridade:
            pos = _locate_center(img)
            if pos:
                _arrastar((pos.x, pos.y), slot_coord)
                break  # Passa para o próximo slot