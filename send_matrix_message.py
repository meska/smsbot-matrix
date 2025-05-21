from matrix_bot import MatrixBot
import time
import os
from dotenv import load_dotenv, find_dotenv

# Carica le variabili d'ambiente
load_dotenv(find_dotenv())

# Configurazione
room_id = os.environ.get("MATRIX_ROOM_ID")
message = "Ciao! Messaggio inviato da script Python."


def main():
    # Creazione dell'istanza del bot (utilizzerà le variabili d'ambiente)
    bot = MatrixBot()

    # Login al server Matrix
    if not bot.login():
        print("[!] Impossibile procedere senza login")
        exit(1)

    # Invio del messaggio alla stanza
    success, event_id = bot.send_message_to_room(room_id, message)

    # Esito dell'operazione
    if success:
        print("[+] Operazione completata con successo!")
        print("[*] Il messaggio verrà cancellato tra 30 secondi...")

        # Aspetta 30 secondi
        time.sleep(30)

        # Cancella il messaggio in modo silenzioso (senza lasciare traccia)
        if bot.silent_delete_message(room_id, event_id):
            print("[+] Messaggio cancellato con successo!")
        else:
            print("[!] Non è stato possibile cancellare il messaggio.")
    else:
        print("[!] Si sono verificati problemi durante l'operazione.")


if __name__ == "__main__":
    main()
