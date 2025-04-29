import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from yt_dlp import YoutubeDL
from threading import Thread
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
from imageio_ffmpeg import get_ffmpeg_exe
import logging
from PIL import Image, ImageTk
import requests
from io import BytesIO
import pandas as pd

root = ttkb.Window(themename="flatly")
root.title("Music Downloader")
root.geometry("1200x700")
root.resizable(False, False)

primary_color = "#3a86ff"
secondary_color = "#62b6cb"
success_color = "#2ecc71"
info_color = "#3498db"
warning_color = "#f39c12"
danger_color = "#e74c3c"
background_color = "#f8f9fa"
text_color = "#333333"
light_gray = "#ced4da"

root.config(bg=background_color)

downloads = []
current_download = {"active": False, "music": None, "artist": None}
download_folder = "Downloads"
statistics = {"total_downloads": 0, "total_errors": 0}
progress_bars = {}
image_cache = {}

logging.basicConfig(filename="errors.log", level=logging.ERROR)


def validate_input(music, artist):
    if not music:
        messagebox.showwarning(
            "Aviso", "O campo 'Nome da Música' é obrigatório.")
        return False
    return True


def get_youtube_info(query):
    ydl_opts = {'quiet': True, 'extract_flat': True, 'max_entries': 1}
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch:{query}", download=False)
            if 'entries' in info and info['entries']:
                entry = info['entries'][0]
                title = entry.get('title')
                thumbnail_url = entry.get('thumbnail')
                return title, thumbnail_url
    except Exception as e:
        logging.error(f"Erro ao buscar informações do YouTube: {e}")
    return None, None


def load_thumbnail(url, size=(80, 60)):
    try:
        response = requests.get(url)
        response.raise_for_status()
        image = Image.open(BytesIO(response.content))
        image = image.resize(size)
        return ImageTk.PhotoImage(image)
    except Exception as e:
        logging.error(f"Erro ao carregar miniatura: {e}")
        return None


def update_table():
    global progress_bars
    global image_cache

    for row in table.get_children():
        table.delete(row)
        if row in progress_bars:
            del progress_bars[row]

    image_cache = {}
    progress_bars = {}

    for idx, download in enumerate(downloads):
        thumbnail = None
        if download["thumbnail_url"] and download["thumbnail_url"] not in image_cache:
            img = load_thumbnail(download["thumbnail_url"])
            if img:
                image_cache[download["thumbnail_url"]] = img
                thumbnail = img
        elif download["thumbnail_url"] in image_cache:
            thumbnail = image_cache[download["thumbnail_url"]]

        item_id = table.insert("", "end", values=(
            idx + 1,
            download["title"] if "title" in download and download["title"] else download["music"],
            download["artist"],
            download["status"],
            f"{download['progress']}%"
        ))

        if thumbnail:
            table.set_image(item_id, column="#0", image=thumbnail)

    update_overall_progress()


def add_to_download_list(music, artist, quality):
    title, thumbnail_url = get_youtube_info(f"{music} {artist}")
    if title:
        downloads.append({"music": music, "artist": artist, "status": "Pendente", "progress": 0,
                         "quality": quality, "title": title, "thumbnail_url": thumbnail_url, "thumbnail": None})
        update_table()
        if not current_download["active"]:
            start_download()
    else:
        messagebox.showerror(
            "Erro", f"Não foi possível encontrar informações para '{music} - {artist}'.")


def download_music():
    music_input = entry_music.get().strip()
    artist = entry_artist.get().strip() or "Desconhecido"
    quality = quality_var.get()

    if not music_input:
        messagebox.showwarning("Aviso", "Por favor, insira o nome da música.")
        return

    music_list = [m.strip() for m in music_input.split(',')]

    for music in music_list:
        if not validate_input(music, artist):
            return
        add_to_download_list(music, artist, quality)


