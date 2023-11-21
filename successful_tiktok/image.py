from manimlib import *

class test(Scene):
    def construct(self):
        image = ImageMobject("dall-path.png").scale(1.5)
        self.add(image)

