#!/bin/bash
if [ -f ~/.cloudflared/tutor.pid ]; then
    PID=$(cat ~/.cloudflared/tutor.pid)
    kill $PID && echo "Cloudflared tunnel (PID $PID) stopped."
    rm ~/.cloudflared/tutor.pid
else
    echo "No tutor tunnel PID file found."
fi
