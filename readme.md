# Matrix SMS Bot

A simple Matrix bot that forwards SMS messages from Gammu SMS daemon to a Matrix room.

## Overview

This project consists of two main components:

1. A Bash script that captures SMS messages from Gammu and forwards them
2. A Python Matrix bot that manages the Matrix communication

## Requirements

-   Python 3.6+
-   Gammu SMS daemon
-   Matrix account for the bot
-   Required Python packages:
    -   matrix-nio
    -   python-dotenv

## Installation

1. Clone this repository

```bash
git clone https://github.com/yourusername/smsbot-matrix.git
cd smsbot-matrix
```

2. Install required Python packages

```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your Matrix credentials

```
MATRIX_HOMESERVER="https://matrix.example.org"
MATRIX_USER="@smsbot:example.org"
MATRIX_PASSWORD="your_password"
MATRIX_ACCESS_TOKEN="optional_access_token"
MATRIX_ROOM_ID="!roomID:example.org"
```

## Configuration

### Gammu Setup

Make sure Gammu is installed and properly configured to receive SMS messages. Configure Gammu to execute `sms_to_matrix.sh` when an SMS is received.

### Bot Setup

The bot will use either the provided access token or the username/password to authenticate with the Matrix homeserver.

## Usage

### Sending a test message

```bash
python send_matrix_message.py
```

This will send a test message to the configured Matrix room and delete it after 30 seconds.

### SMS Forwarding

The `sms_to_discord.sh` script captures incoming SMS messages from Gammu and forwards them. Despite the name, it will be modified to use the Matrix API instead of Discord.

## File Structure

-   `matrix_bot.py` - Core Matrix bot functionality
-   `send_matrix_message.py` - Example script to send messages
-   `sms_to_discord.sh` - SMS capture script (to be updated for Matrix)
-   `.env` - Configuration file (not in git)
-   `.gitignore` - Standard Python gitignore

## Security Notes

-   The access token is stored in `.token_smsbot.json` which is ignored by git
-   Never commit sensitive credentials to the repository
