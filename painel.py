# painel.py
import tkinter as tk
import ctypes
import config

def tornar_nao_interagivel(hwnd):
    """Deixa a janela transparente e sem interação com o mouse."""
    GWL_EXSTYLE = -20
    WS_EX_LAYERED = 0x00080000
    WS_EX_TRANSPARENT = 0x00000020
    LWA_ALPHA = 0x2
    user32 = ctypes.windll.user32
    estilo = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
    user32.SetWindowLongW(hwnd, GWL_EXSTYLE, estilo | WS_EX_LAYERED | WS_EX_TRANSPARENT)
    user32.SetLayeredWindowAttributes(hwnd, 0, 220, LWA_ALPHA)  # 220 = opacidade

def criar_painel():
    root = tk.Tk()
    root.overrideredirect(True)  # Remove bordas
    root.attributes("-topmost", True)  # Sempre no topo
    root.configure(bg="black")

    largura, altura = 300, 120
    sw = root.winfo_screenwidth()
    x = sw - largura - 20
    y = 20
    root.geometry(f"{largura}x{altura}+{x}+{y}")

    label = tk.Label(
        root,
        text="",
        font=("Consolas", 12),
        fg="#00FF6A",
        bg="black",
        justify="left",
        anchor="nw",
        padx=8,
        pady=6
    )
    label.pack(fill="both", expand=True)

    root.update_idletasks()
    try:
        tornar_nao_interagivel(root.winfo_id())
    except Exception:
        pass

    def atualizar():
        texto = (
            f"Etapa = {config.etapa_atual or '---'}\n"
            f"Ciclo: {config.ciclo} de {config.ciclo_max or '∞'}\n"
            f"Bag Index = {config.bag_index}\n"
            f"Hero Level = {config.level_heroi}\n"
            f"Status = {config.status_msg or '---'}\n"
            f"seta = {config.teste or '---'}\n"
            
        )
        label.config(text=texto)
        root.after(200, atualizar)

    atualizar()
    return root

def main():
    app = criar_painel()
    app.mainloop()

if __name__ == "__main__":
    main()