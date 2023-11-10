from manimlib import *

class test(Scene):
    def construct(self):
        arrow = Arrow(LEFT, RIGHT)
        self.add(arrow)

        elbow = Elbow().shift(UP)
        self.add(elbow)

        vector = Vector().shift(DOWN)
        self.add(vector)