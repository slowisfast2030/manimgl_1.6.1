from manimlib import *

class PixelsAsSquares(VGroup):
    CONFIG = {
        "height" : 2,
    }
    def __init__(self, image_mobject, **kwargs):
        VGroup.__init__(self, **kwargs)
        i=0
        for row in image_mobject.pixel_array:
            print(i)
            i+=1
            for rgba in row:
                square = Square(
                    stroke_width = 0, 
                    fill_opacity = rgba[3]/255.0,
                    fill_color = rgba_to_color(rgba/255.0),
                )
                self.add(square)
        self.arrange_in_grid(
            *image_mobject.pixel_array.shape[:2],
            buff = 0
        )
        self.replace(image_mobject)

class test(Scene):
    def construct(self):
        # Load the full image
        image_path = "dall-seagull-32x32.png"
        image_mob = ImageMobject(image_path).scale(2)
        # print(image_mob.image)
        # print(image_mob.path)
        # print(image_mob.texture_paths)

        image_mob.image_rgba = image_mob.image.convert("RGBA")
        image_mob.pixel_array = np.array(image_mob.image_rgba)
        print(image_mob.pixel_array.shape)

        ps = PixelsAsSquares(image_mob).space_out_submobjects(1.1)
        self.add(ps)

