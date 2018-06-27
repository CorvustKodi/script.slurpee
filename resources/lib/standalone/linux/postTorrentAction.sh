#!/bin/bash

PATH_TO_ADDON="$1"
PATH_TO_SETTINGS="$2"
PATH_TO_LOG="$3"

export PYTHONPATH="$PATH_TO_ADDON/resources/lib:$PATH_TO_ADDON/resources/lib/standalone/python:$PYTHONPATH"

if [[ "x$PATH_TO_LOG" == "x" ]]; then
  python "$PATH_TO_ADDON/resources/lib/standalone/linux/postTorrentAction.py" "$PATH_TO_SETTINGS"
else
  python "$PATH_TO_ADDON/resources/lib/stanalone/linux/postTorrentAction.py" "$PATH_TO_SETTINGS" > "$PATH_TO_LOG"
fi
