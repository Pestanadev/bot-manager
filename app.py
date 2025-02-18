import os
import time
import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import threading
from PIL import Image, ImageTk

# Dicionário para armazenar bots e seus processos
bots = {}

# Função para selecionar o arquivo do bot
def select_bot_file():
    file_path = filedialog.askopenfilename(title="Selecione o arquivo do bot", filetypes=(("Python files", "*.py"),))
    if file_path:
        bot_name = os.path.basename(os.path.dirname(file_path))  # Nome do diretório como nome do bot
        if bot_name not in bots:
            bots[bot_name] = {
                "path": os.path.dirname(file_path), 
                "file": file_path, 
                "process": None,
                "start_time": None,
                "last_online": "Nunca",
                "status_label": None,
                "status_thread": None  # Adicionado para armazenar a thread de status
            }
            update_bot_list()  # Atualiza a interface com o novo bot
        else:
            messagebox.showwarning("Aviso", "Esse bot já está na lista!")

# Atualiza a lista de bots na interface
def update_bot_list():
    # Limpa a Listbox
    bot_list.delete(0, tk.END)
    
    # Atualiza o status na interface
    for widget in status_frame.winfo_children():
        widget.destroy()

    for bot_name, bot_info in bots.items():
        # Adiciona o bot à Listbox
        bot_list.insert(tk.END, bot_name)

        row = tk.Frame(status_frame, bg="#2b2b2b")
        row.pack(fill=tk.X, pady=2)

        label = tk.Label(row, text=bot_name, bg="#2b2b2b", fg="white", font=("Arial", 12), width=20, anchor="w")
        label.pack(side=tk.LEFT, padx=10)

        status_label = tk.Label(row, text="🔴 Offline | Último início: Nunca", fg="red", bg="#2b2b2b", font=("Arial", 12))
        status_label.pack(side=tk.LEFT)

        bot_info["status_label"] = status_label  # Salva a referência do status

# Função para iniciar o bot
def start_bot():
    selected = bot_list.curselection()
    if not selected:
        messagebox.showwarning("Aviso", "Selecione um bot para iniciar!")
        return

    bot_name = bot_list.get(selected[0])
    bot_info = bots.get(bot_name)  # Buscar pelo nome correto

    if bot_info and (bot_info["process"] is None or bot_info["process"].poll() is not None):
        try:
            bot_info["process"] = subprocess.Popen(
                ["python", "-O", bot_info["file"]],
                cwd=bot_info["path"]
            )
            bot_info["start_time"] = time.time()
            update_status_display(bot_name)
            start_status_update_thread(bot_name)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao iniciar o bot: {e}")
    else:
        messagebox.showwarning("Aviso", f"O bot '{bot_name}' já está em execução!")

# Função para parar o bot
def stop_bot():
    selected = bot_list.curselection()
    if not selected:
        messagebox.showwarning("Aviso", "Selecione um bot para parar!")
        return

    bot_name = bot_list.get(selected[0])
    bot_info = bots.get(bot_name)

    if bot_info and bot_info["process"] and bot_info["process"].poll() is None:
        bot_info["process"].terminate()
        bot_info["process"].wait()
        bot_info["last_online"] = time.strftime("%d/%m/%Y %H:%M:%S")
        bot_info["start_time"] = None
        messagebox.showinfo("Sucesso", f"Bot '{bot_name}' parado!")
    else:
        messagebox.showwarning("Aviso", f"O bot '{bot_name}' não está em execução!")

# Função para remover o bot
def remove_bot():
    selected = bot_list.curselection()
    if not selected:
        messagebox.showwarning("Aviso", "Selecione um bot para remover!")
        return

    bot_name = bot_list.get(selected[0])
    del bots[bot_name]  # Remove o bot do dicionário
    update_bot_list()  # Atualiza a lista de bots na interface
    messagebox.showinfo("Sucesso", f"Bot '{bot_name}' removido com sucesso!")

