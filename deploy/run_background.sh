#!/usr/bin/env bash
# Script per avviare il bot in background 24/7 su macOS / Linux
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
cd "$DIR"

mkdir -p logs
export PYTHONUNBUFFERED=1
echo "Avvio TravelBot in background..."
nohup .venv/bin/python main.py >> logs/bot.log 2>&1 &
PID=$!
echo "TravelBot avviato con successo! (PID: $PID)"
echo "Log disponibili in tempo reale su: logs/bot.log"
echo "Per verificare lo stato: tail -f logs/bot.log"
echo "Per arrestare il bot: kill $PID"
