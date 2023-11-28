from manimlib import *

class test(Scene):
    def construct(self):
        # Create a group of circles
        circle_group = VGroup(*[Circle(radius=0.5, color=WHITE) for _ in range(3)])
        circle_group.arrange(RIGHT, buff=1)
        circle_group.test_list = [1,2,3]

        # Position the original group on the screen
        circle_group.to_edge(UP)

        # Create a shallow copy and a deep copy of the group
        shallow_copy = circle_group.copy()
        deep_copy = circle_group.deepcopy()

        # Position the copies
        shallow_copy.center()
        deep_copy.to_edge(DOWN)
        
        circle_group[0].set_color(RED)
        circle_group.test_list[0] = 'one'

        self.add(circle_group, shallow_copy, deep_copy)
        print("circle_group.test_list", circle_group.test_list)
        print("shallow_copy.test_list", shallow_copy.test_list)
        print("deep_copy.test_list", deep_copy.test_list)

        # Display all the objects
        self.wait()