def importar_excel():
    file_path = filedialog.askopenfilename(
        title="Selecionar arquivo Excel",
        filetypes=[("Arquivos Excel", "*.xlsx;*.xls")]
    )
    if file_path:
        try:
            df = pd.read_excel(file_path)
            if 'Cantor' in df.columns and 'Musica' in df.columns:
                for index, row in df.iterrows():
                    cantor = str(row['Cantor']).strip() if pd.notna(
                        row['Cantor']) else "Desconhecido"
                    musica = str(row['Musica']).strip()
                    quality = quality_var.get()
                    if validate_input(musica, cantor):
                        downloads.append({"music": musica, "artist": cantor, "status": "Pendente", "progress": 0,
                                         "quality": quality, "title": None, "thumbnail_url": None, "thumbnail": None})
                        update_table()
                        if not current_download["active"]:
                            start_download()
            else:
                messagebox.showerror(
                    "Erro", "O arquivo Excel deve conter colunas 'Cantor' e 'Musica'.")
        except FileNotFoundError:
            messagebox.showerror("Erro", "Arquivo não encontrado.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao ler o arquivo Excel: {e}")


def start_download():
    if current_download["active"] or not downloads:
        return

    for download in downloads:
        if download["status"] == "Pendente":
            current_download["active"] = True
            current_download["music"] = download["music"]
            current_download["artist"] = download["artist"]
            download["status"] = "Baixando"
            update_table()
            Thread(target=perform_download, args=(download,)).start()
            break


def perform_download(download):
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(download_folder, f"{download['artist']} - {download['music']}.%(ext)s"),
            'ffmpeg_location': get_ffmpeg_exe(),
            'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': download["quality"]}],
            'progress_hooks': [lambda d: progress_hook(d, download)],
            'quiet': True,
        }
        if download["quality"] in ["64", "64k"]:
            ydl_opts['postprocessor_args'] = ['-ac', '1', '-b:a', '64k']

        with YoutubeDL(ydl_opts) as ydl:
            ydl.download(
                [f"ytsearch:{download['music']} {download['artist']}"])

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
        start_download()


def progress_hook(d, download):
    if d['status'] == 'downloading':
        total = d.get('total_bytes')
        downloaded = d.get('downloaded_bytes')
        if total is not None and downloaded is not None:
            percent = int(downloaded * 100 / total)
            download["progress"] = percent
            update_table_progress(download)


def update_table_progress(download_item):
    for item in table.get_children():
        if table.item(item, 'values')[1] == download_item['title'] and table.item(item, 'values')[2] == download_item['artist']:
            table.item(item, values=(
                table.item(item, 'values')[0],
                download_item['title'],
                download_item['artist'],
                download_item['status'],
                f"{download_item['progress']}%"
            ))
            break
    update_overall_progress()


def update_overall_progress():
    total_progress = sum(download["progress"]
                         for download in downloads) / len(downloads) if downloads else 0
    overall_progress_bar["value"] = total_progress
    overall_progress_label.config(
        text=f"Progresso geral: {int(total_progress)}%")


def update_statistics():
    stats_label.config(
        text=f"Total de Downloads: {statistics['total_downloads']} | Erros: {statistics['total_errors']}")


def select_folder():
    global download_folder
    folder = filedialog.askdirectory()
    if folder:
        download_folder = folder
        folder_label.config(text=f"Pasta: {folder}")


def clear_queue():
    global downloads
    downloads = [d for d in downloads if d["status"] != "Concluído"]
    update_table()


style = ttkb.Style()
style.theme_use("flatly")

main_frame = ttkb.Frame(root, padding=20, bootstyle="light")
main_frame.pack(fill="both", expand=True)

title_label = ttkb.Label(main_frame, text="Music Downloader", font=(
    "Segoe UI", 20, "bold"), bootstyle="primary")
title_label.pack(pady=(0, 20), anchor="w")

input_frame = ttkb.Frame(main_frame, padding=10, bootstyle="light")
input_frame.pack(fill="x", pady=(0, 20))

music_label = ttkb.Label(input_frame, text="Nome da Música (separar por vírgula):", font=(
    "Segoe UI", 10), bootstyle="secondary")
