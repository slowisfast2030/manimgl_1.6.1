from manimlib import *

class test(Scene):
    def construct(self):
        # Parameters
        circle_radius = 2
        ring_width = 0.3
        num_rings = int(circle_radius / ring_width)

        # Create Circle
        circle = Circle(radius=circle_radius).shift(LEFT*3)
        self.play(ShowCreation(circle))
        self.wait(1)

        # Transform Circle into Rings
        rings = VGroup()
        for i in range(num_rings):
            rings.add(Annulus(inner_radius=i*ring_width,
                              outer_radius=(i+1)*ring_width,
                              color=BLUE))
        
        self.play(Transform(circle, rings), run_time=2)
        
