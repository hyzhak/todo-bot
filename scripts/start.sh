#!/usr/bin/env bash

export PYTHONPATH=${PYTHONPATH}:$(pwd)

echo "PYTHONPATH"
echo ${PYTHONPATH}

echo "====================================================="
echo ""
echo " Setup"
echo ""
echo "====================================================="

python ./boilerplate/main.py --setup

echo "====================================================="
echo ""
echo " Start"
echo ""
echo "====================================================="

gunicorn boilerplate.wsgi:app --bind 0.0.0.0:${API_PORT} --log-file - --reload --worker-class aiohttp.worker.GunicornWebWorker
