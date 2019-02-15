#!/bin/bash

PATH_TO_ADDON="$1"
shift
PATH_TO_SETTINGS="$1"
shift
PATH_TO_TIMESTAMP="$1"
shift
export PYTHONPATH="$PATH_TO_ADDON/resources/lib:$PATH_TO_ADDON/resources/lib/standalone/python:$PYTHONPATH"

python "$PATH_TO_ADDON/resources/lib/standalone/linux/downloadScanner.py" "$PATH_TO_SETTINGS" "$PATH_TO_TIMESTAMP" $@
