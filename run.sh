#!/bin/bash
cd "$(dirname "$0")"

# 가상환경이 활성화되어 있지 않은 경우에만 activate
if [ -z "$VIRTUAL_ENV" ]; then
    source venv/bin/activate
fi

python yt_mp3.py
