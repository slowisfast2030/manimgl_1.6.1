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


def student_with_teacher():
    colors = [BLUE_E, GREY_BROWN]
    student_teacher = [PiCreature(color=color) for color in colors]
    student_teacher = VGroup(*student_teacher)
    student_teacher.arrange(RIGHT, buff=0.9).shift(DOWN*5.5).scale(0.8)

    _, teacher = student_teacher
    teacher.scale(1.3)

    return student_teacher


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
        #self.introduce_three_methods()
        pass

    # 需要注意p1是角所在的位置
    # 这个方法是为了计算p1p2和p1p3之间的夹角
    def angle_of_points(self, p1, p2, p3):
            v1 = np.array(p2) - np.array(p1)
            v2 = np.array(p3) - np.array(p1)
            angle = np.arccos(np.dot(v1, v2)/(np.linalg.norm(v1)*np.linalg.norm(v2)))
            return angle

    # 在屏幕上方出现一个简单的三角形，下方位置留给pi生物
    # 在三角形下方显示tan(alpha) = 3/4，求解tan(alpha/2)
    def opening(self):
        # 画出学生和老师
        student_teacher = student_with_teacher()
        #self.play(FadeIn(student_teacher))
        #self.play(student_teacher[1].says("today, we will \nlearn abandon!"))
        #self.wait(1) 

        triangle = Polygon(self.coord_c_shift, 
                           self.coord_a_shift, 
                           self.coord_b_shift, 
                           color=self.line_color, stroke_width=3)
        point_c = Dot(self.coord_c_shift)
        point_a = Dot(self.coord_a_shift)
        point_b = Dot(self.coord_b_shift)

        ver_c = Tex("C", color=self.label_color).next_to(self.coord_c_shift, DOWN)
        ver_a = Tex("A", color=self.label_color).next_to(self.coord_a_shift, DOWN)
        ver_b = Tex("B", color=self.label_color).next_to(self.coord_b_shift, RIGHT)
        ver_ani = list(map(FadeIn, [ver_c, ver_a, ver_b]))

        self.play(*ver_ani, 
                  ShowCreation(triangle),
                  FadeIn(student_teacher),
                  run_time=1)
        
        # 不起作用
        #self.play(student_teacher[0].animate.blink())
        
        line_ca = Line(self.coord_c_shift, self.coord_a_shift)
        line_cd = Line(self.coord_c_shift, self.coord_b_shift)
        #angle = Angle(line_ca, line_cd, radius=0.6, other_angle=False)
        """
        gl中angle的实现有不同
        """
        angle_ca_cb = self.angle_of_points(self.coord_c_shift, 
                                           self.coord_a_shift, 
                                           self.coord_b_shift)
        angle = Arc(start_angle=Line(self.coord_c_shift, self.coord_b_shift).get_angle(), angle=-angle_ca_cb, radius=0.6, color=WHITE)
        angle.shift(self.coord_c_shift)

        label_angle = Tex(r"\alpha").next_to(angle, RIGHT, 0.1).scale(0.8).shift(0.05*UP)

        self.play(Write(angle), 
                  Write(label_angle), 
                    student_teacher[0].animate.change_mode("happy"),
                    student_teacher[1].animate.change_mode("happy"),
                  run_time=1)
        self.wait()

        text = TexText("It is already to know that $tan(\\alpha) = \\frac{3}{4}$, \\\\ then what is value of $tan(\\frac{\\alpha}{2})$?").scale(self.text_scale).next_to(triangle, DOWN, 1)
        self.play(Write(text), run_time=1)
        self.wait()

        tri_gr = VGroup(triangle, ver_c, ver_a, ver_b, point_a, point_b, point_c)

        tri_gr_up = tri_gr.copy()
        tri_gr_mid = tri_gr.copy()
        tri_gr_down = tri_gr.copy()
        all_gr = VGroup(tri_gr_up, tri_gr_mid, tri_gr_down).arrange(DOWN, buff=2).scale(0.8)

        pi_text = Text("已知全角的正切值，\n如何求解半角的正切值呢？").scale(0.7)
        self.play(FadeOut(angle),
                  FadeOut(label_angle),
                  FadeOut(text),
                  student_teacher[1].says(pi_text),
                  )
        self.play(student_teacher[0].animate.change_mode("confused"))
        self.wait()
        self.play(FadeOut(tri_gr),
                  student_teacher[1].debubble(),
                  FadeOut(student_teacher[0]),
                  FadeOut(student_teacher[1]),
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
        
        rec_up = Rectangle(height=self.all_gr[0].get_height()+0.5, width=config.frame_width, color=BLACK, fill_opacity=0.6).move_to(self.all_gr[0])
        rec_mid = Rectangle(height=self.all_gr[1].get_height()+1.4, width=config.frame_width, color=BLACK, fill_opacity=0.6).move_to(self.all_gr[1])
        rec_down = Rectangle(height=self.all_gr[2].get_height()+2, width=config.frame_width, color=BLACK, fill_opacity=0.6).move_to(self.all_gr[2])

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

        ver_d = Tex("D", color=self.label_color).next_to(point_d, RIGHT)

        line_ca = Line(point_c.get_center(), point_a.get_center())
        line_cd = Line(point_c.get_center(), point_d.get_center())
        #angle_half = Angle(line_ca, line_cd, radius=0.6, other_angle=False)
        angle_ca_cd = self.angle_of_points(point_c.get_center(), 
                                           point_a.get_center(), 
                                           point_d.get_center())
        angle_half = Arc(start_angle=Line(point_c.get_center(), point_d.get_center()).get_angle(), angle=-angle_ca_cd, radius=0.6, color=WHITE)
        angle_half.shift(point_c.get_center())

        label_angle_half = Tex(r"\frac{\alpha}{2}").next_to(angle_half, RIGHT).scale(0.8).shift(0.05*UP)
        
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
        origin_lable = Tex("O").next_to(origin, UP)

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

    