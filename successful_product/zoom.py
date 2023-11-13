from manimlib import *

class test(Scene):
    def construct(self):
        # Create some objects
        square = Square().shift(LEFT*3)
        circle = Circle()

        # Add objects to the scene
        self.add(square, circle)

        # Move the camera to focus on the square
        self.play(self.camera.frame.animate.move_to(square))

        # Zoom in on the circle
        self.play(self.camera.frame.animate.scale(0.5).move_to(circle))
