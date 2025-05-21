#!/bin/bash
# filepath: /Users/meska/Dev/Mecom/smsbot-matrix/test_sms.sh

# Questo script testa il sistema di invio messaggi utilizzando l'SMS di esempio

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SMS_FILE="$SCRIPT_DIR/example_sms.txt"

# Esegue lo script di invio con il file di esempio
echo "[+] Eseguo test con il file di esempio:"
cat "$SMS_FILE"
echo "-----------------------------------------"

# Esecuzione dello script
"$SCRIPT_DIR/sms_to_matrix.sh" "RECEIVED" "$SMS_FILE"
