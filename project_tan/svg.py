from manim import *

# 下面这几行设置竖屏
config.frame_width = 9
config.frame_height = 16

config.pixel_width = 1080
config.pixel_height = 1920


class svg(Scene):
    def construct(self):
        # 综合几何
        svg_compass = SVGMobject("compass.svg").set_fill(GREEN_B, 0.7)
        svg_ruler = SVGMobject("ruler.svg").set_fill(TEAL, 0.5).match_height(svg_compass)
        svg_gr = VGroup(svg_ruler, svg_compass).arrange(RIGHT, buff=0.5).scale(1.5)

        # 解析几何
        plane = NumberPlane().scale(0.5)

        # 整体
        geo_gr = VGroup(svg_gr, plane).arrange(DOWN, buff=3)

        # Display the image
        self.play(Write(svg_gr[0]),
                Write(svg_gr[1]),
                Write(plane),
                run_time = 2)
        self.wait(2)  # Wait for 2 seconds


