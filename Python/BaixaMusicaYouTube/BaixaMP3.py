import os
import tkinter as tk
from tkinter import ttk, messagebox
from yt_dlp import YoutubeDL
from threading import Thread, Event
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
from imageio_ffmpeg import get_ffmpeg_exe
import unicodedata

# Controle de pausa e interrupção
pause_event = Event()
stop_event = Event()

# Configuração da janela principal
root = ttkb.Window(themename="flatly")  # Tema mais limpo e minimalista
root.title("Music Downloader")
root.geometry("1000x700")  # Ajusta o tamanho da janela
root.resizable(True, True)  # Permite o redimensionamento da janela

# Variáveis globais
downloads = []  # Lista de downloads
current_download = {"active": False, "music": None, "artist": None}
progress_dict = {}

# Lista de sinônimos ou abreviações para alguns artistas
artist_synonyms = {
    "Michael Jackson": ["MJ", "King of Pop"],
    "The Beatles": ["Beatles", "Fab Four"],
    "Ariana Grande": ["Ari", "Grande"],
    # Adicione mais conforme necessário
}


def remove_accents(input_str):
    """Remove acentos de uma string."""
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return ''.join([c for c in nfkd_form if not unicodedata.combining(c)])


def normalize_artist_name(artist_name):
    """Normaliza o nome do artista para verificar sinônimos, sem considerar acentos."""
    artist_name = remove_accents(artist_name.lower())  # Remove acentos antes de normalizar
    for key, synonyms in artist_synonyms.items():
        # Normaliza o nome do artista e os sinônimos, removendo acentos também
        normalized_key = remove_accents(key.lower())
        normalized_synonyms = [remove_accents(synonym.lower()) for synonym in synonyms]

        if artist_name == normalized_key or artist_name in normalized_synonyms:
            return key
    return artist_name


def is_cover(description):
    """Verifica se o vídeo é um cover ou não com base na descrição."""
    # Listas de palavras-chave para identificar covers
    cover_keywords = ["cover", "performed by", "tribute", "interpretation", "version"]
    official_keywords = ["official video", "official music video", "album", "track", "single", "official release"]

    # Verifica se algum termo de cover aparece na descrição
    for keyword in cover_keywords:
        if keyword.lower() in description.lower():
            return True  # Se encontrar "cover", assume que é um cover

    # Verifica se algum termo de video oficial aparece
    for keyword in official_keywords:
        if keyword.lower() in description.lower():
            return False  # Se encontrar "official video", assume que é a versão original

    # Caso não encontre nada, assume que pode ser um conteúdo original
    return False


def validate_artist(song, artist_name):
    """Valida o artista baseado na descrição e na letra da música."""
    normalized_artist = normalize_artist_name(artist_name)
    title = song["title"].lower()
    description = song.get("description", "").lower()

    # Remover acentos do título e da descrição também
    title = remove_accents(title)
    description = remove_accents(description)

    # Verifica se o nome do artista aparece no título ou na descrição
    artist_found_in_title = normalized_artist in title
    artist_found_in_description = normalized_artist in description

    # Verifica se o vídeo é de estúdio e não contém termos inválidos como "ao vivo" ou "acoustic"
    invalid_terms = ["ao vivo"]
    contains_invalid_term = any(term in title or term in description for term in invalid_terms)

    if is_cover(description):
        # Caso o vídeo seja um cover, marque como não válido para evitar erro
        contains_invalid_term = True

    # Se o nome do artista foi encontrado no título ou descrição e não for inválido
    if (artist_found_in_title or artist_found_in_description) and not contains_invalid_term:
        return True
    return False


def get_ydl_opts(artist, download_idx):
    """Configurações do YoutubeDL com índice do download."""
    artist_folder = artist if artist else "Desconhecido"
    download_path = os.path.join("Downloads", artist_folder)
    os.makedirs(download_path, exist_ok=True)

    return {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
        'ffmpeg_location': get_ffmpeg_exe(),  # Obtém o caminho do FFmpeg
        'progress_hooks': [lambda d: progress_hook(d, download_idx)],  # Passa o índice para o hook
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }


