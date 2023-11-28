from manimlib import *

class RotationDemo(Scene):
    def construct(self):
        # Create a square
        square = Square()

        # Add the square to the scene
        self.add(square)

        # Rotate the square 90 degrees (PI/2 radians) about its center
        rotation_animation = Rotate(
                                mobject=square, 
                                angle=PI/2,
                                axis=OUT,
                                #about_point=ORIGIN+RIGHT+UP
                                about_edge = RIGHT+UP
                                )

        dot = Dot(ORIGIN+RIGHT+UP)
        self.add(dot)
        # Play the animation
        self.play(rotation_animation)

        # Keep the scene displayed after animation
        self.wait()
