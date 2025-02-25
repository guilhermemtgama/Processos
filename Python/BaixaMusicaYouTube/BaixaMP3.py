import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from yt_dlp import YoutubeDL
from threading import Thread
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
from imageio_ffmpeg import get_ffmpeg_exe
import logging

# Configuração da janela principal
root = ttkb.Window(themename="minty")  # Tema moderno e colorido
root.title("Music Dashboard")
root.geometry("1000x700")  # Tamanho da janela
root.resizable(False, False)  # Impede redimensionamento

# Variáveis globais
downloads = []  # Lista de downloads
current_download = {"active": False, "music": None, "artist": None}
download_folder = "Downloads"  # Pasta padrão para downloads
statistics = {"total_downloads": 0, "total_errors": 0}  # Estatísticas de uso

# Configuração de logging
logging.basicConfig(filename="errors.log", level=logging.ERROR)

# Função para validar entrada
def validate_input(music, artist):
    if not music:
        messagebox.showwarning("Aviso", "O campo 'Nome da Música' é obrigatório.")
        return False
    return True

# Função para baixar música
def download_music():
    music = entry_music.get().strip()
    artist = entry_artist.get().strip() or "Desconhecido"
    quality = quality_var.get()

    if not validate_input(music, artist):
        return

    # Adiciona à lista de downloads
    downloads.append({"music": music, "artist": artist, "status": "Pendente", "progress": 0, "quality": quality})
    update_table()

    # Inicia o download em uma nova thread
    if not current_download["active"]:
        start_download()

# Função para iniciar o download
def start_download():
    if current_download["active"] or not downloads:
        return

    # Pega o próximo download pendente
    for download in downloads:
        if download["status"] == "Pendente":
            current_download["active"] = True
            current_download["music"] = download["music"]
            current_download["artist"] = download["artist"]
            download["status"] = "Baixando"
            update_table()

            # Inicia o download em uma nova thread
            Thread(target=perform_download, args=(download,)).start()
            break

# Função para realizar o download
def perform_download(download):
    try:
        # Configurações do yt-dlp
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(download_folder, f"{download['artist']} - {download['music']}.%(ext)s"),
            'ffmpeg_location': get_ffmpeg_exe(),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': download["quality"],
            }],
            'progress_hooks': [lambda d: progress_hook(d, download)],  # Atualiza o progresso
        }

        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([f"ytsearch:{download['music']} {download['artist']}"])

        download["status"] = "Concluído"
        download["progress"] = 100
        statistics["total_downloads"] += 1
    except Exception as e:
        download["status"] = f"Erro: {e}"
        statistics["total_errors"] += 1
        logging.error(f"Erro durante o download: {e}")
    finally:
        current_download["active"] = False
        update_table()
        update_statistics()
        start_download()  # Inicia o próximo download

# Função para atualizar o progresso
def progress_hook(d, download):
    if d['status'] == 'downloading':
        total = d.get('total_bytes', 1)
        downloaded = d.get('downloaded_bytes', 0)
        percent = int(downloaded * 100 / total)
        download["progress"] = percent
        update_table()

# Função para atualizar a tabela de downloads
def update_table():
    for row in table.get_children():
        table.delete(row)

    for idx, download in enumerate(downloads):
        table.insert("", "end", values=(
            idx + 1,
            download["music"],
            download["artist"],
            download["status"],
            f"{download['progress']}%"
        ))

    # Atualiza a barra de progresso geral
    total_progress = sum(download["progress"] for download in downloads) / len(downloads) if downloads else 0
    progress_bar["value"] = total_progress
    progress_label.config(text=f"Progresso geral: {int(total_progress)}%")

# Função para atualizar estatísticas
def update_statistics():
    stats_label.config(text=f"Total de Downloads: {statistics['total_downloads']} | Erros: {statistics['total_errors']}")

