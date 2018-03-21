#!/usr/bin/env python3

import image
from tkinter import Tk, Toplevel, Frame, filedialog, StringVar, Button, Radiobutton, Label, LEFT, RIGHT, TOP, BOTTOM, BOTH, W, ttk, Scrollbar, VERTICAL, NE, SE, Canvas
import tkinter as tk
import config

from communication import startCom, stopCom

import math
import os
import glob
import re
from enum import Enum

from pathlib import Path

from scrolledWindow import ScrolledWindow


class Mode(Enum):
    GALLERY = 1
    VIEWER = 2

class App(Tk):


    def findImageList(self, filename):
        self.dir = os.path.dirname(filename)
        self.list = []
        self.listIndex = 0
        types = ("*.jpeg", "*.jpg", "*.png", "*.gif", "*.bmp")
        for file in os.listdir(self.dir):
            if re.match(".*\.jpeg|.*\.jpg|.*\.png|.*\.gif|.*\.bmp", file):
                self.list.append(file)
                if (self.dir +"/" + file == filename):
                    self.listIndex = len(self.list) -1

    def displayGallery(self):
        self.findImageList(str(Path.home()) + "/Downloads/kek")
        (_, _, width, height) = self.bbox(0, 0)

        imageWidth = self.config["gallery_miniature_size"]["value"]
        #self.imgWidth = math.floor((width - self.column * 2 * 11) / self.column) - 2
        self.column = math.ceil((width - 15) / (imageWidth + 20 + 16))
        if (imageWidth + 20) * self.column + 10 > width:
            self.column -= 1
        #calcul fill blank empty end line

        col = 0
        row = 0
        self.listLabel = []
        self.listImage = []
        for img in self.list:
            label = Label(self.gallery.scrollwindow)
            label.bind("<Button-1>", lambda evt, i=img: self.galleryImageClick(self.dir + "/" + i))

            label.grid(row=row, column=col, padx=10, pady=10)
            self.listLabel.append(label)
            col += 1
            if col >= self.column:
                row += 1
                col = 0
            im = image.Image(label)
            im.open(self.dir + "/" + img)
            im._setSizeUnsafe(imageWidth, imageWidth)
            self.listImage.append(im)

    def galleryImageClick(self, filename):
        self.switchMode()
        self.image.open(filename)
        (_, _, width, height) = self.bbox(0, 0)
        self.image.setDefaultZoomAndLimits(width, height)
        self.findImageList(filename)


    def navigate(self, i):
        if len(self.list) < 2:
            return
        self.listIndex = (self.listIndex + i) % len(self.list)
        self.image.open(self.dir + "/" + self.list[self.listIndex])
        (_, _, width, height) = self.bbox(0, 0)
        self.image.setDefaultZoomAndLimits(width, height)


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
            self.image.open(filename)
            (_, _, width, height) = self.bbox(0, 0)
            self.image.setDefaultZoomAndLimits(width, height)
            self.findImageList(filename)

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

    def updateConfig(self, config):
        self.config = config
        self.title(self.config['name']['value'])
        self.geometry("%dx%d" % (self.config['width']['value'], self.config['height']['value']))

        if self.mode == Mode.GALLERY:
            self.updateGallery()
        elif self.mode == Mode.VIEWER:
            self.updateViewer()

    def updateGallery(self):
        for item in self.gallery.scrollwindow.winfo_children():
            item.destroy()
        for item in self.buttonsGallery.winfo_children():
            item.destroy()
        Button(self.buttonsGallery, text="Go to Viewer", command=self.switchMode).pack(side=LEFT)# need config
        self.displayGallery()


    def updateViewer(self):
        self.title(self.config['name']['value'])
        self.geometry("%dx%d" % (self.config['width']['value'], self.config['height']['value']))


        buttons_function_ptr = {
            "open": self.open,
            "save": self.image.save,
            "rotate_left": lambda: self.image.rotate(90),
            "rotate_right": lambda: self.image.rotate(-90)
        }
        buttons_side_ptr = {
            "left": LEFT,
            "right": RIGHT,
            "top": TOP,
            "bottom": BOTTOM
        }
        Button(self.buttonsViewer, text="Go to Gallery", command=self.switchMode).pack(side=LEFT)# need config
        Button(self.buttonsViewer, text="->", command=lambda: self.navigate(1)).pack(side=RIGHT)# need config
        Button(self.buttonsViewer, text="<-", command=lambda:self.navigate(-1)).pack(side=LEFT)# need config


        for elem in self.config:
            button = self.getButton(elem)

            if not button and "type" in self.config[elem] and self.config[elem]["type"] == "button" and "display" in self.config[elem] and self.config[elem]["display"]:
                Button(self.buttonsViewer, text=elem, command=buttons_function_ptr[self.config[elem]['function']]).pack(side=buttons_side_ptr[self.config[elem]["side"]])
            elif button and "display" in self.config[elem] and not self.config[elem]["display"]:
                button.destroy()
        self.image.update()
        self.bindEvents()

    def getButton(self, text):
        for button in self.buttonsViewer.winfo_children():
            if button['text'] == text:
                return button
        return None

    def bindEvents(self):
        self.bind("<Button-4>", self.mouse_wheel) # MouseWheel Up
        self.bind("<Button-5>", self.mouse_wheel) # MouseWheel Daoun

    def unbindEvents(self):
        self.unbind("<Button-4>")
        self.unbind("<Button-5>")

    def mouse_wheel(self, event):
        if (event.num == 4):
            self.image.zoomIn()
        else:
            self.image.zoomOut()

    def switchMode(self):
        if self.mode == Mode.GALLERY:
            self.gallery._unbound_to_mousewheel(None)
            self.initViewer()
        elif self.mode == Mode.VIEWER:
            self.unbindEvents()
            self.initGallery()

    def initGallery(self):
        self.unbindEvents()
        self.mode = Mode.GALLERY
        if self.label:
            self.label.destroy()
            self.label = None
        if self.buttonsViewer:
            self.buttonsViewer.destroy()
            self.buttonsViewer = None
        self.gallery = ScrolledWindow(self)
        self.gallery.grid(row=0, column=0)
        self.buttonsGallery = Frame(self)
        self.buttonsGallery.grid(row=1, column=0)
        self.listLabel = []
        self.update()
        self.updateGallery()

    def initViewer(self):
        self.mode = Mode.VIEWER
        if self.gallery:
            self.gallery.destroyAll()
            self.gallery = None
        if self.buttonsGallery:
            self.buttonsGallery.destroy()
            self.buttonsGallery = None
        self.label = Label(self, padx=20, pady=10)
        self.label.grid(row=0, column=0)
        self.buttonsViewer = Frame(self)
        self.buttonsViewer.grid(row=1, column=0)
        self.image = image.Image(self.label)
        self.update()
        self.updateViewer()

    def __init__(self):
        super(App, self).__init__()

        self.config = config.Config()
        self.title(self.config['name']['value'])
        self.geometry("%dx%d" % (self.config['width']['value'], self.config['height']['value']))

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.gallery = None # frame containing images in GALLERY mode
        self.label = None # label containing the image in VIEWER Mode
        self.buttonsGallery = None # frame containing gallery buttons
        self.buttonsViewer = None # frame containing viewer buttons
        self.imageWidth = 60
        self.initGallery()


if __name__ == "__main__":
    app = App()
    # app.style = ttk.Style()
    # #('clam', 'alt', 'default', 'classic')
    # app.style.theme_use("clam")
    startCom(app)
    app.mainloop()
    stopCom()
