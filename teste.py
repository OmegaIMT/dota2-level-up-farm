import pyautogui as pg
import time
import os

# Caminho da nova pasta
PASTA_IMAGENS = r"D:\wamp64\www\python\teste"

# Precisão da detecção
CONFIDENCE = 0.9

def procurar_e_mover():
    print("🔍 Procurando imagens PNG na tela...")

    imagens = [f for f in os.listdir(PASTA_IMAGENS) if f.lower().endswith(".png")]

    if not imagens:
        print("⚠️ Nenhuma imagem PNG encontrada na pasta.")
        return

    while True:
        encontrado = False
        for imagem in imagens:
            caminho = os.path.join(PASTA_IMAGENS, imagem)
            try:
                pos = pg.locateCenterOnScreen(caminho, confidence=CONFIDENCE)
                if pos:
                    print(f"✅ Encontrado: {imagem} — movendo mouse para {pos}")
                    pg.moveTo(pos.x, pos.y)
                    encontrado = True
                    break
            except Exception as e:
                print(f"Erro ao procurar {imagem}: {e}")

        if not encontrado:
            print("⏳ Nenhuma imagem encontrada — tentando novamente...")
        time.sleep(1)

if __name__ == "__main__":
    try:
        procurar_e_mover()
    except KeyboardInterrupt:
        print("\n🛑 Encerrado pelo usuário.")