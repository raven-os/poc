#!/usr/bin/env python3

import image
from tkinter import Tk, Toplevel, Frame, filedialog, StringVar, Button, Radiobutton, Label, LEFT, RIGHT, TOP, BOTTOM, BOTH, W, ttk

import config

from communication import startCom, stopCom

import math

class App(Tk):

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
        self.updateViewer()

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

        for elem in self.config:
            button = self.getButton(elem)

            if not button and "type" in self.config[elem] and self.config[elem]["type"] == "button" and "display" in self.config[elem] and self.config[elem]["display"]:
                Button(self.buttons, text=elem, command=buttons_function_ptr[self.config[elem]['function']]).pack(side=buttons_side_ptr[self.config[elem]["side"]])
            elif button and "display" in self.config[elem] and not self.config[elem]["display"]:
                button.destroy()
        self.image.update()

    def getButton(self, text):
        for button in self.buttons.winfo_children():
            if button['text'] == text:
                return button
        return None

    def bindEvents(self):
        self.bind("<Button-4>", self.mouse_wheel) # MouseWheel Up
        self.bind("<Button-5>", self.mouse_wheel) # MouseWheel Daoun

    def mouse_wheel(self, event):
        if (event.num == 4):
            self.image.zoomIn()
        else:
            self.image.zoomOut()

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

        self.image = image.Image(self.label)

        self.updateViewer()
        self.bindEvents()


if __name__ == "__main__":
    app = App()
    # app.style = ttk.Style()
    # #('clam', 'alt', 'default', 'classic')
    # app.style.theme_use("clam")
    startCom(app)
    app.mainloop()
    stopCom()
