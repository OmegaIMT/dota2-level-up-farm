import time
import threading
import sys
import keyboard
import argparse
import traceback
import psutil  # para checar se o Dota 2 e a Steam estão abertos

import janela
import farm_prata
import kill_boss
import fim_game
import config
import abrir_dota as dota
import abrir_steam as steam
import painel  # painel com transparência

# ======= Estado local =======
etapa_atual = "Inicializando"

def update_status(etapa=None, bag=None, status=None, reset_bag=False):
    if etapa is not None:
        config.etapa_atual = etapa
    if reset_bag:
        config.bag_index = 0
    if bag is not None:
        config.bag_index = bag
    if status is not None:
        config.status_msg = status
    if config.ciclo_max > 0 and config.ciclo >= config.ciclo_max:
        config.status_msg = "Ciclo máximo atingido. Encerrando..."
        fechar(None)

def is_dota_running():
    """Verifica se o processo do Dota 2 está ativo."""
    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'] and "dota2" in proc.info['name'].lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return False

def is_steam_running():
    """Verifica se a Steam está ativa."""
    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'] and "steam" in proc.info['name'].lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return False

# ======= Fluxo Principal =======
def executar_fluxo(etapa_inicial="janela"):
    etapas = ["dota", "janela", "farm", "kill_boss", "essencia", "fim_game"]
    indice_inicial = etapas.index(etapa_inicial)

    while not config.encerrar:
        for etapa in etapas[indice_inicial:]:
            if etapa == "dota":
                # Primeiro verifica se a Steam está aberta
                if not is_steam_running():
                    update_status(etapa="abrir_steam.py", status="Abrindo Steam...")
                    steam.executar(on_status=update_status)
                    time.sleep(2.5)

                # Depois verifica se o Dota está aberto
                if not is_dota_running():
                    update_status(etapa="abrir_dota.py", status="Abrindo Dota")
                    dota.executar(on_status=update_status)
                    time.sleep(2.5)
                else:
                    update_status(etapa="abrir_dota.py", status="Dota 2 já está aberto")
                    time.sleep(1)

            elif etapa == "janela":
                update_status(etapa="janela.py", status="Focando Janela")
                janela.executar(on_status=update_status)
                time.sleep(2.5)

            elif etapa == "farm":
                update_status(etapa="farm_prata.py", status="Iniciando Game", reset_bag=True)
                farm_prata.executar(on_status=update_status)
                time.sleep(2.5)

            elif etapa == "kill_boss":
                update_status(etapa="kill_boss.py", status="Matando Bosses")
                _, killed = kill_boss.executar(on_status=update_status)
                config.bag_index = killed
                time.sleep(2.5)

            elif etapa == "essencia":
                update_status(etapa="essencia.py", status="Farmando Essência")
                try:
                    import essencia
                    essencia.executar(on_status=update_status)
                    update_status(etapa="essencia.py", status="Essência finalizada")
                except Exception:
                    update_status(etapa="essencia.py", status="Erro ao executar essencia.py")
                time.sleep(2.5)

            elif etapa == "fim_game":
                update_status(etapa="fim_game.py", status="Finalizando Jogo")
                try:
                    fim_game.executar(on_status=update_status)
                except Exception as e:
                    update_status(status=f"Erro ao executar fim_game: {type(e).__name__}")
                    traceback.print_exc()

        config.ciclo += 1
        update_status(status="Reiniciando ciclo")
        indice_inicial = 0

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--etapa", type=str,
                        choices=["dota", "janela", "farm", "kill_boss", "essencia", "fim_game"],
                        default="dota")
    args = parser.parse_args()

    app = painel.criar_painel()  # painel com transparência
    keyboard.add_hotkey('esc', lambda: fechar(app))

    def iniciar_fluxo():
        threading.Thread(target=executar_fluxo, args=(args.etapa,), daemon=True).start()

    app.after(100, iniciar_fluxo)
    app.mainloop()

def fechar(app):
    config.encerrar = True
    if app:
        app.destroy()
    sys.exit(0)

if __name__ == "__main__":
    main()