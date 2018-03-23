#!/bin/sh

for entry in `ls /raven_com`; do
    echo -n "$1" > "/raven_com/$entry" &
done
gsettings set org.gnome.desktop.background picture-uri file://$HOME/.local/share/gnome-shell/extensions/RavenProfile@forward/b$1.jpg
