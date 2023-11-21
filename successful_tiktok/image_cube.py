from manimlib import *


class test(Scene):
    def construct(self):
        image_path = ImageMobject("dall-path.png").scale(1.5)
        image_house = ImageMobject("dall-house.png").scale(1.5)
        image_boy = ImageMobject("dall-boy.png").rotate(PI/2).scale(1.5)

        # image_path_copy = image_path.copy().move_to(UP*4).set_width(FRAME_WIDTH)
        # image_house_copy = image_house.copy()
        # image_boy_copy = image_boy.copy().move_to(DOWN*4).rotate(-PI/2) 
        # self.add(image_path_copy, image_boy_copy)

        radius = image_path.get_height()/2
        image_path.move_to(radius * OUT)
        image_house.move_to(radius * OUT)
        image_boy.move_to(radius * OUT)

        result = [image_path]
        
        result.append(image_house.copy().rotate(PI/2, RIGHT, about_point=ORIGIN))
        result.append(image_boy.copy().rotate(PI/2, UP, about_point=ORIGIN))

        result = Group(*result).space_out_submobjects(1.2)
        self.add(*result)   

        frame = self.camera.frame
        def update_frame(frame, dt):
            frame.increment_theta(-0.1 * dt)

        self.play(frame.animate.reorient(60, 70), run_time=2)
        frame.add_updater(update_frame)

        self.wait(5)

