from manimlib import *

class test(Scene):
    def construct(self):
        image_path = ImageMobject("dall-path.png").scale(2).shift(IN*4)
        image_path_blocker = SurroundingRectangle(image_path)
        image_path_blocker.set_fill(BLACK, 1)
        image_path_blocker.set_stroke(width=0)
        
        self.add(image_path, image_path_blocker)

        self.play(ApplyMethod(
                image_path_blocker.stretch, 0, 1, {"about_edge": DOWN},
                run_time=3,
                rate_func=bezier([0, 0, 1, 1]),
            ))