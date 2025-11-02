# config.py

# ======= Estado global =======
ciclo = 0
bag_index = 0
level_heroi = 0
status_msg = ""
encerrar = False
ciclo_max = 0  # 0 para ciclos infinitos
prioridade = 1  # 1 - farm de prata, 2 - farm de essência
essencia_time = 300  # tempo em segundos para farmar essência
seta = False  # usado para reiniciar o Script
resolucao = 1  # 1 = 1920x1080, 2 = 1600x900, 3 = 1366x768, 4 = 1280x720, 5 = 1024x768, 6 = 800x600
mapa_config = 1  # 1 = N1 à N8, 2 = N9+
hammer = False  # True = usar martelo
pill = False  # True = usar pílula
etapa_atual = ""  # Etapa atual do fluxo
steam_exe = r"C:\Program Files (x86)\Steam\Steam.exe" # Caminho do executável da Steam# config.py
auto_ataque = "k"
mapa = "012"
teste = ""

# ======= Diretórios de imagens =======
BUTTONS = r"imagens\\buttons\\"
BOSS = r"imagens\\boss\\"
MAPA = r"imagens\\mapa\\"
SKILLS = r"imagens\\skill_game\\"
SUMMON_HERO = r"imagens\\heros_game\\"
TESOUROS = r"imagens\\tesouro\\"
INICIAR_JOGO = r"imagens\\dota\\"
ESCOLHER_MAPA = f"imagens\\dota\\mapa\\{mapa}.png"
REINICIAR = r"imagens\\buttons\\setas"

# ======= Posição da moeda de ouro =======
ouro = (1722, 1048)

# ======= Posições dos upgrades do Tech Shop =======
upgrade = {
    "ganho_ouro": (877, 940),
    "aumento_atk": (960, 940),
    "atk_speed": (1102, 945),
    "life_steal": (1028, 940),
    "penetracao": (1173, 1022),
    "atk_range": (957, 1017),
    "str": (1170, 945),
    "agi": (1234, 946),
    "int": (883, 1017),
    "hp": (1030, 1017),
    "mana": (1100, 1011),
    "armor": (1237, 1022)
}

# ======= Bag Index por nível de mapa =======
BAG_ITEMS_N9_PLUS = [
    (1314, 960),  # index 0
    (1314, 960),  # index 1
    (1375, 960),  # index 2
    (1251, 1009), # index 3
    (1313, 1009), # index 4
    (1382, 1009)  # index 5
]

BAG_ITEMS_N1_N8 = [
    (1276, 966),  # index 0
    (1276, 966),  # index 1
    (1343, 966),  # index 2
    (1209, 1015), # index 3
    (1274, 1015), # index 4
    (1346, 1015)  # index 5
]

# ======= Descanso por nível de mapa =======
DESCANSO_N9_PLUS = (1312, 1053)
DESCANSO_N1_N8 = (1284, 1053)

# ======= Funções utilitárias =======
def get_bag_items():
    return BAG_ITEMS_N9_PLUS if mapa_config == 2 else BAG_ITEMS_N1_N8

def get_descanso():
    return DESCANSO_N9_PLUS if mapa_config == 2 else DESCANSO_N1_N8