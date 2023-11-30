from manimlib import *

class test(Scene):
    def construct(self):
        # Create a square
        square = Square()

        # Apply a wave animation to the square
        self.play(ApplyWave(square, amplitude=0.5, direction=UP))

        # Keep the scene displayed
        self.wait(2)
