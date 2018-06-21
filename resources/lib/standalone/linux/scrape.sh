#!/bin/bash

PATH_TO_ADDON="$1"
PATH_TO_SETTINGS="$2"
PATH_TO_LOG="$3"

export PYTHONPATH="$PATH_TO_ADDON/resources/lib:$PATH_TO_ADDON/resources/lib/standalone/python:$PYTHONPATH"

python "$PATH_TO_ADDON/resources/lib/torrent/scrape.py" "$PATH_TO_SETTINGS" > "$PATH_TO_LOG"
