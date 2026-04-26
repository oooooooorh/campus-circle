#!/bin/bash
# 启动 Gunicorn 并绑定 FastAPI
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind=0.0.0.0:8000 --timeout 600
