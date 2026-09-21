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
    BOT_PIDS=$(pgrep -x -f "\.venv/bin/python3 main\.py" || true)
    if [ -n "$BOT_PIDS" ]; then
        echo "$BOT_PIDS" | xargs kill
    fi
fi

echo "== жду перезапуск (до 20 секунд: SIGTERM + пауза цикла + старт процесса) =="
NEW_PID=""
for i in $(seq 1 10); do
    sleep 2
    NEW_PID=$(pgrep -x -f "\.venv/bin/python3 main\.py" || true)
    if [ -n "$NEW_PID" ]; then
        break
    fi
done

if [ -n "$NEW_PID" ]; then
    echo "Бот работает, PID $NEW_PID"
else
    echo "ВНИМАНИЕ: бот не поднялся за 20 секунд, последние строки autostart.log:"
    tail -n 20 autostart.log
    exit 1
fi