# Função para selecionar pasta de download
def select_folder():
    global download_folder
    folder = filedialog.askdirectory()
    if folder:
        download_folder = folder
        folder_label.config(text=f"Pasta: {folder}")

# Função para limpar a fila de downloads concluídos
def clear_queue():
    global downloads
    downloads = [d for d in downloads if d["status"] != "Concluído"]
    update_table()

# Layout da interface
frame_top = ttkb.Frame(root)
frame_top.pack(pady=20, padx=20, fill="x")

# Título do Dashboard
label_title = ttkb.Label(frame_top, text="MUSIC HITS", font=("Helvetica", 24, "bold"), bootstyle="primary")
label_title.pack(pady=10)

# Campos de entrada
frame_input = ttkb.Frame(frame_top)
frame_input.pack(pady=10)

label_music = ttkb.Label(frame_input, text="Nome da Música:", font=("Helvetica", 12), bootstyle="primary")
label_music.grid(row=0, column=0, padx=5, pady=5, sticky="w")

entry_music = ttkb.Entry(frame_input, width=40, font=("Helvetica", 12))
entry_music.grid(row=0, column=1, padx=5, pady=5)

label_artist = ttkb.Label(frame_input, text="Artista (opcional):", font=("Helvetica", 12), bootstyle="primary")
label_artist.grid(row=1, column=0, padx=5, pady=5, sticky="w")

entry_artist = ttkb.Entry(frame_input, width=40, font=("Helvetica", 12))
entry_artist.grid(row=1, column=1, padx=5, pady=5)

# Seleção de qualidade
label_quality = ttkb.Label(frame_input, text="Qualidade (kbps):", font=("Helvetica", 12), bootstyle="primary")
label_quality.grid(row=2, column=0, padx=5, pady=5, sticky="w")

quality_var = tk.StringVar(value="192")
quality_menu = ttkb.Combobox(frame_input, textvariable=quality_var, values=["128", "192", "320"], bootstyle="primary")
quality_menu.grid(row=2, column=1, padx=5, pady=5)

# Botão de download
button_download = ttkb.Button(frame_input, text="Baixar", command=download_music, bootstyle="success", width=10)
button_download.grid(row=3, column=0, columnspan=2, pady=10)

# Botão para selecionar pasta
folder_button = ttkb.Button(frame_input, text="Selecionar Pasta", command=select_folder, bootstyle="info")
folder_button.grid(row=4, column=0, padx=5, pady=5)

folder_label = ttkb.Label(frame_input, text=f"Pasta: {download_folder}", font=("Helvetica", 10), bootstyle="primary")
folder_label.grid(row=4, column=1, padx=5, pady=5)

# Tabela de downloads
frame_table = ttkb.Frame(root)
frame_table.pack(pady=20, padx=20, fill="both", expand=True)

columns = ("ID", "Música", "Artista", "Status", "Progresso")
table = ttk.Treeview(frame_table, columns=columns, show="headings", height=10)
table.pack(fill="both", expand=True)

# Configuração das colunas
for col in columns:
    table.heading(col, text=col)
    table.column(col, anchor="center", width=100)

# Barra de progresso geral
progress_bar = ttkb.Progressbar(root, orient=HORIZONTAL, length=500, mode="determinate", bootstyle="success-striped")
progress_bar.pack(pady=10)

# Label para mostrar o progresso geral
progress_label = ttkb.Label(root, text="Progresso geral: 0%", font=("Helvetica", 10), bootstyle="primary")
progress_label.pack(pady=5)

# Estatísticas
stats_label = ttkb.Label(root, text="Total de Downloads: 0 | Erros: 0", font=("Helvetica", 10), bootstyle="primary")
stats_label.pack(pady=5)

# Botão para limpar a fila
clear_button = ttkb.Button(root, text="Limpar Fila", command=clear_queue, bootstyle="danger")
clear_button.pack(pady=10)

# Inicia a interface
root.mainloop()