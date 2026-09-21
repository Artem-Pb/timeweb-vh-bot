#!/bin/bash
set -e

cd "$(dirname "$0")"

echo "== git pull =="
git pull

echo "== зависимости =="
.venv/bin/python3 -m pip install -r requirements.txt

echo "== проверка окружения =="
.venv/bin/python3 check_env.py

LOOP_PID=$(pgrep -f "while true.*main.py" || true)

if [ -z "$LOOP_PID" ]; then
    echo "== цикл автозапуска не найден, поднимаю с нуля =="
    nohup bash -c 'while true; do .venv/bin/python3 main.py; sleep 5; done' > autostart.log 2>&1 &
    disown
else
    echo "== цикл автозапуска уже работает (PID $LOOP_PID), перезапускаю бота =="
    BOT_PID=$(pgrep -f "\.venv/bin/python3 main\.py" || true)
    if [ -n "$BOT_PID" ]; then
        kill "$BOT_PID"
    fi
fi

sleep 6

NEW_PID=$(pgrep -f "\.venv/bin/python3 main\.py" || true)
if [ -n "$NEW_PID" ]; then
    echo "Бот работает, PID $NEW_PID"
else
    echo "ВНИМАНИЕ: бот не поднялся, последние строки autostart.log:"
    tail -n 20 autostart.log
    exit 1
fi
