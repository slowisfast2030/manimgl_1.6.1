from manimlib import *

class test(Scene):
    def construct(self):
        
        frame = self.camera.frame
        frame.scale(2)

        # Create axes
        axes = Axes(
            x_range=[0, 3],
            y_range=[0, 6],
            height = 8,
            width=4,
            axis_config={"color": WHITE},
        )

        # Create the function
        def func(x):
            return 2 * PI * x

        # Create the graph
        graph = axes.get_graph(func, 
                               x_range=[0, 1],
                               color=BLUE)

        # Generate rectangles for Riemann sum/integral approximation
        rects = axes.get_riemann_rectangles(
            graph,
            x_range=[0, 1.1],
            dx=0.1,
            fill_opacity=0.5,
            stroke_width=0.1,
        )

        # Add labels
        two_pi_r_label = Tex(r"2\pi r").next_to(graph, UP+RIGHT).set_color(BLUE)
        dr_label = Tex(r"dr").set_color(RED).next_to(rects[3], DOWN)

        # Add the elements to the scene
        self.add(axes, graph, rects)
        self.add(two_pi_r_label, dr_label)
