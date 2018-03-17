#!/usr/bin/env python3

import PIL.Image
import PIL.ImageTk
from tkinter import Tk, Frame, filedialog, StringVar, Button, Radiobutton, Label, LEFT, RIGHT, TOP, BOTTOM, BOTH

import config

class App(Tk):
    def chg_image(self):
        if self.frame.im.mode == "1": # bitmap image
            self.img = PIL.ImageTk.BitmapImage(self.frame.im, foreground="white")
        else:                   # photo image
            self.img = PIL.ImageTk.PhotoImage(self.frame.im)
        self.label.config(image=self.img, bg="#000000",
                          width=self.img.width(), height=self.img.height())

    def open(self):
        filename = filedialog.askopenfilename()
        if filename != "":
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

    def __init__(self):
        super(App, self).__init__()

        self.config = config.Config()

        self.title(self.config['name']['value'])
        self.geometry("%dx%d" % (self.config['width']['value'], self.config['height']['value']))

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


if __name__ == "__main__":
    app = App()
    app.mainloop()