# Atualiza o status do bot em tempo real
def update_status_display(bot_name):
    bot_info = bots.get(bot_name)
    if not bot_info:
        return

    if bot_info["status_label"]:
        if bot_info["process"] and bot_info["process"].poll() is None:
            bot_info["status_label"].config(text="🟢 Online", fg="green")
        else:
            bot_info["status_label"].config(text=f"🔴 Offline | Último início: {bot_info['last_online']}", fg="red")

# Atualiza o tempo online do bot em um loop separado
def start_status_update_thread(bot_name):
    def update():
        bot_info = bots[bot_name]  # Captura a referência ao bot_info uma vez
        while bot_info["process"] and bot_info["process"].poll() is None:
            elapsed_time = int(time.time() - bot_info["start_time"])
            hours, remainder = divmod(elapsed_time, 3600)
            minutes, seconds = divmod(remainder, 60)
            bot_info["status_label"].config(text=f"🟢 Online | Tempo: {hours:02d}:{minutes:02d}:{seconds:02d}", fg="green")
            time.sleep(1)
        bot_info["status_thread"] = None  # Garantir que a referência é limpa

    # Cria e inicia a thread
    thread = threading.Thread(target=update, daemon=True)  # Define a thread como daemon
    thread.start()
    bots[bot_name]["status_thread"] = thread  # Salva a referência da thread

# Função para carregar ícones
def load_icon(path, size=(20, 20)):
    img = Image.open(path)
    img = img.resize(size, Image.LANCZOS)
    return ImageTk.PhotoImage(img)

# Interface gráfica
app = tk.Tk()
app.title("Gerenciador de Bots")
app.geometry("600x500")
app.configure(bg="#2b2b2b")
app.iconbitmap("img/layer_icon_264857.ico")

header = tk.Label(app, text="Gerenciador de Bots", bg="#1f1f1f", fg="white", font=("Arial", 20, "bold"), pady=10)
header.pack(fill=tk.X)

button_frame = tk.Frame(app, bg="#2b2b2b")
button_frame.pack(pady=10)

# Carregando os ícones para os botões
add_icon = load_icon("img/add.ico")  # Coloque o caminho do ícone aqui
start_icon = load_icon("img/start.ico")  # Coloque o caminho do ícone aqui
stop_icon = load_icon("img/pause.ico")  # Coloque o caminho do ícone aqui
remove_icon = load_icon("img/remove.ico")  # Coloque o caminho do ícone aqui

add_button = tk.Button(button_frame, text=" Adicionar", image=add_icon, compound=tk.LEFT, command=select_bot_file, bg="#4caf50", fg="white", font=("Arial", 12), relief="groove", padx=10)
add_button.grid(row=0, column=0, padx=10)

start_button = tk.Button(button_frame, text=" Iniciar", image=start_icon, compound=tk.LEFT, command=start_bot, bg="#4caf50", fg="white", font=("Arial", 12), relief="groove", padx=10)
start_button.grid(row=0, column=1, padx=10)

stop_button = tk.Button(button_frame, text=" Parar", image=stop_icon, compound=tk.LEFT, command=stop_bot, bg="#f44336", fg="white", font=("Arial", 12), relief="groove", padx=10)
stop_button.grid(row=0, column=2, padx=10)

remove_button = tk.Button(button_frame, text=" Remover", image=remove_icon, compound=tk.LEFT, command=remove_bot, bg="#f44336", fg="white", font=("Arial", 12), relief="groove", padx=10)
remove_button.grid(row=0, column=3, padx=10)

bot_list_frame = tk.Frame(app, bg="#2b2b2b")
bot_list_frame.pack(pady=10)

bot_list_label = tk.Label(bot_list_frame, text="", bg="#2b2b2b", fg="white", font=("Arial", 14))
bot_list_label.pack()

bot_list = tk.Listbox(bot_list_frame, height=10, width=50, bg="#1f1f1f", fg="white", font=("Arial", 12), selectbackground="#4caf50", selectforeground="white")
bot_list.pack(pady=5)

status_frame = tk.Frame(app, bg="#2b2b2b")
status_frame.pack(pady=10)

app.protocol("WM_DELETE_WINDOW", app.quit)  # Apenas fecha a aplicação

app.mainloop()