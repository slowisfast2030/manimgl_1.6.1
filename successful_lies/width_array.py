from manimlib import *

class test(Scene):
    def construct(self):
        # Create a circle
        circle = Circle()

        # Set the stroke width as an array
        # For instance, it alternates between 2 and 4
        stroke_widths = [2, 6]

        # Apply the stroke widths to the circle
        circle.set_stroke(WHITE, width=stroke_widths)

        # Add the circle to the scene
        self.play(ShowCreation(circle))

        # Keep the scene displayed
        self.wait(2)
