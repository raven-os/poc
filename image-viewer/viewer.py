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
import math

class App(Tk):
    def updateImage(self):
        if (not self.image):
            return
        if self.image.mode == "1": # bitmap image
            self.imageTk = PIL.ImageTk.BitmapImage(self.image, foreground="white")
        else:                   # photo image
            self.imageTk = PIL.ImageTk.PhotoImage(self.image)
        self.label.config(image=self.imageTk, bg="#000000")

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
            self.image = PIL.Image.open(filename)
            self.backup = self.image.copy()
            self.updateImage()

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

    def zoom(self, x, y):
        if self.image and x > 0 and y > 0:
            self.image = self.backup.resize((x, y), PIL.Image.ANTIALIAS)

    def zoomRatio(self):
        if (self.image):
            new_width = self.backup.width + self.zooming
            if new_width < 0:
                new_width = 0
            wpercent = (new_width / float(self.backup.width))
            hsize = int((float(self.backup.height) * float(wpercent)))
            return (new_width, hsize)

    def zoomIn(self, percent=10):
        if self.image:
            self.zooming += percent
            self.zoom(self.zoomRatio()[0], self.zoomRatio()[1])

    def zoomOut(self, percent=10):
        if self.image and self.image.width > 10 and self.image.height > 10:
            self.zooming -= percent
            self.zoom(self.zoomRatio()[0], self.zoomRatio()[1])

    def rotate(self, rotation):
        if self.image:
            self.image = self.image.rotate(rotation)
            self.backup = self.backup.rotate(rotation)
            self.updateImage()


    def updateConfig(self, config):
        self.config = config
        self.updateViewer()

    def updateViewer(self):
        self.title(self.config['name'])
        self.geometry("%dx%d" % (self.config['width'], self.config['height']))

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

        actions = self.config['actions']
        for action in actions:
            if "display" in actions[action] and actions[action]["display"]:
                if (action == "open"):
                    if (self.openBtn is None):
                        self.openBtn = Button(self.buttons, text=action, command=buttons_function_ptr[action])
                    self.openBtn.pack(side=buttons_side_ptr[actions[action]["side"]])
                elif (action == "save"):
                    if (self.saveBtn is None):
                        self.saveBtn = Button(self.buttons, text=action, command=buttons_function_ptr[action])
                    self.saveBtn.pack(side=buttons_side_ptr[actions[action]["side"]])
                else:
                    Button(self.frame, text=action, command=buttons_function_ptr[action]).pack(side=buttons_side_ptr[actions[action]["side"]])

            if "display" in actions[action] and not actions[action]["display"]:
                if action == "open" and self.openBtn is not None:
                    self.openBtn.destroy()
                    self.openBtn = None
                if action == "save" and self.saveBtn is not None:
                    self.saveBtn.destroy()
                    self.saveBtn = None

        self.updateImage()

    def bindEvents(self):
        self.bind("<Button-4>", self.mouse_wheel)
        self.bind("<Button-5>", self.mouse_wheel)

    def mouse_wheel(self, event):
        if (event.num == 4):
            self.zoomIn()
        else:
            self.zoomOut()
        self.updateImage()



    def __init__(self):
        super(App, self).__init__()

        self.config = config.Config()

        self.label = Label(self, padx=10, pady=10)
        self.label.pack(fill = BOTH)

        self.buttons = Frame(self)
        self.buttons.pack(side = BOTTOM)

        self.image = None
        self.imageTk = None
        self.openBtn = None
        self.saveBtn = None
        self.zooming = 0

        self.rotationLeftBtn = Button(self.buttons, text="<-", command= lambda: self.rotate(90))
        self.rotationLeftBtn.pack(side = LEFT)
        self.rotationRightBtn = Button(self.buttons, text="->", command= lambda: self.rotate(-90))
        self.rotationRightBtn.pack(side = RIGHT)


        self.updateViewer()
        self.bindEvents()

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
