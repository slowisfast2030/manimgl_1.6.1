from manimlib import *

class SimpleAnimationScene(Scene):
    def construct(self):
        # Create a circle and set its color
        circle = Circle()
        circle.set_fill(BLUE, opacity=0.5)

        # Create a line
        line = Line(ORIGIN, 2*RIGHT)
        line.set_color(RED)

        # Rotate the line around its center
        rotate_line = Rotate(circle, angle=PI, about_edge=RIGHT)

        # Animate
        self.play(
            Animation(line),   # Keep the line in the animation
            rotate_line,
            run_time=2
        )
        
        # Keep the scene still for a short duration after animation
        self.wait(1)
