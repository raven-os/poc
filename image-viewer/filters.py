import PIL.Image
import PIL.ImageOps

class Filters():
    def __init__(self):
        self.col = 0
        self.row = 0
        self.img = None

    def setImage(self, image):
        self.img = image
        self.col, self.row = self.img.size

    def negatif(self):
        image = self.img

        if image.mode == 'RGBA':
            r,g,b,a = image.split()
            image = PIL.Image.merge('RGB', (r,g,b))
        try:
            inverted_image = PIL.ImageOps.invert(image)
        except:
            return image
        return inverted_image
        """Nope
        try:
            imgF = PIL.Image.new(self.img.mode, self.img.size)
            for i in range(self.row):
                for j in range(self.col):
                    pixel = self.img.getpixel((j,i))
                    p = (255 - pixel[0], 255 - pixel[1], 255 - pixel[2])
                    imgF.putpixel((j,i), p)
            return imgF
        except:
            return self.img
        """

    def transpose(self):
        imgF = self.img.transpose(PIL.Image.FLIP_LEFT_RIGHT)
        return imgF

    def blackAndWhite(self):
        imgF = PIL.ImageOps.grayscale(self.img)
        return imgF
