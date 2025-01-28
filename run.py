import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk  # Para usar ícones personalizados
import subprocess
import os

# Dicionário para armazenar bots e seus processos
bots = {}

# Função para selecionar o arquivo do bot
def select_bot_file():
    file_path = filedialog.askopenfilename(title="Selecione o arquivo do bot", filetypes=(("Python files", "*.py"),))
    if file_path:
        bot_name = os.path.basename(os.path.dirname(file_path))  # Nome do diretório como nome do bot
        if bot_name not in bots:
            bots[bot_name] = {"path": os.path.dirname(file_path), "file": file_path, "process": None}
            bot_list.insert(tk.END, bot_name)
        else:
            messagebox.showwarning("Aviso", "Esse bot já está na lista!")

# Função para iniciar o bot
def start_bot():
    selected = bot_list.curselection()
    if not selected:
        messagebox.showwarning("Aviso", "Selecione um bot para iniciar!")
        return

    bot_name = bot_list.get(selected[0])
    bot_info = bots[bot_name]

    # Verifica se o bot já está em execução
    if bot_info["process"] is None or bot_info["process"].poll() is not None:
        try:
            # Inicia o processo do bot
            bot_info["process"] = subprocess.Popen(
                ["python", bot_info["file"]],
                cwd=bot_info["path"]
            )
            messagebox.showinfo("Sucesso", f"Bot '{bot_name}' iniciado!")
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
    bot_info = bots[bot_name]

    # Verifica se o bot está em execução
    if bot_info["process"] and bot_info["process"].poll() is None:
        bot_info["process"].terminate()
        bot_info["process"].wait()
        messagebox.showinfo("Sucesso", f"Bot '{bot_name}' parado!")
    else:
        messagebox.showwarning("Aviso", f"O bot '{bot_name}' não está em execução!")

# Função para carregar ícones
def load_icon(path, size=(20, 20)):
    img = Image.open(path)
    img = img.resize(size, Image.LANCZOS)
    return ImageTk.PhotoImage(img)

# Interface gráfica
app = tk.Tk()
app.title("Gerenciador de Bots Discord")
app.geometry("600x500")
app.configure(bg="#2b2b2b")  # Fundo escuro

# Cabeçalho
header = tk.Label(app, text="Gerenciador de Bots Discord", bg="#1f1f1f", fg="white", font=("Arial", 20, "bold"), pady=10)
header.pack(fill=tk.X)

# Carregar ícones
add_icon = load_icon("img/discord.png")
start_icon = load_icon("img/discord.png")
stop_icon = load_icon("img/discord.png")

# Botões
button_frame = tk.Frame(app, bg="#2b2b2b")
button_frame.pack(pady=10)

add_button = tk.Button(button_frame, text=" Adicionar Bot", image=add_icon, compound=tk.LEFT, command=select_bot_file, bg="#4caf50", fg="white", font=("Arial", 12), relief="groove", padx=10)
add_button.grid(row=0, column=0, padx=10)

start_button = tk.Button(button_frame, text=" Iniciar Bot", image=start_icon, compound=tk.LEFT, command=start_bot, bg="#4caf50", fg="white", font=("Arial", 12), relief="groove", padx=10)
start_button.grid(row=0, column=1, padx=10)

stop_button = tk.Button(button_frame, text=" Parar Bot", image=stop_icon, compound=tk.LEFT, command=stop_bot, bg="#f44336", fg="white", font=("Arial", 12), relief="groove", padx=10)
stop_button.grid(row=0, column=2, padx=10)

# Lista de bots
bot_list_frame = tk.Frame(app, bg="#2b2b2b")
bot_list_frame.pack(pady=10)

bot_list_label = tk.Label(bot_list_frame, text="Bots Adicionados", bg="#2b2b2b", fg="white", font=("Arial", 14))
bot_list_label.pack()

bot_list = tk.Listbox(bot_list_frame, height=15, width=50, bg="#1f1f1f", fg="white", font=("Arial", 12), selectbackground="#4caf50", selectforeground="white")
bot_list.pack(pady=10)

app.mainloop()