def progress_hook(d, download_idx):
    """Atualiza a barra de progresso durante o download."""
    if d['status'] == 'downloading':
        total = d.get('total_bytes', 1)
        downloaded = d.get('downloaded_bytes', 0)
        percent = int(downloaded * 100 / total)

        # Atualiza o progresso apenas se houver progresso real
        if percent > 0:
            downloads[download_idx]["progress"] = percent  # Atualiza o progresso específico
            update_table()  # Atualiza a tabela para refletir o progresso
            progress_label.config(text=f"Progresso geral: {percent}%")
        else:
            downloads[download_idx]["progress"] = 0  # Mantém o progresso como 0 se não houver progresso real
            update_table()

    elif d['status'] == 'finished':
        downloads[download_idx]["progress"] = 100
        downloads[download_idx]["status"] = "Concluído"
        update_table()

def update_overall_progress():
    """Atualiza a barra de progresso geral e altera sua cor com base no status."""
    total_progress = sum(download["progress"] for download in downloads) / len(downloads) if downloads else 0
    progress_bar["value"] = total_progress
    progress_label.config(text=f"Progresso geral: {int(total_progress)}%")

    # Alterando a cor da barra de progresso conforme o status
    if total_progress < 30:
        progress_bar.config(bootstyle="info")  # Cor inicial (azul ou cinza, dependendo do tema)
    elif total_progress < 70:
        progress_bar.config(bootstyle="warning")  # Cor intermediária (amarelo)
    elif total_progress >= 70:
        progress_bar.config(bootstyle="success")  # Cor final (verde claro)

def pause_download():
    """Pausa ou retoma o download."""
    if pause_event.is_set():
        pause_event.clear()  # Retoma o download
        pause_button.config(text="Pausar")
    else:
        pause_event.set()  # Pausa o download
        pause_button.config(text="Retomar")

def update_table():
    """Atualiza a tabela com a lista de downloads."""
    for i in download_table.get_children():
        download_table.delete(i)

    for idx, download in enumerate(downloads):
        download_table.insert("", "end", values=(
            idx + 1,
            download["music"],
            download["artist"],
            download["status"],
            f"{download['progress']}%"
        ))

def add_to_queue():
    """Adiciona músicas à fila de downloads, evitando duplicados."""
    music = search_entry.get().strip()
    artist = artist_entry.get().strip() or "Desconhecido"
    if not music:
        messagebox.showwarning("Aviso", "Insira uma música para adicionar à fila.")
        return

    music_list = [m.strip() for m in music.split(',')]

    for music_item in music_list:
        if music_item:  # Adiciona música apenas se não for uma string vazia
            # Verifica se a música já foi adicionada à fila
            if any(download["music"].lower() == music_item.lower() and download["artist"].lower() == artist.lower() for
                   download in downloads):
                messagebox.showwarning("Aviso", f"A música '{music_item}' de '{artist}' já está na fila.")
            else:
                downloads.append(
                    {"music": music_item, "artist": artist, "status": "Pendente", "progress": 0}
                )

    update_table()

def start_download():
    """Inicia o próximo download da fila de forma contínua."""
    if current_download["active"] or not downloads:
        return  # Se já houver um download ativo ou a lista estiver vazia, não faz nada

    # Procura o próximo download com status "Pendente"
    for download in downloads:
        if download["status"] == "Pendente":
            download["status"] = "Baixando"
            current_download["active"] = True
            current_download["music"] = download["music"]
            current_download["artist"] = download["artist"]
            update_table()
            Thread(target=perform_download, args=(download,)).start()  # Inicia o download em uma nova thread
            break  # Sai do loop após iniciar o download



