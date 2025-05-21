#!/bin/bash

ACTION="$1"
SMS_FILE="$2"
LOGFILE="$HOME/sms_to_matrix.log"

# Configurazione Matrix
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

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

# Formatta il messaggio per Matrix
MATRIX_MESSAGE="✉️ **SMS da:** $SENDER
🕒 **Data:** $DATE
💬 **Messaggio:** $MESSAGE"

# Crea un file temporaneo per salvare l'output del comando Python
TEMP_OUTPUT=$(mktemp)

# Invio tramite Matrix usando il nostro script Python
cd "$SCRIPT_DIR" && "$SCRIPT_DIR/sms_to_matrix.py" \
    --message "$MATRIX_MESSAGE" \
    --delete-after 60 >"$TEMP_OUTPUT" 2>&1

# Debug: stampa il contenuto del file temporaneo
if [ "$DEBUG" = "true" ]; then
    echo "----- Output del comando Python -----"
    cat "$TEMP_OUTPUT"
    echo "------------------------------------"
fi

# Estrai l'ID dell'evento dal file temporaneo
EVENT_ID=$(grep -o 'Event ID: \S\+' "$TEMP_OUTPUT" | cut -d ' ' -f 3)
rm -f "$TEMP_OUTPUT"

# Logging
echo "[$(date)] Messaggio inviato a Matrix con Event ID: $EVENT_ID" >>"$LOGFILE"
