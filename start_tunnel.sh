#!/bin/bash
cloudflared tunnel --config ~/.cloudflared/tutor.yml run tutor &
echo $! > ~/.cloudflared/tutor.pid
echo "Cloudflared tunnel started with PID $(cat ~/.cloudflared/tutor.pid)"