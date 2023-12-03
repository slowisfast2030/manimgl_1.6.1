from manimlib import *

class test(Scene):
    def construct(self):
        annular_sector = AnnularSector(inner_radius=1, outer_radius=2, start_angle=0, angle=TAU/4, color=BLUE, stroke_width=1) 
        self.add(annular_sector)

        for i, point in enumerate(annular_sector.get_points()):
            dot = Dot(point).scale(0.5).set_fill(RED, 1)
            
            if i % 3 == 0:
                print(i)
                dot.set_fill(YELLOW, 1)
                label = Text(str(i)).next_to(dot, UP).scale(0.3)
            
            self.add(dot, label)

