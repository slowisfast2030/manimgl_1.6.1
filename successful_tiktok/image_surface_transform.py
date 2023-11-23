import sys
sys.path.append('/Users/linus/Desktop/slow-is-fast/manimgl_1.6.1/3b1b-videos-master')

from manim_imports_ext import *

class test(Scene):
    CONFIG = {
        "camera_class": ThreeDCamera,
    }

    def construct(self):
        frame = self.camera.frame
        frame.reorient(0, 70) 

        def update_frame(frame, dt):
            frame.increment_theta(-0.5 * dt)    
        frame.add_updater(update_frame)


        sphere1 = Sphere(radius=3)
        sphere2 = Square3D(radius=3, resolution=sphere1.resolution)
       

        # day_texture = "EarthTextureMap"
        # night_texture = "NightEarthTextureMap"
        texture1 = "dall-boy.png"
        #texture = "../successful_product/EarthTextureMap.jpeg"
        mob1 = TexturedSurface(sphere1, texture1).scale(0.3)

        texture2 = "dall-house.png"
        #texture = "../successful_product/EarthTextureMap.jpeg"
        mob2 = TexturedSurface(sphere2, texture2).scale(3)

        #gr = Group(mob1, mob2).arrange(RIGHT, buff=1).shift(OUT*2)

        self.add(mob1)
        
      
        self.wait(2)

        self.play(Transform(mob1, mob2), run_time=2)



            