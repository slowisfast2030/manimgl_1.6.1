from manim import *

config.frame_width = 9
config.frame_height = 16

config.pixel_width = 1080
config.pixel_height = 1920

class CircleAnimation(Scene):
    def construct(self):
        # 创建一个圆
        circle = Circle(radius=2)
        self.add(circle)

        # 创建一个圆周上的点
        circle_point = Dot(point=circle.point_at_angle(0), color=RED)
        self.add(circle_point)

        # 创建两条线段，从圆周上的点指向圆的直径的两端
        line_1 = Line(circle_point.get_center(), circle.get_left(), color=BLUE)
        line_2 = Line(circle_point.get_center(), circle.get_right(), color=GREEN)
        move_lines = VGroup(line_1, line_2)
        self.add(move_lines)

        # 定义一个更新器函数
        def circle_gr_updater(mob):
            new_line_1 = Line(circle_point.get_center(), circle.get_left(), color=BLUE)
            new_line_2 = Line(circle_point.get_center(), circle.get_right(), color=GREEN)
            line_1.become(new_line_1)
            line_2.become(new_line_2)
            print("----->")


        # 添加更新器到move_lines
        move_lines.add_updater(circle_gr_updater)

        # 播放动画：点沿圆周运动
        self.play(Rotate(circle_point, PI, about_point=circle.get_center(), rate_func=linear), run_time=4)

        # 移除更新器
        move_lines.remove_updater(circle_gr_updater)
