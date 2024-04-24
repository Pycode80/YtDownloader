import os
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import threading
import yt_dlp
import re
from tkinter import messagebox
import sqlite3
import os.path
from ttkthemes import ThemedStyle
from PIL import Image, ImageTk
import requests


def download_thumbnail(video_id):
    try:
        thumbnail_url = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
        thumbnail_image = Image.open(requests.get(thumbnail_url, stream=True).raw)
        thumbnail_image.thumbnail((300, 200))  # Redimensionner l'image pour l'affichage
        thumbnail_photo = ImageTk.PhotoImage(thumbnail_image)
        thumbnail_label.config(image=thumbnail_photo)
        thumbnail_label.image = thumbnail_photo  # Gardez une référence pour éviter la suppression par le garbage collector
        video_title = yt_dlp.YoutubeDL().extract_info(f'https://www.youtube.com/watch?v={video_id}', download=False).get('title')
        thumbnail_title.config(text=video_title)
    except Exception as e:
        messagebox.showerror("Error", str(e))

def download_thumbnail_playlist(video_title,video_id):
    try:
        thumbnail_url = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
        thumbnail_image = Image.open(requests.get(thumbnail_url, stream=True).raw)
        thumbnail_image.thumbnail((300, 200))  # Redimensionner l'image pour l'affichage
        thumbnail_photo = ImageTk.PhotoImage(thumbnail_image)
        thumbnail_label.config(image=thumbnail_photo)
        thumbnail_label.image = thumbnail_photo  # Gardez une référence pour éviter la suppression par le garbage collector
        thumbnail_title.config(text=video_title)
    except Exception as e:
        messagebox.showerror("Error", str(e))





