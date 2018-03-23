#!/bin/sh

for entry in `ls /raven_com`; do
    echo -n "$1" > "/raven_com/$entry" &
done
gsettings set org.gnome.desktop.background picture-uri file://$HOME/.local/share/gnome-shell/extensions/RavenProfile@forward/b$1.jpg

[ "$1" = "1" ] && gsettings set org.gnome.shell.extensions.dash-to-dock dock-position LEFT;

[ "$1" = "2" ] && gsettings set org.gnome.shell.extensions.dash-to-dock dock-position BOTTOM;

[ "$1" = "3" ] && gsettings set org.gnome.shell.extensions.dash-to-dock dock-position RIGHT;
