#!/usr/bin/env python3

import PIL.Image
import PIL.ImageTk
from tkinter import Tk, Frame, filedialog, StringVar, Button, Radiobutton, Label, LEFT, RIGHT, TOP, BOTTOM, BOTH

import config

import os
import errno
from threading import Thread
import select
from time import sleep
stop = False

class App(Tk):
    def chg_image(self):
        if self.frame.im.mode == "1": # bitmap image
            self.img = PIL.ImageTk.BitmapImage(self.frame.im, foreground="white")
        else:                   # photo image
            self.img = PIL.ImageTk.PhotoImage(self.frame.im)
        self.label.config(image=self.img, bg="#000000",
                          width=self.img.width(), height=self.img.height())

    def open(self):
        ftypes = [
            ("Images", "*.jpeg *.jpg *.png *.png *.gif *.bmp"),
            ("JPEG", "*.jpeg"),
            ("JPG", "*.jpg"),
            ("PNG", "*.png"),
            ("GIF", "*.gif"),
            ("BMP", "*.bmp")
        ]
        filename = filedialog.askopenfilename(initialdir="~/Downloads", filetypes = ftypes)
        if filename:
            self.frame.im = PIL.Image.open(filename)
            self.chg_image()

    def ask_preferencies(self, b):
        window = Tk()
        window.title("Select preferencies")
        for key in self.config[b]["should ask"]:
            frame = Frame(window)
            v = StringVar()
            for elem in self.config[b]["should ask"][key]:
                Radiobutton(frame, text=elem, variable=v, value=elem).pack()
            print(v)
            self.config[key] = v
        frame.pack()
        window.mainloop()
        del self.config[b]["should ask"]
        self.config.put(b, self.config[b])


    def save(self):
        self.ask_preferencies("Scroll")
        pass

    def zoomIn(self, percent=10):
        pass

    def zoomOut(self, percent=10):
        pass

    def updateConfig(self, config):
        self.config = config
        self.updateViewer()

    def updateViewer(self):
        self.title(self.config['name']['value'])
        self.geometry("%dx%d" % (self.config['width']['value'], self.config['height']['value']))


    def __init__(self):
        super(App, self).__init__()

        self.config = config.Config()

        self.updateViewer()

        self.frame = Frame(self)
        buttons_function_ptr = {
            "open": self.open,
            "save": self.save
            }
        buttons_side_ptr = {
            "left": LEFT,
            "right": RIGHT,
            "top": TOP,
            "bottom": BOTTOM
            }
        for elem in self.config:
            if "type" in self.config[elem]:
                if self.config[elem]["type"] == "button":
                    Button(self.frame, text=elem, command=buttons_function_ptr[self.config[elem]["function"]]).pack(side=buttons_side_ptr[self.config[elem]["side"]])


        self.frame.pack(side=TOP, fill=BOTH)

        self.label = Label(self)
        self.label.pack()

        self.frame.pack()


def read_fifo(app):
    fd = -1
    while (not stop):
        try:
            if fd == -1:
                print("Open fifo")
                fd = os.open("/raven_com/fifo", os.O_RDONLY | os.O_NONBLOCK)
            data = os.read(fd, 1)
            if not stop and len(data) > 0:
                print("Read: {0}".format(data))
                if (b'1' in data):
                    app.updateConfig(config.Config(config = "configs/config1.json"))
                elif (b'2' in data):
                    app.updateConfig(config.Config(config = "configs/config2.json"))

            sleep(0.1)
        except OSError as oe:
            print(oe)
    print("Close fifo")
    os.close(fd)

def createFifo():
    try:
        os.mkfifo("/raven_com/fifo")
    except OSError as oe:
        if (oe.errno != errno.EEXIST):
            return -1
    return 0

if __name__ == "__main__":
    app = App()
    ret = createFifo()

    if ret != 0:
        print("Cannot create communication channel for profile:")
        print("sudo mkdir /raven_com && sudo chmod 777 /raven_com")
    else:
        thread = Thread(target = read_fifo, args=[app])
        thread.start()

    app.mainloop()
    stop = True

    if ret == 0:
        thread.join()
        os.remove("/raven_com/fifo")
