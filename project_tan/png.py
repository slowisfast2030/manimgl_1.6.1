from manim import *

# 下面这几行设置竖屏
config.frame_width = 9
config.frame_height = 16

config.pixel_width = 1080
config.pixel_height = 1920

class png(Scene):
    def construct(self):
        image = ImageMobject("ruler.png").scale(0.2)
        self.add(image)

        self.play(FadeIn(image))
        self.wait()
