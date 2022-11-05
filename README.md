# YtDownloader
Yt Downloader

Voici une petite application avec un interface graphique qui permet de télécharger des vidéos Youtube.

Les modules requis sont : PyQt5,pytube et le module sys

Si vous souhaitez compiler le programme , la commande suivante fonctionne avec Pyinstaller v4.5.1


pyinstaller --noconfirm --onedir --windowed --icon "logo.ico;." --paths "C:/Users/{yourusername}/AppData/Local/Programs/Python/Python39/Lib/site-packages"  "app.py"
