from manimlib import *

class test(Scene):
    def construct(self):
        # Create a VGroup with a square and a circle
        group = VGroup(Square(), Circle()).arrange(RIGHT)

        # Shallow copy of the group
        shallow_copy_group = group.copy()

        # Deep copy of the group
        deep_copy_group = group.deepcopy()

        # Positioning the groups
        group.to_edge(UP)
        shallow_copy_group.to_edge(LEFT)
        deep_copy_group.to_edge(RIGHT)

        # Animate
        self.play(ShowCreation(group), ShowCreation(shallow_copy_group), ShowCreation(deep_copy_group))

        # Change color of the circle in the original group
        self.play(group[1].set_color, YELLOW)

        # Notice how the shallow copy's circle changes color, but the deep copy's circle does not
        self.wait(2)