def create_download_history_table():
    conn = sqlite3.connect('download_history.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS download_history
                 (video_title TEXT, download_location TEXT, download_date TEXT, is_playlist TEXT)''')
    conn.commit()
    conn.close()
    conn = sqlite3.connect('download_folder.db')
    c = conn.cursor()
    # Ajout de la table de préférences
    c.execute('''CREATE TABLE IF NOT EXISTS preferences
                 (download_folder TEXT)''')
    c.execute("INSERT INTO preferences (download_folder) VALUES (?)",(os.path.join(os.path.expanduser("~"), "Downloads"),))
    conn.commit()
    conn.close()
    
def extract_video_id(url):
    video_id_match = re.search(r'(?<=v=)[\w-]+', url)
    if video_id_match:
        return video_id_match.group(0)
    else:
        raise ValueError("Invalid YouTube URL")

create_download_history_table()


def download_thread_function():
    try:
        selected_option = format_choice.get()
        file_path = entry.get()
        is_playlist = is_playlist_var.get()
        if is_playlist:
                progress_bar.grid(row=3, columnspan=2, pady=10)
                eta_label.grid(row=4, columnspan=2)
                n_entries_label.grid(row=3,column=2)
                thumbnail_label.grid(row=6, columnspan=2, padx=20, pady=20)
                thumbnail_label_info.grid(row=5,columnspan=2)
                thumbnail_title.grid(row=7,columnspan=2)
                format_map = {"MP4": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best", "M4A (audio)": "bestaudio[ext=m4a]/best"}
                format_code = format_map.get(selected_option)
                if format_code:
                    ydl_opts = {
                        'format': format_code,  # Choisissez le format de qualité vidéo/audio désiré
                        'outtmpl': os.path.join(read_download_folder_from_db(), '%(title)s.%(ext)s'),  # Nom de fichier de sortie
                        'yes-playlist': True,  # Pour télécharger la playlist complète
                        'progress_hooks': [update_progress_hook_playlist]
                    }
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        ydl.download([file_path])
                        info_dict = ydl.extract_info(file_path, download=False)
                        download_location = read_download_folder_from_db()
                        video_title = info_dict.get('title', 'Untitled')
                        conn = sqlite3.connect('download_history.db')
                        c = conn.cursor()
                        c.execute("INSERT INTO download_history (video_title, download_location, download_date,is_playlist) VALUES (?, ?, datetime('now'), ?)",(video_title, download_location,"x"))
                        conn.commit()
                        conn.close()
        else:
            video_id = extract_video_id(file_path)
            download_thumbnail(video_id)
            thumbnail_title.grid(row=7,columnspan=2)
            progress_bar.grid(row=3, columnspan=2, pady=10)
            eta_label.grid(row=4, columnspan=2)
            thumbnail_label_info.grid(row=5,columnspan=2)
            thumbnail_label.grid(row=6, columnspan=2, padx=20, pady=20)
            format_map = {"MP4": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best", "M4A (audio)": "bestaudio[ext=m4a]/best"}
            format_code = format_map.get(selected_option)
            if format_code:
                # Récupérer le chemin de téléchargement par défaut
                download_folder = preferences.get("download_folder", os.path.join(os.path.expanduser("~"), "Downloads"))
                # Téléchargement du fichier dans le dossier spécifié
                ydl_opts = {
                    'outtmpl': os.path.join(read_download_folder_from_db(), '%(title)s.%(ext)s'),
                    'format': format_code,
                    'progress_hooks': [update_progress_hook]
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([file_path])
                    info_dict = ydl.extract_info(file_path, download=False)
                    download_location = ydl.prepare_filename(info_dict)
                    video_title = info_dict.get('title', 'Untitled')
                    conn = sqlite3.connect('download_history.db')
                    c = conn.cursor()
                    c.execute("INSERT INTO download_history (video_title, download_location, download_date,is_playlist) VALUES (?, ?, datetime('now'), ?)",(video_title, download_location," "))
                    conn.commit()
                    conn.close()
            else:
                print("Format not supported")
    except Exception as e:
        progress_bar['value'] = 0
        progress_bar.grid_remove()
        eta_label.grid_remove()
        messagebox.showerror("Error", str(e))

downloaded_videos = {}  # Dictionnaire pour stocker les vidéos déjà téléchargées

def update_progress_hook_playlist(d):
    try:
        global downloaded_videos
        
        if d['status'] == 'finished' and d["info_dict"].get('n_entries') == d["info_dict"].get('playlist_index'):
            update_progress(True, 100.0, 'finished')
        
        if d['status'] == 'downloading':
            # Obtention des informations sur la playlist
            playlist_size = d["info_dict"].get('n_entries')
            playlist_index = d["info_dict"].get('playlist_index')
            
            video_title = d["info_dict"].get('title')
            video_id = d["info_dict"].get('id')
            
            if video_title not in downloaded_videos:
                download_thumbnail_playlist(video_title,video_id)
                downloaded_videos[video_title] = True

            # Obtention des informations sur la vidéo actuelle
            percentage = d.get('_percent_str', '0.0%')
            percentage_match = re.search(r'(\d+\.\d+)%', percentage)
            if percentage_match:
                percentage = float(percentage_match.group(1))
            else:
                percentage = 0.0

            eta_secondes = d.get('eta', 0)
            if eta_secondes is None:
                eta_formmated = "N/A"
            else:
                minutes = int(eta_secondes // 60)
                secondes = int(eta_secondes % 60)
                eta_formmated = f"{minutes}m{secondes}s"
            n_entries = f"{playlist_index}/{playlist_size}"

            # Mise à jour de la barre de progression
            update_progress(True, percentage, 'downloading', eta_formmated, n_entries)

    except Exception as e:
        messagebox.showerror("Error", str(e))
        progress_bar['value'] = 0
        progress_bar.grid_remove()
        eta_label.grid_remove()


        

def update_progress_hook(d):
    try:
        if d['status'] == 'finished':
            update_progress(False,100.0,'finished')
        if d['status'] == 'downloading':
            percentage = d['_percent_str']
            percentage_match = re.search(r'(\d+\.\d+)%', percentage)
            if percentage_match:
                percentage = float(percentage_match.group(1))
            else:
                percentage = 0.0
            eta_secondes = d.get('eta', 0)
            if eta_secondes == None:
                update_progress(False,percentage, 'downloading',"N/A")
                return
            minutes = int(eta_secondes // 60)
            secondes = int(eta_secondes % 60)
            eta_formmated = f"{minutes}m{secondes}s"
            update_progress(False,percentage, 'downloading',eta_formmated)
    except Exception as e:
        messagebox.showerror("Error", str(e))
        progress_bar['value'] = 0
        progress_bar.grid_remove()
        eta_label.grid_remove()

def update_progress(is_playlist,percentage, status, eta="",n_entries=None):
    if is_playlist:
        n_entries_label.config(text=n_entries)
    progress_bar['value'] = percentage
    eta_label.config(text=f'Temps restant: {eta}')
    if percentage == 100 and status == 'finished':
        if is_playlist:
            n_entries_label.grid_remove()
        progress_bar['value'] = 0
        progress_bar.grid_remove()
        eta_label.grid_remove()
        thumbnail_label_info.grid_remove()
        thumbnail_label.grid_remove()
        thumbnail_title.grid_remove()
        end_label = ttk.Label(frame, text="Téléchargement terminé.")
        end_label.grid(row=3, columnspan=2)
        end_label.after(5000, end_label.destroy)  # Auto-destroy after 5 seconds
        entry.delete(0, 'end')


def start_download():
    # Démarrer le téléchargement dans un thread séparé
    download_thread = threading.Thread(target=download_thread_function)
    download_thread.start()

def update_download_folder(new_folder):
    try:
        conn = sqlite3.connect('download_folder.db')
        c = conn.cursor()
        c.execute("UPDATE preferences SET download_folder = ?", (str(new_folder),))
        conn.commit()
        conn.close()
        current_folder_label.config(text=f"Dossier actuel: {new_folder}")
    except Exception as e:
        messagebox.showerror("Error", str(e))


def change_download_folder():
    new_folder = tk.filedialog.askdirectory()
    print(new_folder)
    if new_folder:
        update_download_folder(new_folder)

def read_download_folder_from_db():
    try:
        conn = sqlite3.connect('download_folder.db')
        c = conn.cursor()
        c.execute("SELECT download_folder FROM preferences")
        result = c.fetchone()
        conn.close()
        if result:
            return result[0]
        else:
            # Si aucun dossier de téléchargement n'est trouvé dans la base de données, retourner le dossier par défaut
            return os.path.join(os.path.join(os.environ['USERPROFILE']), 'Downloads')
    except Exception as e:
        messagebox.showerror("Error", str(e))

def reset_preferences():
    try:
        conn = sqlite3.connect('download_folder.db')
        c = conn.cursor()
        c.execute("UPDATE preferences SET download_folder = ?", (os.path.join(os.path.join(os.environ['USERPROFILE']), 'Downloads'),))
        conn.commit()
        conn.close()
        current_folder_label.config(text="Dossier actuel: "+os.path.join(os.path.join(os.environ['USERPROFILE']), 'Downloads'))
    except Exception as e:
        messagebox.showerror("Error", str(e))






def show_download_history():
    conn = sqlite3.connect('download_history.db')
    c = conn.cursor()
    c.execute("SELECT * FROM download_history")
    history = c.fetchall()
    conn.close()

    # Effacer les anciennes entrées du tableau
    for row in history_treeview.get_children():
        history_treeview.delete(row)

    # Insérer les nouvelles données dans le tableau
    for row in history:
        history_treeview.insert("", "end", values=row)
def show_history_tab(event):
    if notebook.index(notebook.select()) == 2:  # Vérifier si l'onglet sélectionné est "Historique"
        show_download_history()

# Création de la fenêtre principale
root = tk.Tk()
root.title("YouTube Downloader")
root.state('zoomed')

style = ThemedStyle(root)
style.theme_use('plastik') 

# Création de l'onglet "Préférences"
notebook = ttk.Notebook(root)
notebook.grid(row=0, column=0, sticky="nsew")

# Cadre principal
frame = ttk.Frame(notebook, padding="20")
frame.grid(row=0, column=0,sticky="nsew")
notebook.add(frame, text="Téléchargement")

# Label et champ de texte
label = ttk.Label(frame, text="URL YouTube :")
label.grid(row=0, column=0, sticky="w")

eta_label = ttk.Label(frame, text="Temps restant: N/A")
n_entries_label = ttk.Label(frame, text="N/A vidéos effectué")


entry = ttk.Entry(frame, width=50)
entry.grid(row=0, column=1, padx=5, pady=5)

# Liste déroulante
format_choice = tk.StringVar()
format_choice.set("MP4")  # Option par défaut

format_label = ttk.Label(frame, text="Format:")
format_label.grid(row=1, column=0, sticky="w")

format_combo = ttk.Combobox(frame, width=11, textvariable=format_choice, state="readonly")
format_combo['values'] = ("MP4", "M4A (audio)")
format_combo.grid(row=1, column=1, padx=5, pady=5)

# Bouton de téléchargement
download_button = ttk.Button(frame, text="Download !", command=start_download)
download_button.grid(row=3, columnspan=2, pady=10)

is_playlist_var = tk.BooleanVar()
is_playlist_checkbox = ttk.Checkbutton(frame, text="Playlist", variable=is_playlist_var)
is_playlist_checkbox.grid(row=2, columnspan=2)


thumbnail_label = ttk.Label(frame)
thumbnail_label_info = ttk.Label(frame,text='Vidéo en cour de téléchargement :')
thumbnail_title = ttk.Label(frame)



# Barre de progression
progress_bar = ttk.Progressbar(frame, orient='horizontal', length=200, mode='determinate')

# Création de l'onglet "Préférences"
preferences = {}
preferences_frame = ttk.Frame(notebook, padding="20")
preferences_frame.grid(row=0, column=0)
notebook.add(preferences_frame, text="Préférences")


# Bouton pour changer le dossier de téléchargement
change_folder_button = ttk.Button(preferences_frame, text="Changer le dossier de téléchargement", command=change_download_folder)
change_folder_button.grid(row=0, column=0, padx=5, pady=5)

# Label pour afficher le chemin actuel du dossier de téléchargement
current_folder_label = ttk.Label(preferences_frame, text="Dossier actuel: " + read_download_folder_from_db())
current_folder_label.grid(row=0, column=1, padx=5, pady=5)

# Bouton pour réinitialiser les préférences
reset_button = ttk.Button(preferences_frame, text="Réinitialiser les préférences", command=reset_preferences)
reset_button.grid(row=1, columnspan=2, padx=5, pady=5)


history_frame = ttk.Frame(notebook, padding="20")
notebook.add(history_frame, text="Historique")

# Ajout d'un Treeview pour afficher l'historique dans l'onglet Historique
history_treeview = ttk.Treeview(history_frame, columns=("Titre", "Location", "Date","Playlist"), show="headings")
history_treeview.heading("Date", text="Date")
history_treeview.heading("Location", text="Location")
history_treeview.heading("Titre", text="Titre")
history_treeview.heading("Playlist", text="Playlist")


for column in ("Titre", "Location", "Date", "Playlist"):
    history_treeview.column(column, anchor="center")
history_treeview.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")




# Ajout d'une scrollbar pour le Treeview
history_scrollbar = ttk.Scrollbar(history_frame, orient="vertical", command=history_treeview.yview)
history_scrollbar.grid(row=1, column=1, sticky="ns")
history_treeview.configure(yscrollcommand=history_scrollbar.set)



history_frame.rowconfigure(1, weight=1)
history_frame.columnconfigure(0, weight=1)

# Bouton pour rafraîchir l'historique
refresh_button = ttk.Button(history_frame, text="Rafraîchir", command=show_download_history)
refresh_button.grid(row=0, column=0, padx=5, pady=5)



# Afficher l'historique dès que l'onglet Historique est sélectionné
def show_history_tab(event):
    if notebook.index(notebook.select()) == 2:  # Vérifier si l'onglet sélectionné est "Historique"
        show_download_history()

# Associer la fonction show_history_tab à l'événement de changement d'onglet
notebook.bind("<<NotebookTabChanged>>", show_history_tab)



root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)





root.mainloop()