music_label.pack(anchor="w")
entry_music = ttkb.Entry(input_frame, font=("Segoe UI", 10))
entry_music.pack(fill="x", pady=5)

artist_label = ttkb.Label(input_frame, text="Artista (opcional):", font=(
    "Segoe UI", 10), bootstyle="secondary")
artist_label.pack(anchor="w", pady=(10, 0))
entry_artist = ttkb.Entry(input_frame, font=("Segoe UI", 10))
entry_artist.pack(fill="x", pady=5)

quality_frame = ttkb.Frame(input_frame, bootstyle="light")
quality_frame.pack(fill="x", pady=(10, 0))
quality_label = ttkb.Label(quality_frame, text="Qualidade:", font=(
    "Segoe UI", 10), bootstyle="secondary")
quality_label.pack(side="left")
quality_var = tk.StringVar(value="192")
quality_menu = ttkb.Combobox(quality_frame, textvariable=quality_var, values=[
                             "64", "128", "192", "320"], bootstyle="primary")
quality_menu.pack(side="left", padx=10)

download_button = ttkb.Button(
    input_frame, text="Baixar", command=download_music, bootstyle="success", padding=10)
download_button.pack(pady=15, fill="x")

import_excel_button = ttkb.Button(
    input_frame, text="Importar do Excel", command=importar_excel, bootstyle="info", padding=10)
import_excel_button.pack(pady=10, fill="x")

folder_frame = ttkb.Frame(main_frame, bootstyle="light")
folder_frame.pack(fill="x", pady=(10, 0))
folder_button = ttkb.Button(folder_frame, text="Selecionar Pasta",
                            command=select_folder, bootstyle="info", padding=5)
folder_button.pack(side="left")
folder_label = ttkb.Label(folder_frame, text=f"Pasta: {download_folder}", font=(
    "Segoe UI", 10), bootstyle="secondary", anchor="w")
folder_label.pack(side="left", padx=10, fill="x", expand=True)

table_frame = ttkb.Frame(main_frame, padding=10, bootstyle="light")
table_frame.pack(fill="both", expand=True, pady=(20, 0))

columns = ("#0", "Música", "Artista", "Status", "Progresso")
table = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)
table.heading("#0", text="Miniatura", anchor="w")
table.heading("Música", text="Música", anchor="w")
table.heading("Artista", text="Artista", anchor="w")
table.heading("Status", text="Status", anchor="center")
table.heading("Progresso", text="Progresso", anchor="center")

table.column("#0", width=80, stretch=False)
table.column("Música", width=300, anchor="w")
table.column("Artista", width=200, anchor="w")
table.column("Status", width=120, anchor="center")
table.column("Progresso", width=250, anchor="center")

table.pack(fill="both", expand=True)

overall_progress_frame = ttkb.Frame(main_frame, padding=10, bootstyle="light")
overall_progress_frame.pack(fill="x", pady=(20, 0))
overall_progress_label = ttkb.Label(overall_progress_frame, text="Progresso geral: 0%", font=(
    "Segoe UI", 10), bootstyle="secondary", anchor="w")
overall_progress_label.pack(fill="x")
overall_progress_bar = ttkb.Progressbar(
    overall_progress_frame, orient=HORIZONTAL, mode="determinate", bootstyle="success-striped")
overall_progress_bar.pack(fill="x", pady=5)

bottom_frame = ttkb.Frame(main_frame, padding=10, bootstyle="light")
bottom_frame.pack(fill="x", pady=(10, 0))

stats_label = ttkb.Label(bottom_frame, text="Total de Downloads: 0 | Erros: 0", font=(
    "Segoe UI", 10), bootstyle="info", anchor="w")
stats_label.pack(side="left")

clear_button = ttkb.Button(bottom_frame, text="Limpar Concluídos",
                           command=clear_queue, bootstyle="danger", padding=5)
clear_button.pack(side="right")

root.mainloop()
