from manimlib import *

"""
这段代码绝对的传奇：
在稿纸上画出草图，通过gpt4的识图功能，生成manim代码

x轴和f(x)之间有一些直线
当f(x)变成g(x)的时候，这些直线的高度也会变化

实现f(x)到g(x)的变化很简单
在此过程中，直线高度的变化给人直观上是因果关系
但是实现的时候，因果关系很难实现
所以，可以转向并行实现
一旦转向并行实现，就需要控制每一帧的直线的高度
这个时候，就需要使用UpdateFromAlphaFunc类
"""
class test(Scene):
    def construct(self):
        # Define axes
        axes = Axes(
            x_min=-3, x_max=3, 
            y_min=-1, y_max=9, 
            axis_config={"color": BLUE}
        )

        # Define functions
        def f(x):
            return x**2

        def g(x):
            return -1* x**2 + 1

        # Create curves for f(x) and g(x)
        graph_f = axes.get_graph(f, color=BLUE)
        graph_g = axes.get_graph(g, color=GREEN)

        # Create labels for f(x) and g(x)
        graph_label_f = axes.get_graph_label(graph_f, label='f(x)')
        graph_label_g = axes.get_graph_label(graph_g, label='g(x)')

        # Create vertical lines to the x-axis
        lines = VGroup(*[
            Line(
                start=axes.c2p(x, 0), 
                end=axes.c2p(x, f(x)), 
                color=RED
            ) for x in np.arange(-3, 3, 0.5)
        ])

        # Update function for the lines
        def update_lines(group, alpha):
            for line, x in zip(group, np.arange(-3, 3, 0.5)):
                y = interpolate(f(x), g(x), alpha)
                new_end = axes.c2p(x, y)
                line.put_start_and_end_on(line.get_start(), new_end)

        # Draw axes and initial plot with lines
        self.add(axes, graph_f, graph_label_f, lines)

        # Transform f(x) to g(x) and update lines
        self.play(
            Transform(graph_f, graph_g),
            Transform(graph_label_f, graph_label_g),
            UpdateFromAlphaFunc(lines, update_lines),
            run_time=4
        )
        self.wait()

# To run the scene, use the following command in your terminal:
# manimgl line_length.py test -ol
