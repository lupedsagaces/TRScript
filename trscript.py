import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pyperclip
import yt_dlp as youtube_dl
import whisper
import threading
import os
import time
import subprocess

# ============================
# Funções principais
# ============================

def download_audio(youtube_url):
    """Baixa o áudio do vídeo do YouTube"""
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': 'audio.mp3',
        'progress_hooks': [hook],
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])

    return 'audio.mp3'


def extract_audio_from_video(video_path):
    """Extrai o áudio de um vídeo local (.mp4) usando ffmpeg"""
    result_label.config(text="Converting video to audio...")
    progress['value'] = 20
    root.update_idletasks()

    output_audio = "audio_from_video.mp3"
    try:
        subprocess.run(
            ["ffmpeg", "-y", "-i", video_path, "-vn", "-acodec", "libmp3lame", "-q:a", "2", output_audio],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
    except Exception as e:
        raise RuntimeError(f"Error converting video: {e}")

    return output_audio


def transcribe_audio(audio_path, language):
    """Transcreve o áudio usando Whisper"""
    model = whisper.load_model("base")
    result = model.transcribe(audio_path, language=language)
    return result["text"]


def process_transcription(audio_path, language):
    """Processa a transcrição"""
    result_label.config(text="Transcribing audio...")
    progress['value'] = 50
    root.update_idletasks()

    try:
        text = transcribe_audio(audio_path, language)
    except Exception as e:
        result_label.config(text=f"Error transcribing audio: {e}")
        start_button.config(state=tk.NORMAL)
        upload_button.config(state=tk.NORMAL)
        return

    with open("transcription.txt", "w", encoding="utf-8") as f:
        f.write(text)

    result_label.config(text="✅ Transcription complete! Saved in 'transcription.txt'.")
    progress['value'] = 100
    start_button.config(state=tk.NORMAL)
    upload_button.config(state=tk.NORMAL)


def download_and_transcribe():
    """Baixa áudio de um link do YouTube e transcreve"""
    url = url_entry.get()
    language = language_var.get()

    if not url:
        result_label.config(text="Please enter the video URL.")
        start_button.config(state=tk.NORMAL)
        upload_button.config(state=tk.NORMAL)
        return

    start_button.config(state=tk.DISABLED)
    upload_button.config(state=tk.DISABLED)
    progress['value'] = 0
    root.update_idletasks()

    try:
        result_label.config(text="Downloading audio...")
        audio_path = download_audio(url)
        process_transcription(audio_path, language)
    except Exception as e:
        result_label.config(text=f"Error: {e}")
        start_button.config(state=tk.NORMAL)
        upload_button.config(state=tk.NORMAL)


def select_video_file():
    """Abre um seletor de arquivo para escolher um vídeo local"""
    file_path = filedialog.askopenfilename(
        title="Select a video file",
        filetypes=[("Video files", "*.mp4 *.mkv *.mov *.avi")]
    )

    if file_path:
        threading.Thread(target=transcribe_local_video, args=(file_path,), daemon=True).start()


def transcribe_local_video(file_path):
    """Transcreve um vídeo local"""
    language = language_var.get()
    start_button.config(state=tk.DISABLED)
    upload_button.config(state=tk.DISABLED)
    progress['value'] = 0
    root.update_idletasks()

    try:
        audio_path = extract_audio_from_video(file_path)
        process_transcription(audio_path, language)
    except Exception as e:
        result_label.config(text=f"Error processing video: {e}")
        start_button.config(state=tk.NORMAL)
        upload_button.config(state=tk.NORMAL)


def start_transcription():
    threading.Thread(target=download_and_transcribe, daemon=True).start()


def paste_url():
    url = pyperclip.paste()
    url_entry.delete(0, tk.END)
    url_entry.insert(0, url)


def hook(d):
    if d['status'] == 'finished':
        progress['value'] = 50
        root.update_idletasks()


# ============================
# Interface gráfica (Tkinter)
# ============================

root = tk.Tk()
root.title("TRScript")

# URL do vídeo
url_label = tk.Label(root, text="YouTube Video URL:")
url_label.pack(pady=5)

url_frame = tk.Frame(root)
url_frame.pack(pady=5)

url_entry = tk.Entry(url_frame, width=50)
url_entry.pack(side=tk.LEFT, padx=(10, 0))

paste_button = tk.Button(url_frame, text="Paste URL", command=paste_url)
paste_button.pack(side=tk.LEFT, padx=5)

# Idioma
language_var = tk.StringVar()
language_options = ["English", "Portuguese", "Spanish", "French", "German"]
language_var.set(language_options[0])

language_label = tk.Label(root, text="Select Language:")
language_label.pack(pady=5)

language_menu = ttk.OptionMenu(root, language_var, *language_options)
language_menu.pack(pady=5)

# Botões principais
buttons_frame = tk.Frame(root)
buttons_frame.pack(pady=10)

start_button = tk.Button(buttons_frame, text="Transcribe YouTube", command=start_transcription)
start_button.pack(side=tk.LEFT, padx=5)

upload_button = tk.Button(buttons_frame, text="Transcribe Local Video", command=select_video_file)
upload_button.pack(side=tk.LEFT, padx=5)

# Barra de progresso
progress = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
progress.pack(pady=10)

# Status
result_label = tk.Label(root, text="")
result_label.pack(pady=5)

root.mainloop()
