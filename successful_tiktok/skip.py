from manimlib import *

class SkipAnimationDemo(Scene):
    def construct(self):
        # Create a square
        square = Square()

        # Force skipping the animation of the square's creation
        self.force_skipping()
        self.play(ShowCreation(square))
        self.revert_to_original_skipping_status()

        # Transform the square into a circle
        circle = Circle()
        self.play(Transform(square, circle))

        # Display the scene
        self.wait(2)
