import sys
sys.path.append('/Users/linus/Desktop/slow-is-fast/manimgl_1.6.1/3b1b-videos-master')

from manim_imports_ext import *

class test(Scene):
    CONFIG = {
        "camera_class": ThreeDCamera,
    }

    def construct(self):
        frame = self.camera.frame
        frame.reorient(20, 70) 

        def update_frame(frame, dt):
            frame.increment_theta(-0.5 * dt)    
        frame.add_updater(update_frame)

        colors = color_gradient([BLUE, GREEN], 2)
        pis = [PiCreature(color=color).scale(0.8).fix_in_frame() for color in colors]
        pis[1].set_color(GREY_BROWN).scale(1.3).shift(UP*1.2)
        pi_group = VGroup(*pis)
        pi_group.arrange(RIGHT, buff=0.9).shift(DOWN*2).stretch(0.33 ,1).scale(1.5)
        self.play(FadeIn(pi_group))
        #self.play(pis[1].says("today, we will \nleran abandon!"))
        #self.play(pis[1].debubble())
        #self.wait()

        sphere1 = Sphere(radius=3)
        sphere2 = Sphere(radius=3)
        sphere3 = Sphere(radius=3)
        # You can texture a surface with up to two images, which will
        # be interpreted as the side towards the light, and away from
        # the light.  These can be either urls, or paths to a local file
        # in whatever you've set as the image directory in
        # the custom_config.yml file

        # day_texture = "EarthTextureMap"
        # night_texture = "NightEarthTextureMap"
        texture1 = "dall-boy.png"
        #texture = "../successful_product/EarthTextureMap.jpeg"
        mob1 = TexturedSurface(sphere1, texture1).scale(0.3)

        texture2 = "dall-house.png"
        #texture = "../successful_product/EarthTextureMap.jpeg"
        mob2 = TexturedSurface(sphere2, texture2).scale(0.3)

        texture3 = "dall-path.png"
        #texture = "../successful_product/EarthTextureMap.jpeg"
        mob3 = TexturedSurface(sphere3, texture3).scale(0.3)

        #gr = Group(mob1, mob2, mob3).arrange(RIGHT, buff=1).shift(OUT*2)
        gr = Group(mob1, mob2, mob3).shift(OUT*4)
        mob1.move_to([3, 0, 0])
        mob2.move_to([-1, 2, 0])
        mob3.move_to([-1, -2, 0])

        self.add(gr)

        self.play(Rotate(gr[1], PI/2, axis=RIGHT), 
                  Rotate(gr[2], PI/2),
                  Rotate(gr[0], PI/2, axis=UP),
                   run_time= 4)
        
        # frame.remove_updater(update_frame)
        # frame.reorient(90, 0)
        # gr.move_to(ORIGIN+UP*6+RIGHT*2)
        self.wait(2)



            