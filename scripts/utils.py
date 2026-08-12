import os

import pygame

BASE_IMG_PATH = 'data/images/'

def load_image(path):
    img = pygame.image.load(BASE_IMG_PATH + path).convert()
    img.set_colorkey((0, 0, 0))
    return img

def load_images(path):
    images = []
    # His original code doesn't work on macOs/linux since 
    # macOs & Linux have ordering of files that may be
    # different since in Windows it is alphabetical. 
    # Might need to do sorted(os.listdir(...)) instead.
    # Windows file order doesn't require sorted().
    # In Linux 'image10' may be ordered before 'image08' and
    # before or after 'image01' since it goes alphabetically
    # by index names each individual index is ordered. Linux
    # will not see 10 as ten but 10 as one, zero.
    for img_name in sorted(os.listdir(BASE_IMG_PATH + path)):
        images.append(load_image(path + '/' + img_name))
    return images

class Animation:
    def __init__(self, images, img_dur=5, loop=True):
        self.images = images
        self.loop = loop
        self.img_duration = img_dur
        self.done = False
        self.frame = 0

    # The image list aren't actually copied and are
    # passed by reference which helps to save memory
    def copy(self):
        return Animation(self.images, self.img_duration, self.loop)
    # updates frame number to reset if it reaches the last frame and img_duration
    def update(self):
        if self.loop:
            self.frame = (self.frame + 1) % (self.img_duration * len(self.images))
        else:
            self.frame = min(self.frame + 1, self.img_duration * len(self.images) - 1)
            if self.frame >= self.img_duration * len(self.images) - 1:
                self.done = True

    def img(self):
        return self.images[int(self.frame / self.img_duration)]