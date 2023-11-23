from manimlib import *

class test(Scene):
    def construct(self):
        frame = self.camera.frame
        frame.reorient(0, 70)
        def update_frame(frame, dt):
            frame.increment_theta(-0.1 * dt)
        #frame.add_updater(update_frame)

        image_path = ImageMobject("dall-house.png").scale(0.4).set_opacity(1)
        image_path_cube = self.image_to_cube(image_path).space_out_submobjects(1)

        image_boy = ImageMobject("dall-boy.png").scale(0.4).set_opacity(1)
        image_boy_cube = self.image_to_cube(image_boy).space_out_submobjects(1)

        image_house = ImageMobject("dall-path.png").scale(0.4).set_opacity(1)
        image_house_cube = self.image_to_cube(image_house).space_out_submobjects(1)

        gr = Group(image_path_cube, image_boy_cube, image_house_cube).arrange(RIGHT, buff=1)
        #gr = gr.rotate(PI/2, OUT)
        self.add(gr)

        gr.scale(0.4).shift(OUT*6.5+RIGHT*2.5)
        gr[:2].set_opacity(0.2)


    def image_to_cube(self, image):
        
        radius = image.get_height() / 2
        square = Square(side_length=2*radius)

        image.move_to(radius * OUT)
        result = [image]
        #result.append(image.copy().rotate(PI/2, -RIGHT, about_point=ORIGIN))
        #result.append(image.copy().rotate(PI/2, -UP, about_point=ORIGIN))
        result.append(image.copy().rotate(PI/2, RIGHT, about_point=ORIGIN))
        result.append(image.copy().rotate(PI/2, UP, about_point=ORIGIN))
        #result.append(image.copy().rotate(PI, RIGHT, about_point=ORIGIN))
       
        return Group(*result)
    