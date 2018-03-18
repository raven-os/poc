#!/bin/sh

for entry in `ls /raven_com`; do
    echo -n "$1" > "/raven_com/$entry" &
done
