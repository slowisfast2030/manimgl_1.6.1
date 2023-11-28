from manimlib import *

class test(Scene):
    def construct(self):
        # Create a square
        square = Square()

        # Shallow copy of the square
        shallow_copy_square = square.copy()

        # Deep copy of the square
        deep_copy_square = square.deepcopy()

        # Positioning the squares
        shallow_copy_square.to_edge(LEFT)
        deep_copy_square.to_edge(RIGHT)

        # Animate
        self.play(ShowCreation(square))
        self.play(ShowCreation(shallow_copy_square))
        self.play(ShowCreation(deep_copy_square))

        # Change color of the original square
        self.play(square.set_color, YELLOW)

        # Notice how the shallow copy changes color, but the deep copy does not
        self.wait(2)
