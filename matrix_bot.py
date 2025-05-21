import httpx
import uuid
import os
import json
import time
import mimetypes
from dotenv import load_dotenv, find_dotenv


class MatrixBot:
    def __init__(self, server=None, username=None, password=None):
        """
        Inizializza un'istanza del bot Matrix
        Se i parametri non sono specificati, vengono caricati dal file .env

        Args:
            server (str, optional): URL del server Matrix
            username (str, optional): Nome utente per il login
            password (str, optional): Password per il login
        """
        # Carica le variabili d'ambiente dal file .env
        load_dotenv(find_dotenv())

        # Usa i parametri forniti o le variabili d'ambiente
        self.server = server or os.environ.get("MATRIX_SERVER")
        self.username = username or os.environ.get("MATRIX_USERNAME")
        self.password = password or os.environ.get("MATRIX_PASSWORD")

        if not self.server or not self.username or not self.password:
            raise ValueError("Server, username e password devono essere specificati o presenti nel file .env")

        self.access_token = None
        self.headers = None
        self.token_file = f".token_{self.username}.json"

    def load_saved_token(self):
        """
        Carica un token salvato da un file

        Returns:
            bool: True se il token è stato caricato e è valido, False altrimenti
        """
        if not os.path.exists(self.token_file):
            return False

        try:
            with open(self.token_file, "r") as f:
                token_data = json.load(f)

            # Verifica se il token è ancora valido
            if "expires_at" in token_data and token_data["expires_at"] > time.time():
                self.access_token = token_data["access_token"]
                self.headers = {"Authorization": f"Bearer {self.access_token}", "Content-Type": "application/json"}
                print("[+] Token caricato dal file.")
                return True
            else:
                print("[!] Token scaduto, effettuerò un nuovo login.")
                os.remove(self.token_file)  # Rimuovi il token scaduto
                return False
        except Exception as e:
            print(f"[!] Errore nel caricamento del token: {e}")
            return False

    def save_token(self, access_token, expires_in=None):
        """
        Salva il token su un file

        Args:
            access_token (str): Token di accesso
            expires_in (int, optional): Tempo di scadenza in secondi
        """
        try:
            token_data = {"access_token": access_token, "created_at": time.time()}

            # Se abbiamo un tempo di scadenza, lo aggiungiamo
            if expires_in:
                token_data["expires_at"] = time.time() + expires_in
            else:
                # Per default, consideriamo il token valido per 24 ore
                token_data["expires_at"] = time.time() + (24 * 60 * 60)

            with open(self.token_file, "w") as f:
                json.dump(token_data, f)

            print("[+] Token salvato su file.")
        except Exception as e:
            print(f"[!] Errore nel salvataggio del token: {e}")

    def login(self):
        """
        Effettua il login al server Matrix e ottiene l'access token
        Prima prova a caricare un token salvato, se non è possibile effettua un nuovo login

        Returns:
            bool: True se il login ha successo, False altrimenti
        """
        # Prova a caricare un token salvato
        if self.load_saved_token():
            return True

        # Se non c'è un token salvato o è scaduto, effettua un nuovo login
        login_url = f"{self.server}/_matrix/client/v3/login"
        login_data = {"type": "m.login.password", "user": self.username, "password": self.password}

        print("[*] Effettuo login...")
        try:
            resp = httpx.post(login_url, json=login_data)

            if resp.status_code != 200:
                print("[!] Login fallito:", resp.text)
                return False

            resp_data = resp.json()
            self.access_token = resp_data["access_token"]
            self.headers = {"Authorization": f"Bearer {self.access_token}", "Content-Type": "application/json"}

            # Salviamo il token per usi futuri
            expires_in = resp_data.get("expires_in_ms")
            if expires_in:
                expires_in = expires_in / 1000  # Convertiamo da millisecondi a secondi
            self.save_token(self.access_token, expires_in)

            print("[+] Login effettuato, token ottenuto.")
            return True
        except Exception as e:
            print("[!] Errore durante il login:", e)
            return False

    def join_room(self, room_id):
        """
        Unisce il bot ad una stanza Matrix

        Args:
            room_id (str): ID della stanza Matrix

        Returns:
            bool: True se l'operazione ha successo, False altrimenti
        """
        if not self.access_token:
            print("[!] Devi prima effettuare il login")
            return False

        join_url = f"{self.server}/_matrix/client/v3/rooms/{room_id}/join"

        print(f"[*] Tentativo di unirsi alla stanza {room_id}...")
        try:
            join_resp = httpx.post(join_url, headers=self.headers, json={})

            if join_resp.status_code == 200:
                print("[+] Unito alla stanza con successo!")
                return True
            else:
                print(f"[!] Avviso nell'unirsi alla stanza: {join_resp.status_code} {join_resp.text}")
                return False
        except Exception as e:
            print("[!] Errore durante l'unione alla stanza:", e)
            return False

    def send_message(self, room_id, message):
        """
        Invia un messaggio ad una stanza Matrix

        Args:
            room_id (str): ID della stanza Matrix
            message (str): Il messaggio da inviare

        Returns:
            bool: True se l'operazione ha successo, False altrimenti
            str: ID dell'evento messaggio se l'invio ha successo, None altrimenti
        """
        if not self.access_token:
            print("[!] Devi prima effettuare il login")
            return False, None

        transaction_id = str(uuid.uuid4()).replace("-", "")  # Genero un ID di transazione unico senza trattini
        send_url = f"{self.server}/_matrix/client/v3/rooms/{room_id}/send/m.room.message/{transaction_id}"
        message_data = {"msgtype": "m.text", "body": message}

        print(f"[*] Invio messaggio alla stanza {room_id}...")
        try:
            resp = httpx.put(send_url, headers=self.headers, json=message_data)

            if resp.status_code == 200:
                event_id = resp.json().get("event_id")
                print(f"[+] Messaggio inviato correttamente! Event ID: {event_id}")
                return True, event_id
            else:
                print("[!] Errore nell'invio:", resp.status_code, resp.text)
                return False, None
        except Exception as e:
            print("[!] Errore durante l'invio del messaggio:", e)
            return False, None

    def delete_message(self, room_id, event_id):
        """
        Cancella un messaggio da una stanza Matrix

        Args:
            room_id (str): ID della stanza Matrix
            event_id (str): ID dell'evento messaggio da cancellare

        Returns:
            bool: True se l'operazione ha successo, False altrimenti
        """
        if not self.access_token:
            print("[!] Devi prima effettuare il login")
            return False

        if not event_id:
            print("[!] ID evento non valido")
            return False

        transaction_id = str(uuid.uuid4()).replace("-", "")
        redact_url = f"{self.server}/_matrix/client/v3/rooms/{room_id}/redact/{event_id}/{transaction_id}"
        reason_data = {"reason": "Messaggio cancellato automaticamente"}

        print(f"[*] Cancellazione messaggio con ID {event_id}...")
        try:
            resp = httpx.put(redact_url, headers=self.headers, json=reason_data)

            if resp.status_code == 200:
                print("[+] Messaggio cancellato correttamente!")
                return True
            else:
                print("[!] Errore nella cancellazione:", resp.status_code, resp.text)
                return False
        except Exception as e:
            print("[!] Errore durante la cancellazione del messaggio:", e)
            return False

    def send_message_to_room(self, room_id, message):
        """
        Metodo pratico che unisce alla stanza e invia un messaggio

        Args:
            room_id (str): ID della stanza Matrix
            message (str): Il messaggio da inviare

        Returns:
            tuple: (success, event_id) dove success è un bool e event_id è l'ID dell'evento o None
        """
        # Prima uniamoci alla stanza
        success = self.join_room(room_id)
        if not success:
            print("[*] Provo comunque a inviare il messaggio...")

        # Poi inviamo il messaggio
        return self.send_message(room_id, message)

    def edit_message(self, room_id, event_id, new_message):
        """
        Modifica un messaggio esistente in una stanza Matrix

        Args:
            room_id (str): ID della stanza Matrix
            event_id (str): ID dell'evento messaggio da modificare
            new_message (str): Nuovo contenuto del messaggio

        Returns:
            bool: True se l'operazione ha successo, False altrimenti
        """
        if not self.access_token:
            print("[!] Devi prima effettuare il login")
            return False

        if not event_id:
            print("[!] ID evento non valido")
            return False

        transaction_id = str(uuid.uuid4()).replace("-", "")
        edit_url = f"{self.server}/_matrix/client/v3/rooms/{room_id}/send/m.room.message/{transaction_id}"

        # Dati per sovrascrivere il messaggio precedente
        edit_data = {"msgtype": "m.text", "body": new_message, "m.relates_to": {"rel_type": "m.replace", "event_id": event_id}}

        print(f"[*] Modifica messaggio con ID {event_id}...")
        try:
            resp = httpx.put(edit_url, headers=self.headers, json=edit_data)

            if resp.status_code == 200:
                print("[+] Messaggio modificato correttamente!")
                return True
            else:
                print("[!] Errore nella modifica:", resp.status_code, resp.text)
                return False
        except Exception as e:
            print("[!] Errore durante la modifica del messaggio:", e)
            return False

    def silent_delete_message(self, room_id, event_id):
        """
        Cancella un messaggio silenziosamente (prima lo sostituisce con spazio vuoto, poi lo cancella)

        Args:
            room_id (str): ID della stanza Matrix
            event_id (str): ID dell'evento messaggio da cancellare

        Returns:
            bool: True se l'operazione ha successo, False altrimenti
        """
        if not self.access_token:
            print("[!] Devi prima effettuare il login")
            return False

        if not event_id:
            print("[!] ID evento non valido")
            return False

        # Prima modifichiamo il messaggio con un contenuto vuoto
        edit_success = self.edit_message(room_id, event_id, " ")

        if not edit_success:
            print("[!] Non è stato possibile modificare il messaggio prima della cancellazione")
            # Proviamo comunque la cancellazione normale

        # Poi procediamo con la cancellazione
        return self.delete_message(room_id, event_id)

    def update_profile_image(self, image_path):
        """
        Aggiorna l'immagine del profilo dell'utente

        Args:
            image_path (str): Percorso del file immagine da caricare

        Returns:
            bool: True se l'operazione ha successo, False altrimenti
        """
        if not self.access_token:
            print("[!] Devi prima effettuare il login")
            return False

        # Prima dobbiamo caricare l'immagine sul server Matrix
        try:
            # Leggi il file immagine
            with open(image_path, "rb") as f:
                image_data = f.read()

            # Determina il tipo MIME del file
            mime_type, _ = mimetypes.guess_type(image_path)
            if not mime_type:
                mime_type = "image/jpeg"  # Default fallback

            # Carica l'immagine sul server Matrix
            upload_url = f"{self.server}/_matrix/media/v3/upload"
            upload_headers = {"Authorization": f"Bearer {self.access_token}", "Content-Type": mime_type}

            print(f"[*] Caricamento immagine {image_path}...")
            upload_resp = httpx.post(upload_url, headers=upload_headers, content=image_data)

            if upload_resp.status_code != 200:
                print(f"[!] Errore nel caricamento dell'immagine: {upload_resp.status_code} {upload_resp.text}")
                return False

            # Ottieni l'URI dell'immagine caricata
            content_uri = upload_resp.json().get("content_uri")
            if not content_uri:
                print("[!] Impossibile ottenere l'URI dell'immagine caricata")
                return False

            # Aggiorna il profilo con la nuova immagine
            # Assicuriamoci che l'ID utente sia formattato correttamente
            user_id = self.username if self.username.startswith("@") else f"@{self.username}:mecomsrl.com"
            profile_url = f"{self.server}/_matrix/client/v3/profile/{user_id}/avatar_url"
            profile_data = {"avatar_url": content_uri}

            print("[*] Aggiornamento immagine del profilo...")
            profile_resp = httpx.put(profile_url, headers=self.headers, json=profile_data)

            if profile_resp.status_code == 200:
                print("[+] Immagine del profilo aggiornata con successo!")
                return True
            else:
                print(f"[!] Errore nell'aggiornamento dell'immagine del profilo: {profile_resp.status_code} {profile_resp.text}")
                return False

        except Exception as e:
            print(f"[!] Errore durante l'aggiornamento dell'immagine del profilo: {e}")
            return False
