#!/bin/bash
pip install poetry==1.7.1 poetry-plugin-export
poetry export -f requirements.txt --output requirements.txt --without-hashes
ls -la requirements.txt
wc -l requirements.txt
pip wheel --no-cache-dir --no-deps --wheel-dir wheels -r requirements.txt
ls -la wheels
