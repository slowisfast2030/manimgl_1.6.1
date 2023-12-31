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

    student, teacher = student_teacher
    # 学生一开始设置为gracoius
    student.change_mode("gracious")

    teacher.scale(1.3)
    teacher.flip()

    return student_teacher

class s3(Scene):
    def setup(self):
        self.coord_c = [-4,0,0]
        self.coord_a = [0,0,0]
        self.coord_b = [0,3,0]
        self.line_color = MAROON_B
        self.label_color = WHITE

        self.coord_d = [0, 4/3, 0]
        self.coord_e = [-4/5, 12/5, 0]
        self.coord_f = [1, 0, 0]

        self.shift_vector = np.array([-2, 1.5, 0]) - 3*UP
        self.coord_c_shift = np.array(self.coord_c) - self.shift_vector
        self.coord_a_shift = np.array(self.coord_a) - self.shift_vector
        self.coord_b_shift = np.array(self.coord_b) - self.shift_vector

        # 文本缩放因子
        self.text_scale = 0.8
        pass

    def construct(self):
        self.review_problem()
        self.clear()
        """
        通过pr剪辑插入pr Scene
        """
        self.introduce_triange_plane()
        self.introduce_vertical_line() 
        pass
        
    # 需要注意p1是角所在的位置
    # 这个方法是为了计算p1p2和p1p3之间的夹角
    def angle_of_points(self, p1, p2, p3):
            v1 = np.array(p2) - np.array(p1)
            v2 = np.array(p3) - np.array(p1)
            angle = np.arccos(np.dot(v1, v2)/(np.linalg.norm(v1)*np.linalg.norm(v2)))
            return angle
    
    # 快速回顾问题
    # 屏幕中间出现一个三角形，屏幕下方出现pi生物
    def review_problem(self):
        # 画出学生和老师
        student_teacher = student_with_teacher()

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

        
        
        line_ca = Line(self.coord_c_shift, self.coord_a_shift)
        line_cd = Line(self.coord_c_shift, self.coord_b_shift)
        #angle = Angle(line_ca, line_cd, radius=0.6, other_angle=False)
        angle_ca_cb = self.angle_of_points(self.coord_c_shift, 
                                           self.coord_a_shift, 
                                           self.coord_b_shift)
        angle = Arc(start_angle=Line(self.coord_c_shift, self.coord_b_shift).get_angle(), angle=-angle_ca_cb, radius=0.6, color=WHITE)
        angle.shift(self.coord_c_shift)
        label_angle = Tex(r"\alpha").next_to(angle, RIGHT).scale(0.8).shift(0.05*UP)

        # 将所有的mob向上移动2个单位，为下方的pi生物让出空间
        tri_gr = VGroup(triangle, ver_c, ver_a, ver_b, angle, label_angle).shift(1*UP)

        self.play(*ver_ani, 
                  ShowCreation(triangle),
                  FadeIn(student_teacher),
                  run_time=1)
        #self.wait()
        self.play(Write(angle),
                  FadeIn(label_angle),
                  student_teacher[0].animate.change_mode("connving"),
                    student_teacher[1].animate.change_mode("happy"),
                    run_time=1)
        self.wait()
        
        #text = TexText("It is already to know that $tan(\\alpha) = \\frac{3}{4}$, \\\\ then what is value of $tan(\\frac{\\alpha}{2})$?").scale(self.text_scale).next_to(triangle, DOWN, 1)
        # 用text和Tex的组合引入中文和公式
        # 开篇一定要用中文
        text_0 = Text("已知")
        text_1 = Tex(r"tan(\alpha)=\frac{AB}{AC}=\frac{3}{4},")
        text_2 = Text("那么")
        text_3 = Tex(r"tan(\frac{\alpha}{2})= ?")
        text_01 = VGroup(text_0, text_1).arrange(RIGHT, buff=0.1)
        text_23 = VGroup(text_2, text_3).arrange(RIGHT, buff=0.1)
        text = VGroup(text_01, text_23).arrange(DOWN, buff=0.5).scale(self.text_scale).next_to(triangle, DOWN, 1)
        # 有一个小问题: text_2和text_3的有点不对齐。手动调一下
        text_2.shift(0.05*UP)

        self.play(FadeIn(text), run_time=1)
        self.wait(2.5)

        """
        此时下方的pi生物老师说, 我们来看第三种方法
        """
        pi_text = Text("我们来看第三种方法！").scale(0.7)
        self.play(
                  student_teacher[1].says(pi_text),
                  )
        self.wait(2)
        self.play(student_teacher[0].animate.change_mode("hooray"))
        self.wait(5.5)
        """
        淡出pi生物, 同时出现下方的动画
        """
        # 出现文字：systhetic geometry
        text_syn_en = Text("Synthetic Geometry").scale(self.text_scale)
        text_syn_ch = Text("综合几何").scale(self.text_scale)
        # 出现文字：analytic geometry
        text_ana_en = Text("Analytic Geometry").scale(self.text_scale)
        text_ana_ch = Text("解析几何").scale(self.text_scale)

        text_syn_gr = VGroup(text_syn_en, text_syn_ch).arrange(DOWN, 0.5)
        text_ana_gr = VGroup(text_ana_en, text_ana_ch).arrange(DOWN, 0.5)
        text_gr = VGroup(text_syn_gr, text_ana_gr).arrange(RIGHT, 1.2).shift(DOWN*3)
        #self.play(FadeIn(text_gr))
        self.play(Write(text_syn_en),
                  student_teacher[1].debubble(),
                  FadeOut(student_teacher[0]),
                  FadeOut(student_teacher[1]),)
        self.wait()
        self.play(Write(text_syn_ch))
        self.wait(4)
        self.play(GrowFromCenter(text_ana_gr))
        self.wait(4.5)

        pass

    def  introduce_triange_plane(self):
        # 引入三角形
        triangle = Polygon(self.coord_c_shift, 
                           self.coord_a_shift, 
                           self.coord_b_shift, 
                           color=self.line_color, stroke_width=3)
        ver_c = Tex("C", color=self.label_color).next_to(self.coord_c_shift, DOWN)
        ver_a = Tex("A", color=self.label_color).next_to(self.coord_a_shift, DOWN)
        ver_b = Tex("B", color=self.label_color).next_to(self.coord_b_shift, RIGHT)
        ver_ani = list(map(FadeIn, [ver_c, ver_a, ver_b]))

        
        
        tri_gr = VGroup(triangle, ver_c, ver_a, ver_b)
        # 引入坐标平面
        # 将整个画面网上提一点，为下方的pi生物让出空间
        plane = NumberPlane().shift(3*UP)
        self.play(Write(plane),
                  run_time=2)
        self.wait()

        self.play(*ver_ani, 
                  ShowCreation(triangle),
                  run_time=1)
        self.wait()
        
        # 将整个场景移到屏幕中间
        self.play(plane.animate.shift(-plane.get_center()),
                  tri_gr.animate.shift(-self.coord_a_shift),
                  run_time=1)
        self.wait()

        self.tri_gr = tri_gr
        self.plane = plane
        pass


    # 添加坐标系
    def introduce_vertical_line(self):

        # 显示角平分线
        half_line = Line(self.coord_c, self.coord_d, color=self.line_color)
        ver_d = Tex("D", color=WHITE).next_to(self.coord_d, RIGHT)
        self.play(ShowCreation(half_line), run_time=1)
        self.wait()
        self.play(Write(ver_d), run_time=1)
        self.wait()

        # 显示直线CD的垂线
        line_ef = Line(self.coord_e, self.coord_f, color=self.line_color)
        ver_e = Tex("E", color=WHITE).next_to(self.coord_e, LEFT)
        ver_f = Tex("F", color=WHITE).next_to(self.coord_f, DOWN)

        self.play(GrowFromPoint(line_ef, self.coord_d), run_time=1)
        self.wait(2)
        self.play(Write(ver_e), Write(ver_f), run_time=1)
        self.wait(3)
        # 给出剩余解法
        # 显示三角形全等
        tri_cdb = Polygon(self.plane.c2p(-4,0), 
                          self.plane.c2p(0,4/3), 
                          self.plane.c2p(0,3), 
                          color=self.line_color, 
                          stroke_width=3)
        tri_cdb.set_fill(BLUE, 0.6)
        tri_cdf = Polygon(self.plane.c2p(-4,0),
                            self.plane.c2p(0,4/3),
                            self.plane.c2p(1,0),
                            color=self.line_color,
                            stroke_width=3)
        tri_cdf.set_fill(GREEN, 0.6)
        

        text0 = Tex(r"\triangle CDB \cong \triangle CDF").next_to(self.plane, UP, buff=2.5).scale(self.text_scale)
        text0_center = text0.get_center()
        self.play(Write(text0), 
                  Write(tri_cdb),
                  Write(tri_cdf),
                  run_time=1)
        self.wait(3)
        text0_res = Tex("\Rightarrow  F(1,0)").scale(self.text_scale)
        text0_gr = VGroup(text0.copy(), text0_res).arrange(RIGHT, buff=0.3).move_to(text0_center)
        
        self.play(ReplacementTransform(text0, text0_gr[0]),
                  Write(text0_res),
                  Indicate(ver_f),
                  )
        self.wait(3.5)
        # 显示垂直和斜率乘积为-1
        line_ef = Line(self.coord_e, self.coord_f, color=RED)
        line_cb = Line(self.coord_c, self.coord_b, color=RED)

        text1 = Tex(r"EF \perp CB").scale(self.text_scale)
        text1_res = Tex(r"\Rightarrow  k_{EF} \cdot k_{CB} = -1").scale(self.text_scale)
        text1_gr = VGroup(text1, text1_res).arrange(RIGHT, buff=0.3).next_to(text0_gr, DOWN, buff=0.5)
        self.play(Write(text1), 
                  Indicate(line_ef),
                    Indicate(line_cb),
                  run_time=1)
        self.wait(2)
        self.play(Write(text1_res), run_time=1)
        self.wait()

        # 显示直线BC的斜率
        text2 = Tex(r"k_{CB} = \frac{3}{4}").scale(self.text_scale)
        text2_res = Tex(r"\Rightarrow  k_{EF} = -\frac{4}{3}").scale(self.text_scale)
        text2_gr = VGroup(text2, text2_res).arrange(RIGHT, buff=0.3).next_to(text1_gr, DOWN, buff=0.5)
        self.play(Write(text2), run_time=1)
        self.wait(2)
        self.play(Write(text2_res), run_time=1)
        self.wait(2.5)

        # 显示直线EF的方程和点D的坐标
        line_ef = Line(self.coord_e, self.coord_f, color=YELLOW)
        text3 = Tex(r"EF: y = -\frac{4}{3}x + \frac{4}{3}").scale(self.text_scale).next_to(self.plane, DOWN, buff=-2.5)
        text3_center = text3.get_center()
        text3_res = Tex(r"\Rightarrow D(0, \frac{4}{3})").scale(self.text_scale)
        text3_gr = VGroup(text3.copy(), text3_res).arrange(RIGHT, buff=0.3).move_to(text3_center)
        self.play(Write(text3), 
                  Indicate(line_ef),
                  run_time=1)
        self.wait(2)
        self.play(
            ReplacementTransform(text3, text3_gr[0]),
            Write(text3_res), 
            Indicate(ver_d),
            run_time=1)
        self.wait(3.6)
        # 显示最终结论
        text4 = Tex(r"tan(\frac{\alpha}{2}) = \frac{AD}{AC} = \frac{1}{3}").scale(self.text_scale).next_to(text3_gr, DOWN, buff=0.5)
        self.play(Write(text4), run_time=1)
        self.wait(7)



        pass  




