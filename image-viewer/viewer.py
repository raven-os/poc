#!/usr/bin/env python3

import image
from tkinter import Tk, Toplevel, Frame, filedialog, StringVar, Button, Radiobutton, Label, LEFT, RIGHT, TOP, BOTTOM, BOTH, W, ttk, Scrollbar, VERTICAL, NE, SE, Canvas, Message
import tkinter as tk
import config

from communication import startCom, stopCom

import math
import os
import glob
import re
from enum import Enum
import PIL.ImageTk
import PIL.Image

from threading import Thread
from queue import Queue
from queue import Empty


from os.path import expanduser

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
        self.findImageList(expanduser(self.config["base_path"]["value"]) + self.config["image_directory"]["value"] + "/")
        (_, _, width, _) = self.bbox(0, 0)

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

    def updateGalleryGrid(self, event):
        (_, _, width, _) = self.bbox(0, 0)
        imageWidth = self.config["gallery_miniature_size"]["value"]
        self.column = math.ceil((width - 15) / (imageWidth + 20 + 16))
        if (imageWidth + 20) * self.column + 10 > width:
            self.column -= 1
        col = 0
        row = 0
        for l in self.listLabel:
            for children in self.gallery.scrollwindow.children.values():
                if children == l:
                    info = children.grid_info()
                    if info['row'] != row or info['column'] != col:
                        l.grid(row=row, column=col, padx=10, pady=10)
            col += 1
            if col >= self.column:
                row += 1
                col = 0

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
        filename = filedialog.askopenfilename(initialdir=self.config["base_path"]["value"] + self.config["image_directory"]["value"], filetypes = ftypes)
        if filename:
            self.image.open(filename)
            (_, _, width, height) = self.bbox(0, 0)
            self.image.setDefaultZoomAndLimits(width, height)
            self.findImageList(filename)

    def ask_preferencies(self, b):
        if not "should ask" in self.config[b]:
            return
        popup = Toplevel(self)
        popup.title("Select options for %s" % b)
        popup.geometry("400x200")
        Message(popup, text=self.config[b]["message"] ,width=100).pack()
        v = {}
        for key in self.config[b]["should ask"]:
            pframe = Frame(popup)
            v[key] = StringVar()
            v[key].set(self.config[b]["should ask"][key][0])
            for elem in self.config[b]["should ask"][key]:
                Radiobutton(pframe, text=elem, variable=v[key], value=elem).pack(anchor=W)
            pframe.pack()
        del self.config[b]["should ask"]
        def _test(): # quit then destroy windows
            popup.quit()
            popup.destroy()
        Button(popup, text="OK", command=_test).pack()
        popup.protocol('WM_DELETE_WINDOW', _test)
        popup.mainloop()
        for elem in v:
            self.config[b][elem] = v[elem].get()
        self.config.put(b, self.config[b])

    def updateConfig(self, config):
        self.config = config
        self.title(self.config['name']['value'])
        self.geometry("%dx%d" % (self.config['width']['value'], self.config['height']['value']))
        self.tk_setPalette(background=self.config["color"]["background"],
                           foreground=self.config["color"]["foreground"])
        self.updateInner()

    def updateInner(self):
        if self.mode == Mode.GALLERY:
            self.updateGallery()
        elif self.mode == Mode.VIEWER:
            self.updateViewer()

    def updateGallery(self):
        buttons_function_ptr = {
            "viewer": self.switchMode
        }
        buttons_side_ptr = {
            "left": LEFT,
            "right": RIGHT,
            "top": TOP,
            "bottom": BOTTOM
        }
        self.findImageList(expanduser(self.config["base_path"]["value"]) + self.config["image_directory"]["value"] + "/")

        for item in self.gallery.scrollwindow.winfo_children():
            item.destroy()
        for item in self.buttonsGallery.winfo_children():
            item.destroy()
        self.gallery.update_colors()
        for elem in self.config:

            if "type" in self.config[elem] and self.config[elem]["type"] == "button" and "display" in self.config[elem] and self.config[elem]["display"] == "gallery":
                if "image" in self.config[elem] and self.config[elem]["image"]:
                    self.imgButton[elem] = PIL.ImageTk.PhotoImage(PIL.Image.open(self.config[elem]["image"]).resize((30, 30), PIL.Image.ANTIALIAS))
                else:
                    self.imgButton[elem] = None
                if elem == "Viewer" and len(self.list) <= 0:
                    Button(self.buttonsGallery, image=self.imgButton[elem], text=elem, command=buttons_function_ptr[self.config[elem]['function']]).pack(side=buttons_side_ptr[self.config[elem]["side"]])

        self.displayGallery()

    def updateViewer(self):
        buttons_function_ptr = {
            "open": self.open,
            "save": self.image.save,
            "rotate_left": lambda: self.image.rotate(90),
            "rotate_right": lambda: self.image.rotate(-90),
            "next": lambda: self.navigate(1),
            "prev": lambda: self.navigate(-1),
            "gallery": self.switchMode,
            "negatif": lambda: self.image.filters("negatif"),
            "transpose": lambda: self.image.filters("transpose"),
            "blackAndWhite": lambda: self.image.filters("blackAndWhite")
        }
        buttons_side_ptr = {
            "left": LEFT,
            "right": RIGHT,
            "top": TOP,
            "bottom": BOTTOM
        }
        for child in self.buttonsViewer.winfo_children():
            child.destroy()
        for elem in self.config:

            # button handling
            if "type" in self.config[elem] and self.config[elem]["type"] == "button" and "display" in self.config[elem] and self.config[elem]["display"] == "viewer":
                if "image" in self.config[elem] and self.config[elem]["image"]:
                    self.imgButton[elem] = PIL.ImageTk.PhotoImage(PIL.Image.open(self.config[elem]["image"]).resize((30, 30), PIL.Image.ANTIALIAS))
                else:
                    self.imgButton[elem] = None
                Button(self.buttonsViewer, borderwidth=0, image=self.imgButton[elem], text=elem, command=buttons_function_ptr[self.config[elem]['function']]).pack(side=buttons_side_ptr[self.config[elem]["side"]])

            if "shortcut" in self.config[elem]:
                self.bind(self.config[elem]["shortcut"], self.shortcut)
        self.image.update()
        self.bindEvents()

    def bindEvents(self):
        self.bind("<Button-4>", self.mouse_wheel) # MouseWheel Up
        self.bind("<Button-5>", self.mouse_wheel) # MouseWheel Daoun

    def unbindEvents(self):
        self.unbind("<Button-4>")
        self.unbind("<Button-5>")
        for elem in self.config:
            if "shortcut" in self.config[elem]:
                self.unbind(self.config[elem]["shortcut"])


    def shortcut(self, event):
        def _modifiers(event):
            modifiers = []
            if event.state & 1:
                modifiers.append('Shift')
            if event.state & 2:
                modifiers.append('Caps_Lock')
            if event.state & 4:
                modifiers.append('Control')
            if event.state & 8:
                modifiers.append('Alt_L')
            if event.state & 10:
                modifiers.append('Num_Lock')
            if event.state & 80:
                modifiers.append('Alt_R')
            return '-'.join(modifiers)
        modifiers = _modifiers(event)
        if len(modifiers) > 0:
            modifiers += "-"
        shortcut = "<" + modifiers + event.keysym + ">"
        buttons_function_ptr = {
            "open": self.open,
            "save": self.image.save,
            "rotate_left": lambda: self.image.rotate(90),
            "rotate_right": lambda: self.image.rotate(-90),
            "next": lambda: self.navigate(1),
            "prev": lambda: self.navigate(-1),
            "gallery": self.switchMode,
            "negatif": lambda: self.image.filters("negatif"),
            "transpose": lambda: self.image.filters("transpose"),
            "blackAndWhite": lambda: self.image.filters("blackAndWhite")
        }
        for elem in self.config:
            if "shortcut" in self.config[elem] and self.config[elem]["shortcut"] == shortcut:
                buttons_function_ptr[self.config[elem]['function']]()


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
        self.gallery.bind("<Configure>", self.updateGalleryGrid)

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

    def read_queue(self):
        try:
            tmp = self.queue.get_nowait()
            self.updateConfig(config.Config(config = tmp))
        except Empty:
            pass
        self.after(100, self.read_queue)

    def __init__(self):
        super().__init__()

        self.config = config.Config()
        self.title(self.config['name']['value'])
        self.geometry("%dx%d" % (self.config['width']['value'], self.config['height']['value']))
        self.tk_setPalette(background=self.config["color"]["background"],
                           foreground=self.config["color"]["foreground"])

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.gallery = None # frame containing images in GALLERY mode
        self.label = None # label containing the image in VIEWER Mode
        self.buttonsGallery = None # frame containing gallery buttons
        self.buttonsViewer = None # frame containing viewer buttons
        self.imgButton = {}

        self.queue = Queue()
        self.after(100, self.read_queue)

        self.initGallery()

if __name__ == "__main__":
    app = App()
    startCom(app)
    app.mainloop()
    stopCom()
