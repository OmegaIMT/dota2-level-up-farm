# auto_farm.py
import time
import ctypes
import tkinter as tk
import threading
import sys
import keyboard
import argparse
import traceback


import janela
import farm
import kill_boss
import fim_game

# ======= Estado global =======
etapa_atual = "Inicializando"
ciclo = 0
bag_index = 0
status_msg = ""
encerrar = False

def update_status(etapa=None, bag=None, status=None, reset_bag=False):
    global etapa_atual, bag_index, status_msg
    if etapa is not None:
        etapa_atual = etapa
    if reset_bag:
        bag_index = 0
    if bag is not None:
        bag_index = bag
    if status is not None:
        status_msg = status

def tornar_nao_interagivel(hwnd):
    GWL_EXSTYLE = -20
    WS_EX_LAYERED = 0x00080000
    WS_EX_TRANSPARENT = 0x00000020
    LWA_ALPHA = 0x2
    user32 = ctypes.windll.user32
    estilo = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
    user32.SetWindowLongW(hwnd, GWL_EXSTYLE, estilo | WS_EX_LAYERED | WS_EX_TRANSPARENT)
    user32.SetLayeredWindowAttributes(hwnd, 0, 220, LWA_ALPHA)

def criar_overlay():
    root = tk.Tk()
    root.overrideredirect(True)
    root.attributes("-topmost", True)
    root.configure(bg="black")
    largura, altura = 280, 100
    sw = root.winfo_screenwidth()
    x = sw - largura - 10
    y = 10
    root.geometry(f"{largura}x{altura}+{x}+{y}")

    label = tk.Label(
        root, text="", font=("Consolas", 12),
        fg="#00FF6A", bg="black", justify="left", anchor="nw",
        padx=8, pady=6
    )
    label.pack(fill="both", expand=True)

    root.update_idletasks()
    try:
        tornar_nao_interagivel(root.winfo_id())
    except Exception:
        pass

    def atualizar():
        texto = (
            f"Etapa = {etapa_atual}\n"
            f"Ciclo Atual = {ciclo}\n"
            f"Bag Index = {bag_index}\n"
            f"Status = {status_msg}"
        )
        label.config(text=texto)
        root.after(200, atualizar)

    atualizar()
    return root

# ======= Fluxo Principal com etapa inicial =======
def executar_fluxo(etapa_inicial="janela"):
    global ciclo, bag_index, encerrar

    etapas = ["janela", "farm", "kill_boss", "essencia", "fim_game"]
    indice_inicial = etapas.index(etapa_inicial)

    while not encerrar:
        for etapa in etapas[indice_inicial:]:
            if etapa == "janela":
                update_status(etapa="janela.py", status="Focando Janela")
                janela.executar(on_status=update_status)
                time.sleep(2.5)

            elif etapa == "farm":
                update_status(etapa="farm.py", status="Farmando", reset_bag=True)
                farm.executar(on_status=update_status)
                time.sleep(2.5)

            elif etapa == "kill_boss":
                update_status(etapa="kill_boss.py", status="Matando Bosses")
                _, killed = kill_boss.executar(on_status=update_status)
                bag_index = killed
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


        ciclo += 1
        update_status(status="Reiniciando ciclo")
        indice_inicial = 0  # Após o primeiro ciclo, sempre começa do início

def main():
    global encerrar

    parser = argparse.ArgumentParser()
    parser.add_argument("--etapa", type=str, choices=["janela", "farm", "kill_boss", "essencia", "fim_game"], default="janela")
    args = parser.parse_args()

    app = criar_overlay()
    keyboard.add_hotkey('esc', lambda: fechar(app))

    def iniciar_fluxo():
        threading.Thread(target=executar_fluxo, args=(args.etapa,), daemon=True).start()

    app.after(100, iniciar_fluxo)
    app.mainloop()

def fechar(app):
    global encerrar
    encerrar = True
    if app:
        app.destroy()
    sys.exit(0)

if __name__ == "__main__":
    main()