#!/bin/bash
FPATH=$(dirname "$2")
mkdir -p "$FPATH"
cp "$1" "$2"
chown $3:$3 -R "$2"

