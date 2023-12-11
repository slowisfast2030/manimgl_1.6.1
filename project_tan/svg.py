import sys
sys.path.append('/Users/linus/Desktop/slow-is-fast/manimgl_1.6.1/3b1b-videos-master')

from manim_imports_ext import *

"""
开场
"""
# manimgl中没有config这个对象，代码中使用了config.frame_width
# 这里为了兼容，引入了config
class C:
    pass

config = C()
config.frame_width = 9
config.frame_height = 16


class svg(Scene):
    def construct(self):
        # 综合几何
        
        svg_compass = SVGMobject("c1.svg").set_fill(GREEN_B, 0.7)
        

        svg_ruler = SVGMobject("ruler.svg").set_fill(TEAL, 0.5).match_height(svg_compass)
        svg_gr = VGroup(svg_ruler, svg_compass).arrange(RIGHT, buff=0.5).scale(1.5)

        # 解析几何
        plane = NumberPlane().scale(0.5)

        # 整体
        geo_gr = VGroup(svg_gr, plane).arrange(DOWN, buff=3)

        # Display the image
        self.play(
            #FadeIn(dot),
            Write(svg_gr[0]),
                Write(svg_gr[1]),
                Write(plane),
                run_time = 2)
        self.wait(2)  # Wait for 2 seconds