class pr(s3):
    def construct(self):

        self.two_geometry() 
        self.two_geometry_example()
        pass

    # 引入两种几何
    def two_geometry(self):
        # 综合几何
        svg_compass = SVGMobject("c1.svg").set_fill(GREEN_B, 0.7)
        svg_ruler = SVGMobject("ruler.svg").set_fill(TEAL, 0.5).match_height(svg_compass)
        svg_gr = VGroup(svg_ruler, svg_compass).arrange(RIGHT, buff=0.5).scale(1.5)

        # 解析几何
        plane = NumberPlane().scale(0.5)

        # 整体
        geo_gr = VGroup(svg_gr, plane).arrange(DOWN, buff=2).scale(1.1)

        # Display the image
        self.play(Write(svg_gr[0]),
                  Write(svg_gr[1]),
                  Write(plane),
                  run_time = 2)
        self.wait(2)

        # 为了分别讲解两个几何, 需要设置一个起到遮罩的作用的矩形
        rec_up = Rectangle(height=geo_gr[0].get_height()+0.5, width=config.frame_width, color=BLACK, fill_opacity=0.6).move_to(geo_gr[0])
        rec_down = Rectangle(height=geo_gr[1].get_height()+0.5, width=config.frame_width, color=BLACK, fill_opacity=0.6).move_to(geo_gr[1])
        
        # 淡入下面的矩形
        self.play(FadeIn(rec_down), run_time=1)
        self.wait(9.2)
        # 淡入上面的矩形
        self.play(FadeIn(rec_up), FadeOut(rec_down),run_time=1)
        self.wait(6.5)

        self.play( 
                  FadeIn(rec_down))
        #self.wait(1)

        # 添加一个rect, 用来遮住所有的对象
        rect = Rectangle(height=config.frame_height, width=config.frame_width, color=BLACK, fill_opacity=1)
        self.play(FadeIn(rect), run_time=1)
        #self.wait(1)
        pass

    # 以将军饮马问题介绍两种几何
    def two_geometry_example(self):
        bank = Line([-4, 0, 0], [4, 0, 0], color=WHITE)
        point_a = Dot([-1, 1, 0], color=WHITE)
        point_b = Dot([2, 2, 0], color=WHITE)
        label_a = Tex("A", color=WHITE).next_to(point_a, UP)
        label_b = Tex("B", color=WHITE).next_to(point_b, UP)
        bank_gr = VGroup(bank, point_a, point_b, label_a, label_b)

        # 上
        bank_up = bank_gr.copy()
        # 下
        bank_down = bank_gr.copy()

        bank_up_down = VGroup(bank_up, bank_down).arrange(DOWN, buff=3)
        bank_up.shift(UP)
        self.play(Write(bank_up_down), run_time=1)
        self.wait(1.76)

        # 求解A的对称点
        ver_dis = bank_up[1].get_center()[1] - bank_up[0].get_center()[1]
        point_a_sym_x = bank_up[1].get_center()[0]
        point_a_sym_y = bank_up[1].get_center()[1] - 2*ver_dis
        point_a_sym = Dot([point_a_sym_x, point_a_sym_y, 0], color=WHITE)
        label_a_sym = Tex("A'", color=WHITE).next_to(point_a_sym, DOWN)

        line_a_sym_b = Line(point_a_sym.get_center(), bank_up[2].get_center(), color=RED)   
        
        plane = NumberPlane().shift(bank_down[0].get_center()).scale(0.7)
        point_c = Dot(plane.get_center() + RIGHT, color=WHITE)
        label_c = Tex("C(x,y)", color=RED).next_to(point_c, DOWN)
        self.play(FadeIn(plane), 
                  Write(point_a_sym), 
                  Write(label_a_sym), 
                  run_time=1)

        self.wait(3)

        self.play(Write(point_c),
                  Write(label_c),
                  ShowCreation(line_a_sym_b))
        self.wait(6)

        ani = list(map(FadeOut, self.mobjects))
        #self.play(*ani)
        pass

    # 以费马点的例子介绍两种几何
    def two_geometry_example_depreate(self):
        self.clear()
        c_a = [-1.4, -1, 0]
        c_b = [1.1, -1.4, 0]
        c_c = [0, 1.2, 0]
        triangle = Polygon(c_a, c_b, c_c, color=self.line_color, stroke_width=3)
        self.play(Write(triangle), run_time=1)

        ver_a = Tex("A", color=WHITE).next_to(c_a, DOWN)
        ver_b = Tex("B", color=WHITE).next_to(c_b, DOWN)
        ver_c = Tex("C", color=WHITE).next_to(c_c, UP)
        ver_ani = list(map(FadeIn, [ver_a, ver_b, ver_c]))
        self.play(*ver_ani, run_time=1)

        tri_bc = self.get_equilateral_triangle(Line(c_b, c_c))
        dot_e_label = Tex("E", color=WHITE).next_to(tri_bc[2], RIGHT)

        tri_ca = self.get_equilateral_triangle(Line(c_c, c_a))
        dot_d_label = Tex("D", color=WHITE).next_to(tri_ca[2], LEFT)

        tri_ab = self.get_equilateral_triangle(Line(c_a, c_b))
        dot_f_label = Tex("F", color=WHITE).next_to(tri_ab[2], DOWN)

        self.play(Write(dot_e_label), Write(dot_d_label), Write(dot_f_label), run_time=1)

        self.play(ShowCreation(tri_bc[0].reverse_points()),
                  ShowCreation(tri_bc[1]),
                    ShowCreation(tri_ca[0].reverse_points()),
                    ShowCreation(tri_ca[1]),
                    ShowCreation(tri_ab[0].reverse_points()),
                    ShowCreation(tri_ab[1]),
                    run_time=1)
        
        # 显示费马点
        line_ae = Line(c_a, tri_bc[2].get_center(), color=BLUE_C)
        line_bd = Line(c_b, tri_ca[2].get_center(), color=BLUE_C)
        line_cf = Line(c_c, tri_ab[2].get_center(), color=BLUE_C)

        self.play(ShowCreation(line_ae),
                    ShowCreation(line_bd),
                    ShowCreation(line_cf),
                    run_time=1) 
        
    def get_equilateral_triangle(self, line):
        # 将line顺指针和逆时针各旋转一次
        start = line.get_start()
        end = line.get_end() 
        
        # 以start为旋转中心，顺时针旋转PI/3
        line1 = Line(start, end).copy().set_color(WHITE)
        line1.rotate(-PI/3, about_point=start) 
        # 将end也顺时针旋转PI/3
        dot = Dot(end)
        dot.rotate(-PI/3, about_point=start)

        # 以end为旋转中心，逆时针旋转PI/3
        line2 = Line(start, end).copy().set_color(WHITE)
        line2.rotate(PI/3, about_point=end)

        return VGroup(line1, line2, dot)





