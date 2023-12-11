from manim import *

"""
开场
"""
# 下面这几行设置竖屏
config.frame_width = 9
config.frame_height = 16

config.pixel_width = 1080
config.pixel_height = 1920

# 一个很聪明的方案
class ShowCreation(Create):
    pass

class s0(Scene):
    def setup(self):
        self.coord_c = [-4,0,0]
        self.coord_a = [0,0,0]
        self.coord_b = [0,3,0]
        self.coord_d = [0, 4/3, 0]
        self.coord_e = [-4/5, 12/5, 0]
        self.coord_f = [1, 0, 0]

        self.line_color = MAROON_B
        self.label_color = WHITE

        self.radius = 2
        self.stroke_color = WHITE
        self.radial_line_color = MAROON_B

        self.shift_vector = np.array([-2, 1.5, 0]) - 4*UP
        self.coord_c_shift = np.array(self.coord_c) - self.shift_vector
        self.coord_a_shift = np.array(self.coord_a) - self.shift_vector
        self.coord_b_shift = np.array(self.coord_b) - self.shift_vector

        self.text_scale = 0.9
        pass

    def construct(self):
        self.opening()  
        self.introduce_three_methods()
        pass


    
    # 在屏幕上方出现一个简单的三角形，下方位置留给pi生物
    # 在三角形下方显示tan(alpha) = 3/4，求解tan(alpha/2)
    def opening(self):
        triangle = Polygon(self.coord_c_shift, 
                           self.coord_a_shift, 
                           self.coord_b_shift, 
                           color=self.line_color, stroke_width=3).set_z_index(1)
        point_c = Dot(self.coord_c_shift)
        point_a = Dot(self.coord_a_shift)
        point_b = Dot(self.coord_b_shift)

        ver_c = MathTex("C", color=self.label_color).next_to(self.coord_c_shift, DOWN).set_z_index(1)
        ver_a = MathTex("A", color=self.label_color).next_to(self.coord_a_shift, DOWN).set_z_index(1)
        ver_b = MathTex("B", color=self.label_color).next_to(self.coord_b_shift, RIGHT).set_z_index(1)
        ver_ani = list(map(FadeIn, [ver_c, ver_a, ver_b]))

        self.play(*ver_ani, 
                  ShowCreation(triangle),
                  run_time=1)
        self.wait()
        
        line_ca = Line(self.coord_c_shift, self.coord_a_shift)
        line_cd = Line(self.coord_c_shift, self.coord_b_shift)
        angle = Angle(line_ca, line_cd, radius=0.6, other_angle=False)
        label_angle = MathTex(r"\alpha").next_to(angle, RIGHT).scale(0.8).shift(0.05*UP)

        self.play(Write(angle), Write(label_angle), run_time=1)
        self.wait()

        text = Tex("It is already to know that $tan(\\alpha) = \\frac{3}{4}$, \\\\ then what is value of $tan(\\frac{\\alpha}{2})$?").scale(self.text_scale).next_to(triangle, DOWN, 1)
        self.play(Write(text), run_time=1)
        self.wait()

        tri_gr = VGroup(triangle, ver_c, ver_a, ver_b, point_a, point_b, point_c)

        tri_gr_up = tri_gr.copy()
        tri_gr_mid = tri_gr.copy()
        tri_gr_down = tri_gr.copy()
        all_gr = VGroup(tri_gr_up, tri_gr_mid, tri_gr_down).arrange(DOWN, buff=2).scale(0.8)

        self.play(FadeOut(angle),
                  FadeOut(label_angle),
                  FadeOut(text))
        self.play(FadeOut(tri_gr),
                  TransformFromCopy(tri_gr, tri_gr_up),
                  TransformFromCopy(tri_gr, tri_gr_mid),
                  TransformFromCopy(tri_gr, tri_gr_down))
        self.wait()
        self.all_gr = all_gr    

        pass

    # 屏幕从上至下出现3种解法
    """
    有一个很炫的转场
    开场中间出现了一个三角形
    然后这个三角形被分成了三个部分：上中下
    然后在上中下三个三角形的基础上分别显示三种解法

    非常丝滑
    """
    def introduce_three_methods(self):
        
        method_1 = self.introduce_first_method()
        method_2 = self.introduce_second_method()
        method_3 = self.introduce_third_method()

        # 为每一个方法添加文字说明
        # text_1 = Text("法一").scale(self.text_scale).next_to(self.all_gr[0], LEFT, 0.5)
        # text_2 = Text("法二").scale(self.text_scale).next_to(self.all_gr[1], LEFT, 0.5)
        # text_3 = Text("法三").scale(self.text_scale).next_to(self.all_gr[2], LEFT, 0.5)

        self.play(ShowCreation(method_1),
                  ShowCreation(method_2),
                  ShowCreation(method_3),
                    # Write(text_1),
                    # Write(text_2),
                    # Write(text_3),
                  run_time=2)
        self.wait()
        
        rec_up = Rectangle(height=self.all_gr[0].get_height()+0.5, width=config.frame_width, color=BLACK, fill_opacity=0.6).move_to(self.all_gr[0]).set_z_index(2)
        rec_mid = Rectangle(height=self.all_gr[1].get_height()+1.4, width=config.frame_width, color=BLACK, fill_opacity=0.6).move_to(self.all_gr[1]).set_z_index(2)
        rec_down = Rectangle(height=self.all_gr[2].get_height()+2, width=config.frame_width, color=BLACK, fill_opacity=0.6).move_to(self.all_gr[2]).set_z_index(2)

        # 可视化1的长度
        # line = Line(ORIGIN, RIGHT).to_edge()
        # self.add(line)

        self.play(FadeIn(rec_mid), FadeIn(rec_down), run_time=1)
        self.wait(2)
        self.play(FadeIn(rec_up), FadeOut(rec_mid), run_time=1)
        self.wait(2)
        self.play(FadeIn(rec_mid), FadeOut(rec_down),run_time=1)
        self.wait(2)

    # 第一种解法
    def introduce_first_method(self):
        tri_gr_up = self.all_gr[0]
        point_a = tri_gr_up[4]
        point_b = tri_gr_up[5]
        point_c = tri_gr_up[6]
        # 根据比例计算出点D的坐标
        point_d = Dot(5/9*point_a.get_center() + 4/9*point_b.get_center())

        half_line = Line(point_c.get_center(), point_d.get_center(), color=self.line_color)

        ver_d = MathTex("D", color=self.label_color).next_to(point_d, RIGHT)

        line_ca = Line(point_c.get_center(), point_a.get_center())
        line_cd = Line(point_c.get_center(), point_d.get_center())
        angle_half = Angle(line_ca, line_cd, radius=0.6, other_angle=False)
        label_angle_half = MathTex(r"\frac{\alpha}{2}").next_to(angle_half, RIGHT).scale(0.8).shift(0.05*UP)
        
        result = VGroup(half_line, 
                        ver_d,
                        angle_half, 
                        label_angle_half)
        return result
        
    # 第二种解法
    def introduce_second_method(self):
        tri_gr_mid = self.all_gr[1]
        point_a = tri_gr_mid[4]
        point_b = tri_gr_mid[5]
        point_c = tri_gr_mid[6]

        # 圆心是c和b的中点
        origin = Dot((point_c.get_center() + point_b.get_center())/2)
        origin_lable = MathTex("O").next_to(origin, UP)

        circle = Circle(
            radius = self.radius,
            stroke_color = self.stroke_color
        ).move_to(origin)


        result = VGroup(origin, 
                        origin_lable, 
                        circle)
        return result

    # 第三种解法    
    def introduce_third_method(self):
        
        tri_gr_down = self.all_gr[2]
        point_a = tri_gr_down[4]
        point_b = tri_gr_down[5]
        point_c = tri_gr_down[6]

        plane = NumberPlane().move_to(tri_gr_down.get_center()).scale(0.6)
        

        result = VGroup(plane)
        return result

    