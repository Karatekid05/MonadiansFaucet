#!/bin/bash
while true; do
    python3 bot.py >> bot.log 2>&1
    echo "Bot crashed or stopped. Restarting in 5 seconds..."
    sleep 5
done 