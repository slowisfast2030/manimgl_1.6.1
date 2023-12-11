from manim import *

# 下面这几行设置竖屏
config.frame_width = 9
config.frame_height = 16

config.pixel_width = 1080
config.pixel_height = 1920

class test(Scene):
    def construct(self):
        number_plane = NumberPlane(
            background_line_style={
                "stroke_color": TEAL,
                "stroke_width": 4,
                "stroke_opacity": 0.6
            }
        )
        self.play(Write(number_plane))
        self.wait()

class NumberPlaneScaled(Scene):
    def construct(self):
        number_plane = NumberPlane(
            x_range=(-4, 11, 1),
            y_range=(-3, 3, 1),
            x_length=5,
            y_length=2,
        ).move_to(LEFT*3)

        number_plane_scaled_y = NumberPlane(
            x_range=(-4, 11, 1),
            x_length=5,
            y_length=4,
        ).move_to(RIGHT*3)

        self.add(number_plane)
        self.add(number_plane_scaled_y)


class NumberPlaneExample(Scene):
    def construct(self):
        plane = NumberPlane(
            x_range=[-10, 10, 1],
            y_range=[-10, 10, 1],
            axis_config={"color": WHITE},
            x_axis_config={
                "numbers_to_include": range(-10, 11, 2),
                "numbers_with_elongated_ticks": range(-10, 11, 2),
            },
            y_axis_config={
                "numbers_to_include": range(-10, 11, 2),
                "numbers_with_elongated_ticks": range(-10, 11, 2),
            },
        )
        #self.add(plane)
        self.play(Write(plane))
        self.wait()
