#!/bin/bash

ACTION="$1"
SMS_FILE="$2"
LOGFILE="/var/log/sms_to_discord.log"
WEBHOOK_URL="https://discord.com/api/webhooks/xxxxxxxxxx/xxxxxxxxxxxxx?wait=true"
WEBHOOK_URL2="https://discord.com/api/webhooks/xxxxxxxxxx/xxxxxxxxxxxxx"

# Se non è un messaggio ricevuto, esci
if [ "$ACTION" != "RECEIVED" ]; then
    exit 0
fi

# Parsiamo i dati
SENDER=$(grep "^From: " "$SMS_FILE" | cut -d' ' -f2-)
DATE=$(grep "^Received: " "$SMS_FILE" | cut -d' ' -f2-)
MESSAGE=$(awk 'BEGIN{found=0} /^[[:space:]]*$/ {found=1; next} found {print}' "$SMS_FILE")

# Se vuoto, metti messaggio placeholder
[ -z "$SENDER" ] && SENDER="(sconosciuto)"
[ -z "$DATE" ] && DATE="(sconosciuta)"
[ -z "$MESSAGE" ] && MESSAGE="(nessun contenuto)"

# Logging inizio
echo "[$(date)] SMS da: $SENDER | Data: $DATE | Messaggio: $MESSAGE" >>"$LOGFILE"

# Invio al webhook Discord e salva la risposta
RESPONSE=$(curl -s -X POST -H "Content-Type: application/json" \
    -d "$(jq -n \
        --arg from "$SENDER" \
        --arg date "$DATE" \
        --arg msg "$MESSAGE" \
        '{content: "✉️ **SMS da:** \($from)\n🕒 **Data:** \($date)\n💬 **Messaggio:** \($msg)"}')" \
    "$WEBHOOK_URL")

# Estrai l'ID del messaggio
MESSAGE_ID=$(echo "$RESPONSE" | jq -r '.id')

# Logging ID
echo "[$(date)] Messaggio inviato a Discord con ID: $MESSAGE_ID" >>"$LOGFILE"

# Se l'ID è valido, cancella dopo 60 secondi
if [[ "$MESSAGE_ID" != "null" && -n "$MESSAGE_ID" ]]; then
    (
        sleep 60
        DELETE_RESULT=$(curl -s -X DELETE "$WEBHOOK_URL2/messages/$MESSAGE_ID")
        echo "[$(date)] Messaggio ID $MESSAGE_ID eliminato da Discord. Risultato: $DELETE_RESULT" >>"$LOGFILE"
    ) &
fi
