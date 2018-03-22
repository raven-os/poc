import PIL.Image
import PIL.ImageTk
from filters import Filters

class Image():
    def __init__(self, label):
        self.label = label # label to display image
        self.image  = None # PIL image modified for display
        self.backup = None # PIL image backup (base for zoom)
        self.imageTk = None # PIL TK image displayed
        self.filename = None # filename
        self.zooming = 0 # zoom in range [min..max]
        self.min = 0 # minimum size of image
        self.max = 0 # maximum size of image
        self.f = Filters();

    def open(self, filename):
        self.filename = filename
        self.image = PIL.Image.open(filename)
        self.backup = self.image.copy()

    def update(self):
        if not self.image:
            return
        if self.image.mode == "1": # bitmap image
            self.imageTk = PIL.ImageTk.BitmapImage(self.image, foreground="white")
        else:                   # photo image
            self.imageTk = PIL.ImageTk.PhotoImage(self.image)
        self.label.config(image=self.imageTk, bg="#000000")

    def _setSizeUnsafe(self, width, height):
        self.image = self.image.resize((width, height), PIL.Image.ANTIALIAS)
        self.backup = self.image.copy()
        self.update()

    def setDefaultZoomAndLimits(self, width, height):
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
        self.zooming = 0
        self.update()

    def zoomRatioWidth(self, new_width):
        if new_width <= 0:
            new_width = 1
        wpercent = (new_width / float(self.backup.width))
        hsize = int((float(self.backup.height) * float(wpercent)))
        if hsize <= 0:
            hsize = 1
        return (new_width, hsize)

    def zoomRatioHeight(self, new_height):
        if new_height <= 0:
            new_height = 1
        hpercent = (new_height / float(self.backup.height))
        wsize = int((float(self.backup.width) * float(hpercent)))
        if wsize <= 0:
            wsize = 1
        return (wsize, new_height)

    def zoomIn(self, percent=10):
        tmp = percent + int(self.min * -1 / 100)
        if not (self.image and self.zooming + tmp < self.max):
            return
        self.zooming += tmp
        self.image = self.backup.resize(self.zoomRatioWidth(self.backup.width + self.zooming),
                                        PIL.Image.ANTIALIAS)
        self.update()

    def zoomOut(self, percent=10):
        tmp = percent + int(self.min * -1 / 100)
        if not (self.image and self.zooming - tmp > self.min):
            return
        self.zooming -= tmp
        self.image = self.backup.resize(self.zoomRatioWidth(self.backup.width + self.zooming),
                                        PIL.Image.ANTIALIAS)
        self.update()

    def rotate(self, rotation):
        if self.image:
            self.image = self.image.rotate(rotation, expand = True)
            self.backup = self.backup.rotate(rotation, expand = True)
            self.update()

    def save(self):
        if self.image:
            self.image.save(self.filename)

    def filters(self, filter_type):
        if self.image:
            self.f.setImage(self.image)
            if filter_type == "negatif":
                self.image = self.f.negatif()
            elif filter_type == "blackAndWhite":
                self.image = self.f.blackAndWhite()
            elif filter_type == "transpose":
                self.image = self.f.transpose()
            self.update()
