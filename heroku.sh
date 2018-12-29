#!/bin/bash
gunicorn -b 0.0.0.0:$PORT app:app --daemon --log-file -
python worker.py
