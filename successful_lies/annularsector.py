from manimlib import *

class test(Scene):
    def construct(self):
        annular_sector = AnnularSector(inner_radius=1, outer_radius=2, angle=TAU/4) 
        self.add(annular_sector)

        for i, point in enumerate(annular_sector.get_points()):
            dot = Dot(point).scale(0.5).set_color(RED)
            label = Tex(str(i)).next_to(dot, UP)
            
            self.add(dot, label)

