from manimlib import *  # or from manimlib import * for ManimGL


class ExampleScene(Scene):
    def construct(self):
        # Create two mobjects
        circle = Circle(color=BLUE)
        square = Square(color=RED).shift(RIGHT*1.9)
        self.add(circle, square)

        circle.add_updater(lambda m: m.shift(0.1* LEFT))

        # Animate the square to maintain its position relative to the circle
        self.play(MaintainPositionRelativeTo(square, circle), run_time=3)
        #self.wait(3)

