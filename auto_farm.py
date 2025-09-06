import os
import time
import threading
import sys
import keyboard
import traceback
import psutil
import pyautogui
import argparse

import janela
import farm_prata
import kill_boss
import fim_game
import config
import abrir_dota as dota
import abrir_steam as steam
import painel

# ======= Atualiza status =======
def update_status(etapa=None, bag=None, status=None, reset_bag=False):
    if etapa: config.etapa_atual = etapa
    if reset_bag: config.bag_index = 0
    if bag is not None: config.bag_index = bag
    if status: config.status_msg = status
    if config.ciclo_max > 0 and config.ciclo >= config.ciclo_max:
        config.status_msg = "Ciclo máximo. Saindo..."
        fechar(None)

# ======= Verificações =======
def is_dota_running():
    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'] and "dota2" in proc.info['name'].lower():
                return True
        except:
            pass
    return False

def is_steam_running():
    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'] and "steam" in proc.info['name'].lower():
                return True
        except:
            pass
    return False

# ======= Monitor de seta =======
def monitor_seta():
    caminho_seta = os.path.join(config.REINICIAR, "seta.png")
    caminho_dog = os.path.join(config.REINICIAR, "dog.png")

    while not config.encerrar:
        for restante in range(180, 0, -1):
            if config.encerrar: 
                return
            minutos = restante // 60
            segundos = restante % 60
            config.teste = f"Próxima análise em: {minutos:02d}:{segundos:02d}"
            time.sleep(1)

        if not is_dota_running():
            config.teste = "Dota fechado. Reiniciando..."
            config.seta = True
            continue

        config.teste = "Buscando seta por 30s..."
        inicio = time.time()
        tempo_total = 30

        while time.time() - inicio < tempo_total and not config.encerrar:
            segundos = int(tempo_total - (time.time() - inicio))
            config.teste = f"Buscando seta... {segundos}s restantes"

            try:
                pos = pyautogui.locateOnScreen(caminho_seta, confidence=0.6)
            except:
                pos = None

            if pos:
                config.teste = "Seta encontrada. Clicando no dog..."
                try:
                    pos_dog = pyautogui.locateOnScreen(caminho_dog, confidence=0.6)
                except:
                    pos_dog = None

                if pos_dog:
                    x, y = pyautogui.center(pos_dog)
                    pyautogui.moveTo(x, y)                    
                    time.sleep(0.05)
                    pyautogui.click(x, y)
                    config.teste = f"Clique em dog ({x}, {y})"
                config.seta = True
                break

            time.sleep(1)

        if not config.seta:
            config.teste = "Seta não encontrada"

# ======= Fluxo principal =======
def executar_fluxo(etapa_inicial="dota"):
    etapas = ["dota", "janela", "farm", "kill_boss", "essencia", "fim_game"]
    if etapa_inicial not in etapas:
        etapa_inicial = "dota"

    while not config.encerrar:
        if config.seta:
            config.seta = False
            etapa_inicial = "dota"
            update_status(etapa="reinicio", status="Reiniciando...", reset_bag=True)
            time.sleep(1.5)
            continue

        for i in range(etapas.index(etapa_inicial), len(etapas)):
            if config.seta:
                config.seta = False
                etapa_inicial = "dota"
                update_status(etapa="reinicio", status="Reiniciando...", reset_bag=True)
                time.sleep(1.5)
                break  # sai do loop e reinicia tudo

            etapa = etapas[i]
            if etapa == "dota":
                if not is_steam_running():
                    update_status("abrir_steam.py", status="Abrindo Steam")
                    steam.executar(on_status=update_status)
                    time.sleep(2.5)

                if not is_dota_running():
                    update_status("abrir_dota.py", status="Abrindo Dota")
                    dota.executar(on_status=update_status)
                    time.sleep(2.5)
                else:
                    update_status("abrir_dota.py", status="Dota já aberto")
                    time.sleep(1)

            elif etapa == "janela":
                update_status("janela.py", status="Focando janela")
                janela.executar(on_status=update_status)
                time.sleep(2.5)

            elif etapa == "farm":
                update_status("farm_prata.py", status="Iniciando", reset_bag=True)
                farm_prata.executar(on_status=update_status)
                time.sleep(2.5)

            elif etapa == "kill_boss":
                update_status("kill_boss.py", status="Matando boss")
                _, killed = kill_boss.executar(on_status=update_status)
                config.bag_index = killed
                time.sleep(2.5)

            elif etapa == "essencia":
                update_status("essencia.py", status="Farmando essência")
                try:
                    import essencia
                    essencia.executar(on_status=update_status)
                    update_status("essencia.py", status="Essência ok")
                except:
                    update_status("essencia.py", status="Erro na essência")
                time.sleep(2.5)

            elif etapa == "fim_game":
                update_status("fim_game.py", status="Finalizando")
                try:
                    fim_game.executar(on_status=update_status)
                except Exception as e:
                    update_status(status=f"Erro fim_game: {type(e).__name__}")
                    traceback.print_exc()

        config.ciclo += 1
        update_status(status="Novo ciclo")
        etapa_inicial = "dota"

# ======= Inicialização =======
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--etapa", choices=["dota", "janela", "farm", "kill_boss", "essencia", "fim_game"],
                        help="Define a etapa inicial do fluxo")
    args = parser.parse_args()

    etapa_inicial = args.etapa if args.etapa else "dota"

    config.seta = False  # inicia limpo
    app = painel.criar_painel()
    keyboard.add_hotkey('esc', lambda: fechar(app))
    threading.Thread(target=monitor_seta, daemon=True).start()
    threading.Thread(target=executar_fluxo, args=(etapa_inicial,), daemon=True).start()
    app.mainloop()

def fechar(app):
    config.encerrar = True
    if app: 
        app.destroy()
    sys.exit(0)

if __name__ == "__main__":
    main()
