from manimlib.constants import *
from manimlib.mobject.geometry import Rectangle
from manimlib.utils.config_ops import digest_config


class ScreenRectangle(Rectangle):
    CONFIG = {
        "aspect_ratio": 16.0 / 9.0,
        "height": 4
    }

    def __init__(self, **kwargs):
        Rectangle.__init__(self, **kwargs)
        self.set_width(
            self.aspect_ratio * self.get_height(),
            stretch=True
        )

"""
self.add(FullScreenRectangle())
        rects = Rectangle(3.5, 4.5).replicate(3)
        rects.set_stroke(WHITE, 2)
        rects.set_fill(BLACK, 1)
        rects.arrange(RIGHT, buff=0.75)
        rects.to_edge(DOWN, buff=0.25)


"""
class FullScreenRectangle(ScreenRectangle):
    CONFIG = {
        "height": FRAME_HEIGHT,
        "fill_color": GREY_E,
        "fill_opacity": 1,
        "stroke_width": 0,
    }


class FullScreenFadeRectangle(FullScreenRectangle):
    CONFIG = {
        "stroke_width": 0,
        "fill_color": BLACK,
        "fill_opacity": 0.7,
    }


class PictureInPictureFrame(Rectangle):
    CONFIG = {
        "height": 3,
        "aspect_ratio": 16.0 / 9.0
    }

    def __init__(self, **kwargs):
        digest_config(self, kwargs)
        Rectangle.__init__(
            self,
            width=self.aspect_ratio * self.height,
            height=self.height,
            **kwargs
        )