def perform_download(download):
    """Realiza o download com validação rigorosa do artista."""
    attempts = 0
    max_attempts = 3
    found_artist = False

    # Obtém o índice do download na lista para atualizar o progresso corretamente
    download_idx = downloads.index(download)

    while attempts < max_attempts and not found_artist:
        try:
            ydl_opts = get_ydl_opts(download["artist"], download_idx)
            with YoutubeDL(ydl_opts) as ydl:
                result = ydl.extract_info(f"ytsearch:{download['music']} {download['artist']}", download=False)
                if result and 'entries' in result:
                    song = result['entries'][0]

                    # Validação do artista usando a nova função
                    if validate_artist(song, download["artist"]):
                        found_artist = True
                        ydl.download([song['id']])
                    else:
                        # Se o artista não for encontrado ou o vídeo for inválido, tenta novamente
                        attempts += 1
                        download["status"] = f"Tentando novamente ({attempts}/{max_attempts})"
                        download["progress"] = 0
                        update_table()
                        continue

                if not found_artist:
                    download["status"] = "Falha no Download"
                    update_table()
                    break  # Não continua a execução

        except Exception as e:
            attempts += 1
            if attempts == max_attempts:
                download["status"] = f"Erro: {e}"
                download["progress"] = 0  # Garante que o progresso é 0 em caso de erro
                update_table()

    if found_artist:
        download["status"] = "Concluído"
        update_table()

    # Atualiza o progresso geral
    update_overall_progress()

    # Marca o download atual como concluído
    current_download["active"] = False

    # Inicia o próximo download após o término
    start_download()  # Isso garantirá que o próximo download seja iniciado


# Layout com grid para maior controle
frame_left = ttk.Frame(root)
frame_left.grid(row=0, column=0, padx=20, pady=20, sticky=N)

frame_right = ttk.Frame(root)
frame_right.grid(row=0, column=1, padx=20, pady=20, sticky=N)

# Frame à esquerda com os controles de busca e adicionar
search_label = ttk.Label(frame_left, text="Música (separada por vírgula):")
search_label.grid(row=0, column=0, padx=10, pady=5, sticky=W)

search_entry = ttk.Entry(frame_left, width=40)
search_entry.grid(row=0, column=1, padx=10, pady=5)

artist_label = ttk.Label(frame_left, text="Artista (opcional):")
artist_label.grid(row=1, column=0, padx=10, pady=5, sticky=W)

artist_entry = ttk.Entry(frame_left, width=40)
artist_entry.grid(row=1, column=1, padx=10, pady=5)

# Frame à direita com os botões
add_button = ttk.Button(frame_right, text="Adicionar à Fila", command=add_to_queue)
add_button.grid(row=0, column=0, padx=10, pady=5)

download_button = ttk.Button(frame_right, text="Iniciar Download", command=start_download)
download_button.grid(row=1, column=0, padx=10, pady=5)

pause_button = ttk.Button(frame_right, text="Pausar", command=pause_download)
pause_button.grid(row=2, column=0, padx=10, pady=5)

# Frame para a tabela e barra de progresso na parte inferior
table_frame = ttk.Frame(root)
table_frame.grid(row=1, column=0, columnspan=2, padx=20, pady=20, sticky=NSEW)

columns = ("ID", "Música", "Artista", "Status", "Progresso")
download_table = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)
download_table.grid(row=0, column=0, padx=10, pady=10, sticky=NSEW)

# Definir colunas
for col in columns:
    download_table.heading(col, text=col)
    download_table.column(col, anchor=CENTER)

progress_bar = ttk.Progressbar(table_frame, orient=HORIZONTAL, length=500, mode="determinate")
progress_bar.grid(row=1, column=0, padx=10, pady=10, sticky=NSEW)

progress_label = ttk.Label(table_frame, text="Progresso geral: 0%")
progress_label.grid(row=2, column=0, padx=10, pady=5)

root.mainloop()
