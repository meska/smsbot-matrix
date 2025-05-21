#!/usr/bin/env python
# filepath: /Users/meska/Dev/Mecom/smsbot-matrix/sms_to_matrix.py

import argparse
import time
import os
from dotenv import load_dotenv, find_dotenv
from matrix_bot import MatrixBot

# Carica le variabili d'ambiente
load_dotenv(find_dotenv())


def main():
    # Parse degli argomenti da riga di comando
    parser = argparse.ArgumentParser(description="Invia un messaggio a una stanza Matrix")
    parser.add_argument("--server", help="URL del server Matrix (default dal file .env)")
    parser.add_argument("--username", help="Nome utente per il login (default dal file .env)")
    parser.add_argument("--password", help="Password per il login (default dal file .env)")
    parser.add_argument("--room", help="ID della stanza Matrix (default dal file .env)")
    parser.add_argument("--message", required=True, help="Messaggio da inviare")
    parser.add_argument("--delete-after", type=int, default=0, help="Tempo in secondi dopo il quale cancellare il messaggio (0 = non cancellare)")

    args = parser.parse_args()

    # Ottieni la room da argomenti o variabili d'ambiente
    room_id = args.room or os.environ.get("MATRIX_ROOM_ID")
    if not room_id:
        print("[!] ID stanza non specificato e non presente nel file .env")
        exit(1)

    # Creazione dell'istanza del bot
    bot = MatrixBot(server=args.server, username=args.username, password=args.password)

    # Login al server Matrix
    if not bot.login():
        print("[!] Impossibile procedere senza login")
        exit(1)

    # Invio del messaggio alla stanza
    success, event_id = bot.send_message_to_room(room_id, args.message)

    # Esito dell'operazione
    if success:
        print("[+] Messaggio inviato con successo!")

        # Se è richiesta la cancellazione automatica
        if args.delete_after > 0:
            print(f"[*] Il messaggio verrà cancellato tra {args.delete_after} secondi...")

            # Aspetta il tempo specificato
            time.sleep(args.delete_after)

            # Cancella il messaggio in modo silenzioso
            if bot.silent_delete_message(room_id, event_id):
                print("[+] Messaggio cancellato con successo!")
            else:
                print("[!] Non è stato possibile cancellare il messaggio.")
    else:
        print("[!] Si sono verificati problemi durante l'invio del messaggio.")


if __name__ == "__main__":
    main()
