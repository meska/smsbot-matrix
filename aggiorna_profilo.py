#!/usr/bin/env python
from matrix_bot import MatrixBot
import os
from dotenv import load_dotenv, find_dotenv

# Carica le variabili d'ambiente
load_dotenv(find_dotenv())

# Percorso dell'immagine da caricare
script_dir = os.path.dirname(os.path.realpath(__file__))
image_path = os.path.join(script_dir, "sms.png")


def main():
    # Verifica che l'immagine esista
    if not os.path.exists(image_path):
        print(f"[!] Errore: Il file {image_path} non esiste!")
        exit(1)

    print(f"[*] Utilizzo dell'immagine: {image_path}")

    # Creazione dell'istanza del bot
    bot = MatrixBot()

    # Login al server Matrix
    if not bot.login():
        print("[!] Impossibile procedere senza login")
        exit(1)

    # Aggiornamento dell'immagine del profilo
    if bot.update_profile_image(image_path):
        print("[+] Operazione completata con successo!")
    else:
        print("[!] Si sono verificati problemi durante l'aggiornamento del profilo.")


if __name__ == "__main__":
    main()
