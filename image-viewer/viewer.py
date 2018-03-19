#!/usr/bin/env python3

import PIL.Image
import PIL.ImageTk
from tkinter import Tk, Toplevel, Frame, filedialog, StringVar, Button, Radiobutton, Label, LEFT, RIGHT, TOP, BOTTOM, BOTH, W, ttk

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
        if not self.image:
            return
        if self.image.mode == "1": # bitmap image
            self.imageTk = PIL.ImageTk.BitmapImage(self.image, foreground="white")
        else:                   # photo image
            self.imageTk = PIL.ImageTk.PhotoImage(self.image)
        self.label.config(image=self.imageTk, bg="#000000")

    def defaultZoom(self):
        (_, _, width, height) = self.bbox(0, 0)
        if self.image.width >= self.image.height:
            self.min = width * -1
            self.max = width * 2
            (nwidth, nheight) = self.zoomRatioWidth(width)
        else:
            self.min = height * -1
            self.max = height * 2
            (nwidth, nheight) = self.zoomRatioHeight(height)
        self.image = self.image.resize((nwidth, nheight), PIL.Image.ANTIALIAS)
        self.backup = self.image.copy()


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
            self.defaultZoom()

            self.updateImage()

    def ask_preferencies(self, b):
        if not "should ask" in self.config[b]:
            return
        window = Toplevel(self)
        window.title("Select preferencies")
        window.geometry("300x300")
        v = {}
        for key in self.config[b]["should ask"]:
            frame = Frame(window)
            v[key] = StringVar()
            v[key].set(self.config[b]["should ask"][key][0])
            for elem in self.config[b]["should ask"][key]:
                Radiobutton(frame, text=elem, variable=v[key], value=elem).pack(anchor=W)
            frame.pack()
        window.mainloop()
        for elem in v:
            self.config[b][elem] = v[elem].get()

        print(self.config[b])
        del self.config[b]["should ask"]
        print(self.config[b])
        self.config.put(b, self.config[b])

    def save(self):
        pass

    def zoomRatioWidth(self, new_width):
        if new_width < 0:
            new_width = 0
        wpercent = (new_width / float(self.backup.width))
        hsize = int((float(self.backup.height) * float(wpercent)))
        return (new_width, hsize)

    def zoomRatioHeight(self, new_height):
        if new_height < 0:
            new_height = 0
        hpercent = (new_height / float(self.backup.height))
        wsize = int((float(self.backup.width) * float(hpercent)))
        return (wsize, new_height)

    def zoomIn(self, percent=10):
        tmp = percent + int(self.min * -1 / 100)
        if not (self.image and self.zooming + tmp < self.max):
            return
        self.zooming += tmp
        self.image = self.backup.resize(self.zoomRatioWidth(self.backup.width + self.zooming),
                                        PIL.Image.ANTIALIAS)

    def zoomOut(self, percent=10):
        tmp = percent + int(self.min * -1 / 100)
        if not (self.image and self.zooming - tmp > self.min):
            return
        self.zooming -= tmp
        self.image = self.backup.resize(self.zoomRatioWidth(self.backup.width + self.zooming),
                                        PIL.Image.ANTIALIAS)

    def rotate(self, rotation):
        if self.image:
            self.image = self.image.rotate(rotation, expand = True)
            self.backup = self.backup.rotate(rotation, expand = True)
            self.updateImage()

    def updateConfig(self, config):
        self.config = config
        self.updateViewer()

    def updateViewer(self):
        self.title(self.config['name']['value'])
        self.geometry("%dx%d" % (self.config['width']['value'], self.config['height']['value']))

        buttons_function_ptr = {
            "open": self.open,
            "save": self.save,
            "rotate_left": lambda: self.rotate(90),
            "rotate_right": lambda: self.rotate(-90)
        }
        buttons_side_ptr = {
            "left": LEFT,
            "right": RIGHT,
            "top": TOP,
            "bottom": BOTTOM
        }

        for elem in self.config:
            button = self.getButton(elem)

            if not button and "type" in self.config[elem] and self.config[elem]["type"] == "button" and "display" in self.config[elem] and self.config[elem]["display"]:
                Button(self.buttons, text=elem, command=buttons_function_ptr[self.config[elem]['function']]).pack(side=buttons_side_ptr[self.config[elem]["side"]])
            elif button and "display" in self.config[elem] and not self.config[elem]["display"]:
                button.destroy()
        self.updateImage()

    def getButton(self, text):
        for button in self.buttons.winfo_children():
            if button['text'] == text:
                return button
        return None

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

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.label = Label(self, padx=20, pady=10)
        self.label.grid(row=0, column=0)

        self.buttons = Frame(self)
        self.buttons.grid(row=1, column=0)

        self.update()

        self.image = None
        self.imageTk = None
        self.openBtn = None
        self.saveBtn = None
        self.zooming = 0

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
    # app.style = ttk.Style()
    # #('clam', 'alt', 'default', 'classic')
    # app.style.theme_use("clam")
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
