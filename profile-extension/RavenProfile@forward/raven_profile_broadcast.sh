#!/bin/sh

for entry in `ls /raven_com`; do
    echo "$1" > "/raven_com/$entry" &
done
