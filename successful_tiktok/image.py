from manimlib import *

class test(Scene):
    def construct(self):
        image_path = ImageMobject("dall-path.png").scale(2).shift(IN*4)
        image_house = ImageMobject("dall-house.png").scale(2)
        image_boy = ImageMobject("dall-boy.png").scale(2).shift(OUT*4)

        self.add(image_path, image_house, image_boy)

        frame = self.camera.frame
        def update_frame(frame, dt):
            frame.increment_theta(-0.1 * dt)

        self.play(frame.animate.reorient(30, 70), run_time=2)
        frame.add_updater(update_frame)
        self.wait(5)

