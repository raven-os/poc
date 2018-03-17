# RavenProfile@forward

This is a gnome extension to handle `raven-os` profile.
It contains a list a profiles, and when an user will change the profile, it will broadcast the changes to all running `raven-os` applications through `Named Pipes`.

## Getting Started

### Prerequisites

This is a `gnome-shell-extension` so make sure you have the last version of **GNOME** environment. My version is _3.26.2_.

Check your version :
```
$ gnome-shell --version
```

The extension will search for `Named Pipes` in the `/raven_com` directory, so you have to create this directory and your applications have to create their `Named Pipe`s in it and give permissions (**666**).

```
$ sudo mkdir /raven_com
$ sudo chmod 777 /raven_com
```

### Installing


```
$ cp -r RavenProfile@forward ~/.local/share/gnome-shell/extensions
```
Now restart GNOME. Press `Alt + F2` and enter `r` or log out / log in

Now enable the extension :
```
$ gnome-shell-extension-tool -e RavenProfile@forward
```

If it doesn't work, use [`gnome-tweak-tool`](https://doc.ubuntu-fr.org/gnome-tweak-tool)
```
$ sudo apt-get install gnome-tweak-tool
$ gnome-tweak-tool
```

### How to use

Create a `Named Pipe` in `/raven_com` and read it to get informations about profile change.

```
$ cd /raven_com
$ sudo mkfifo this_is_a_pipe
$ sudo chmod 666 this_is_a_pipe
$ cat this_is_a_pipe
```
Use the extension to change profile. Get info in your pipe.

GLHF.
