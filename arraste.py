from pynput import mouse, keyboard

ARQUIVO_LOG = "cliques.txt"

executando = True
contador = 1  # numeração dos cliques

def salvar_linha(texto):
    print(texto)
    with open(ARQUIVO_LOG, "a", encoding="utf-8") as f:
        f.write(texto + "\n")

def on_click(x, y, button, pressed):
    global contador
    if pressed:
        salvar_linha(f"{contador} - ({x}, {y})")
        contador += 1

def on_press(tecla):
    global executando
    if tecla == keyboard.Key.esc:
        print("ESC pressionado. Encerrando...")
        executando = False
        return False

# Listener de mouse
listener_mouse = mouse.Listener(on_click=on_click)
listener_mouse.start()

# Listener de teclado
with keyboard.Listener(on_press=on_press) as listener_teclado:
    while executando:
        pass

listener_mouse.stop()