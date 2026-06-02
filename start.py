import json
import os
import customtkinter as ctk
from PIL import Image
import config  # Importa suas configurações globais
import subprocess
import sys

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.idiomas_disponiveis = self.load_available_languages()

        self.title("DotaLevelUpFarm v2.0")
        self.width, self.height = 450, 540
        self.geometry(f"{self.width}x{self.height}")
        self.resizable(False, False)
        self.configure(fg_color="#0d0d0d")

        self.bg_image = self.load_bg()
        if self.bg_image:
            self.bg_label = ctk.CTkLabel(self, image=self.bg_image, text="")
            self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        self.show_config_screen()

    def load_bg(self):
        path = os.path.join("img", "background", "icon.png")
        if os.path.exists(path):
            img = Image.open(path)
            return ctk.CTkImage(
                light_image=img, dark_image=img, size=(self.width, self.height)
            )
        return None

    def load_available_languages(self):
        path = os.path.join("language", "language.json")
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    dados = json.load(f)
                    return list(dados.values())
            except (json.JSONDecodeError, UnicodeDecodeError, OSError) as e:
                print(f"Error loading language.json: {e}")
        return ["en-US"]

    def clear_screen(self):
        for widget in self.winfo_children():
            if widget != getattr(self, "bg_label", None):
                widget.destroy()

    def show_config_screen(self):
        self.clear_screen()

        config_frame = ctk.CTkFrame(
            self, fg_color="transparent", border_width=0
        )
        config_frame.place(
            relx=0.5, rely=0.5, anchor="center", relwidth=0.85, relheight=0.95
        )

        ctk.CTkLabel(
            config_frame,
            text="Configuration Interface",
            font=("Roboto", 22, "bold"),
            text_color="white",
        ).pack(pady=(15, 15))

        # ---- MAPA ----
        ctk.CTkLabel(
            config_frame,
            text="Map Number (1 to 37):",
            font=("Roboto", 12, "bold"),
            text_color="#ccc",
        ).pack(anchor="w", padx=10)
        self.map_entry = ctk.CTkEntry(
            config_frame,
            placeholder_text="Ex: 15",
            width=320,
            fg_color="#141414",
            border_color="#333",
        )
        mapa_atual = str(int(getattr(config, "mapa", "1")))
        self.map_entry.insert(0, mapa_atual)
        self.map_entry.pack(pady=(2, 12))

        # ---- CICLOS ----
        ctk.CTkLabel(
            config_frame,
            text="Amount of Cycles (Repetitions): 0 = Infinite",
            font=("Roboto", 12, "bold"),
            text_color="#ccc",
        ).pack(anchor="w", padx=10)
        self.ciclos_entry = ctk.CTkEntry(
            config_frame,
            placeholder_text="Ex: 5",
            width=320,
            fg_color="#141414",
            border_color="#333",
        )
        ciclos_atuais = str(getattr(config, "ciclo_max", "1"))
        self.ciclos_entry.insert(0, ciclos_atuais)
        self.ciclos_entry.pack(pady=(2, 12))

        # ---- IDIOMA ----
        ctk.CTkLabel(
            config_frame,
            text="Select Language:",
            font=("Roboto", 12, "bold"),
            text_color="#ccc",
        ).pack(anchor="w", padx=10)
        self.lang_select = ctk.CTkOptionMenu(
            config_frame,
            values=self.idiomas_disponiveis,
            width=320,
            fg_color="#141414",
            button_color="#222",
            button_hover_color="#333",
        )
        if self.idiomas_disponiveis:
            self.lang_select.set(self.idiomas_disponiveis[0])
        self.lang_select.pack(pady=(2, 12))

        # ---- CHECKBOX: SPEED GAME ----
        self.check_speed = ctk.CTkCheckBox(
            config_frame,
            text="Increase Game Speed (Speed Game)",
            text_color="white",
            font=("Roboto", 12),
        )
        if getattr(config, "speed_game", False):
            self.check_speed.select()
        self.check_speed.pack(pady=(5, 20), anchor="w", padx=10)

        # ---- BOTÃO START ----
        btn_start = ctk.CTkButton(
            config_frame,
            text="START AUTOMATION",
            fg_color="#1f8a70",
            hover_color="#166351",
            command=self.start_bot,
            font=("Roboto", 14, "bold"),
            width=240,
            height=45,
        )
        btn_start.pack(pady=10)

    def salvar_config_no_arquivo(self, mapa_val, ciclos_val, speed_val):
        caminho_config = "config.py"
        if not os.path.exists(caminho_config):
            print("Error: config.py file not found!")
            return

        with open(caminho_config, "r", encoding="utf-8") as f:
            linhas = f.readlines()

        novas_linhas = []
        for linha in linhas:
            if linha.strip().startswith("mapa ="):
                novas_linhas.append(f'mapa = "{mapa_val:03d}"\n')
            elif linha.strip().startswith("ciclo_max ="):
                novas_linhas.append(f"ciclo_max = {ciclos_val}\n")
            elif linha.strip().startswith("speed_game ="):
                novas_linhas.append(f"speed_game = {str(speed_val)}\n")
            else:
                novas_linhas.append(linha)

        if not any(l.strip().startswith("speed_game =") for l in linhas):
            novas_linhas.append(f"\nspeed_game = {str(speed_val)}\n")

        with open(caminho_config, "w", encoding="utf-8") as f:
            f.writelines(novas_linhas)

    def executar_gerenciador(self):
        """Executa o auto_farm sem passar argumentos conflitantes na linha de comando"""
        try:
            # Em vez de passar argumentos que o argparse rejeita, usamos variáveis de ambiente.
            # Isso clona o ambiente atual do sistema e injeta uma flag limpa.
            env_atual = os.environ.copy()
            env_atual["EXECUTADO_PELO_START"] = "true"

            # Chama o auto_farm puro. Ele vai abrir o painel interno dele normalmente
            # e rodar sem que o argparse acuse erro.
            subprocess.Popen([sys.executable, "auto_farm.py"], env=env_atual)
            print("Interface: auto_farm.py iniciado com sucesso.")
        except Exception as e:
            print(f"Error launching auto_farm.py process: {e}")

    def start_bot(self):
        mapa_txt = self.map_entry.get()
        mapa_val = (
            int(mapa_txt)
            if mapa_txt.isdigit() and (1 <= int(mapa_txt) <= 37)
            else 1
        )

        ciclos_txt = self.ciclos_entry.get()
        ciclos_val = int(ciclos_txt) if ciclos_txt.isdigit() else 1

        speed_val = bool(self.check_speed.get() == 1)
        idioma_selecionado = self.lang_select.get()

        # Salva fisicamente e atualiza a RAM
        self.salvar_config_no_arquivo(mapa_val, ciclos_val, speed_val)
        config.mapa = f"{mapa_val:03d}"
        config.ciclo_max = ciclos_val
        config.speed_game = speed_val
        config.ESCOLHER_MAPA = f"imagens\\dota\\mapa\\{config.mapa}.png"

        print(
            f"Interface: Configs updated. Starting main engine... (Lang: {idioma_selecionado})"
        )

        # Minimiza a interface de configurações
        self.iconify()

        # Dispara o gerenciador
        self.executar_gerenciador()


if __name__ == "__main__":
    app = App()
    app.mainloop()