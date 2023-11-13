from manimlib import *

class test(Scene):
    def construct(self):
        # Create a triangle (clockwise arranged points)
        triangle = RegularPolygon(3).scale(2)
        # Create a square (counterclockwise arranged points)
        square = Square().scale(2).flip()

        # Animate
        self.play(ShowCreation(triangle))
        self.wait(1)
        self.play(Transform(triangle, square))
        self.wait(1)
