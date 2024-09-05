import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import pyperclip
import yt_dlp as youtube_dl
import whisper
import threading
import os
import time  # Import time for simulation of progress

def download_audio(youtube_url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': 'audio.mp3',
        'progress_hooks': [hook],  # Hook to update the progress bar
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])

    return 'audio.mp3'

def transcribe_audio(audio_path, language):
    model = whisper.load_model("base")
    result = model.transcribe(audio_path+".mp3", language=language)
    return result["text"]

def download_and_transcribe():
    url = url_entry.get()
    language = language_var.get()

    if not url:
        result_label.config(text="Please enter the video URL.")
        start_button.config(state=tk.NORMAL)  # Re-enable the button in case of error
        return

    # Disable the button while processing
    start_button.config(state=tk.DISABLED)
    
    result_label.config(text="Downloading audio...")
    progress['value'] = 0
    root.update_idletasks()

    try:
        audio_path = download_audio(url)
    except Exception as e:
        result_label.config(text=f"Error downloading audio: {e}")
        start_button.config(state=tk.NORMAL)  # Re-enable the button in case of error
        return

    result_label.config(text="Audio downloaded. Transcribing audio...")
    progress['value'] = 50  # Update progress bar to 50% during transcription
    root.update_idletasks()

    try:
        # Simulate incremental progress in transcribing
        for i in range(10):  # Simulate progress steps (10 steps for example)
            text = transcribe_audio(audio_path, language)
            progress['value'] = 50 + i * 5  # Incremental update
            root.update_idletasks()
            time.sleep(0.5)  # Simulate time taken for processing
        progress['value'] = 100  # Complete progress
    except Exception as e:
        result_label.config(text=f"Error transcribing audio: {e}")
        start_button.config(state=tk.NORMAL)  # Re-enable the button in case of error
        return

    with open("transcription.txt", "w", encoding="utf-8") as f:
        f.write(text)
    
    result_label.config(text="Transcription complete! Saved in 'transcription.txt'.")
    progress['value'] = 100

    # Re-enable the button after completion
    start_button.config(state=tk.NORMAL)

def start_transcription():
    threading.Thread(target=download_and_transcribe, daemon=True).start()

def paste_url():
    url = pyperclip.paste()
    url_entry.delete(0, tk.END)
    url_entry.insert(0, url)

def hook(d):
    if d['status'] == 'finished':
        progress['value'] = 50  # Update progress bar to 50% when download finishes
        root.update_idletasks()

# GUI Configuration
root = tk.Tk()
root.title("TRScript")

# Video URL
url_label = tk.Label(root, text="YouTube Video URL:")
url_label.pack(pady=5)

url_frame = tk.Frame(root)
url_frame.pack(pady=5)
''
url_entry = tk.Entry(url_frame, width=50)
url_entry.pack(side=tk.LEFT, padx=(10, 0))  # Adds 10 pixels of space to the left

paste_button = tk.Button(url_frame, text="Paste URL", command=paste_url)
paste_button.pack(side=tk.LEFT, padx=5)

# Language
language_var = tk.StringVar()
language_options = ["English", "Portuguese", "Spanish", "French", "German"]

# Set default option and update menu
language_var.set(language_options[0])  # Sets the default option to the first item in the list

language_label = tk.Label(root, text="Select Language:")
language_label.pack(pady=5)

language_menu = ttk.OptionMenu(root, language_var, *language_options)
language_menu.pack(pady=5)

# Force update of OptionMenu to reflect changes
def update_language_menu():
    menu = language_menu["menu"]
    menu.delete(0, "end")
    for option in language_options:
        menu.add_command(label=option, command=tk._setit(language_var, option))

update_language_menu()

# Button to start transcription
start_button = tk.Button(root, text="Start Transcription", command=start_transcription)
start_button.pack(pady=10)

# Progress bar
progress = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
progress.pack(pady=10)

# Status label
result_label = tk.Label(root, text="")
result_label.pack(pady=5)

root.mainloop()
