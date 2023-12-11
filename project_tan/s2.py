from manim import *

"""
辅助圆
"""
# 下面这几行设置竖屏
config.frame_width = 9
config.frame_height = 16

config.pixel_width = 1080
config.pixel_height = 1920

# 一个很聪明的方案
class ShowCreation(Create):
    pass

class s2(Scene):
    def setup(self):
        self.radius = 2
        self.stroke_color = WHITE
        self.radial_line_color = MAROON_B

        # for solve method
        self.line_color = MAROON_B
        self.label_color = WHITE
        self.line_color_auxiliary = BLUE
        self.label_color_auxiliary = BLUE

        self.coord_c = [-4,0,0]
        self.coord_a = [0,0,0]
        self.coord_b = [0,3,0]
        self.shift_vector = np.array([-2, 1.5, 0]) - 2*UP
        self.coord_c_shift = np.array(self.coord_c) - self.shift_vector
        self.coord_a_shift = np.array(self.coord_a) - self.shift_vector
        self.coord_b_shift = np.array(self.coord_b) - self.shift_vector

        # 文本缩放因子
        self.text_scale = 0.8
        pass

    def construct(self):
        self.review_problem()
        self.diameter_angle()
        self.show_two_property()
        self.clear()
        self.solve()
        pass

    # 在第二章开头，首先需要回顾题目！！！且快速
    def review_problem(self):
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

        
        
        line_ca = Line(self.coord_c_shift, self.coord_a_shift)
        line_cd = Line(self.coord_c_shift, self.coord_b_shift)
        angle = Angle(line_ca, line_cd, radius=0.6, other_angle=False)
        label_angle = MathTex(r"\alpha").next_to(angle, RIGHT).scale(0.8).shift(0.05*UP)

        # 将所有的mob向上移动2个单位，为下方的pi生物让出空间
        tri_gr = VGroup(triangle, ver_c, ver_a, ver_b, angle, label_angle).shift(2*UP)

        self.play(*ver_ani, 
                  ShowCreation(triangle),
                  run_time=1)
        self.play(Write(angle),
                  FadeIn(label_angle),)
        """
        此时下方的pi生物老师说, 我们来看第二种方法
        """

        text = Tex("It is already to know that $tan(\\alpha) = \\frac{3}{4}$, \\\\ then what is value of $tan(\\frac{\\alpha}{2})$?").scale(self.text_scale).next_to(triangle, DOWN, 1)
        self.play(FadeIn(text), run_time=1)
        self.wait()

        """
        淡出pi生物, 同时出现下方的动画
        """
        # 出现两行文字，第一行是“直角三角形”，第二行是“半角”
        text1 = Text("直角三角形").scale(self.text_scale)
        text2 = Text("半角").scale(self.text_scale)
        text12_gr = VGroup(text1, text2).arrange(DOWN, buff=1).to_edge(LEFT, buff=1.5)
        text12_gr.shift(3*DOWN)

        self.play(FadeIn(text1),
                  FadeIn(text2),
                  run_time=1)
        self.wait()

        # 在text_gr右侧出现一个括号
        brace = Brace(text12_gr, direction=RIGHT, buff=0.5)
        self.play(GrowFromCenter(brace), run_time=1)
        self.wait() 

        # 在括号右侧出现一行文字“辅助圆”
        text3 = Text("辅助圆").scale(self.text_scale)   
        text3.next_to(brace, RIGHT, 0.5)
        self.play(GrowFromCenter(text3), run_time=1)
        self.wait()

        """
        多亏了gpt4, 实现了我一直想要的操作
        """
        mobjects_to_fade_out = [mobject for mobject in self.mobjects if mobject != text3]
        self.text3 = text3
        self.mobjects_to_fade_out = mobjects_to_fade_out

        # self.play(*[FadeOut(mobject) for mobject in mobjects_to_fade_out])
        # self.wait()
        pass 

    # 在屏幕中间显示一个圆
    # 分别向上和向下移动，作为接下来两个动画的基础
    def diameter_angle(self):
        self.play(self.text3.animate.move_to(ORIGIN+UP*3.2),
            *[FadeOut(mobject) for mobject in self.mobjects_to_fade_out])
        self.wait()

        self.origin = Dot(ORIGIN)
        self.origin_lable = MathTex("O").next_to(self.origin, UP)

        self.circle = Circle(
            radius = self.radius,
            stroke_color = self.stroke_color
        )
        self.radius_line = Line(
            self.circle.get_center(),
            self.circle.get_right(),
            color = self.radial_line_color
        )
        self.radius_brace = Brace(self.radius_line, buff = SMALL_BUFF)
        self.radius_label = self.radius_brace.get_tex("R", buff = SMALL_BUFF)

        self.play(
            ShowCreation(self.radius_line),
            GrowFromCenter(self.radius_brace),
            Write(self.radius_label),
            ShowCreation(self.origin),
            Write(self.origin_lable),
        )
        #self.circle.set_fill(opacity = 0)

        self.play(
            Rotate(
                self.radius_line, 2*PI-0.001, 
                about_point = self.circle.get_center(),
            ),
            ShowCreation(self.circle),
            run_time = 2
        )

        self.wait(1)

        # raidus_brace和radius_label的消失
        # 半径变成直径
        self.line_diameter = Line(
            self.circle.get_left(),
            self.circle.get_right(),
            color = self.radial_line_color
        )
        self.play(
            FadeOut(self.radius_brace),
            FadeOut(self.radius_label),
            FadeOut(self.radius_line),
            #GrowFromCenter(self.line_diameter),
            self.origin_lable.animate.next_to(self.origin, DOWN),
            run_time = 1
        )
        self.wait(1)

        self.circle_gr = VGroup(self.circle, 
                                #self.line_diameter,
                                self.origin,
                                self.origin_lable)
        
        self.two_gr = VGroup(self.circle_gr.copy(),self.circle_gr.copy()).arrange(DOWN, buff=1)

        self.play(TransformFromCopy(self.circle_gr, self.two_gr[0]),
                  TransformFromCopy(self.circle_gr, self.two_gr[1]),
                  FadeOut(self.circle_gr),
                  FadeOut(self.text3),
                  run_time=1)
    
    # 在上下圆中分别显示一个性质
    def show_two_property(self):
        self.clear()
        self.add(self.two_gr)
        self.wait()

        # 上圆显示直径和一个动点
        # 下圆显示三个动点
        circle_1, origin_1, origin_lable_1 = self.two_gr[0]
        circle_2, origin_2, origin_lable_2 = self.two_gr[1]

        # 上圆
        circle_point = Dot(point=circle_1.point_at_angle(PI/3), color=RED)
        circle_point_lable = MathTex("C").next_to(circle_point, UP) 
        line_diameter = Line(circle_1.get_left(), circle_1.get_right(), color=self.radial_line_color)
        line_1 = Line(circle_point.get_center(), line_diameter.get_left(), color=self.radial_line_color)
        line_2 = Line(circle_point.get_center(), line_diameter.get_right(), color=self.radial_line_color)
        # 下圆
        point_a = Dot(circle_2.point_at_angle(PI + PI/6), color=RED)
        point_b = Dot(circle_2.point_at_angle(PI + 5*PI/6), color=RED)
        point_c = Dot(circle_2.point_at_angle(PI/2), color=RED)
        label_a = MathTex("A").next_to(point_a, LEFT)
        label_b = MathTex("B").next_to(point_b, RIGHT)
        label_c = MathTex("C").next_to(point_c, UP)

        line_ao = Line(point_a.get_center(),origin_2, color=self.radial_line_color)
        line_bo = Line(point_b.get_center(),origin_2, color=self.radial_line_color)
        line_ac = Line(point_a.get_center(),point_c.get_center(), color=self.radial_line_color)
        line_bc = Line(point_b.get_center(),point_c.get_center(), color=self.radial_line_color)


        self.play(ShowCreation(circle_point),
                  Write(circle_point_lable),
                  GrowFromCenter(line_diameter),
                  ShowCreation(line_1),
                  ShowCreation(line_2),
                  ShowCreation(point_a),
                  ShowCreation(point_b),
                  ShowCreation(point_c),
                  Write(label_a),
                  Write(label_b),
                  Write(label_c),
                  ShowCreation(line_ao),
                  ShowCreation(line_bo),
                  ShowCreation(line_ac),
                  ShowCreation(line_bc),
                  run_time=1)  

        # 上圆更新器
        move_lines = VGroup(line_1, line_2, circle_point_lable)
        self.add(move_lines)
        def move_lines_updater(mob):
            new_line_1 = Line(circle_point.get_center(), line_diameter.get_left(), color=self.radial_line_color)
            new_line_2 = Line(circle_point.get_center(), line_diameter.get_right(), color=self.radial_line_color)
            line_1.become(new_line_1)
            line_2.become(new_line_2)
            circle_point_lable.next_to(circle_point, UP)
        
        # 下圆更新器
        line_label_gr = VGroup(line_ac, line_bc, label_c)
        self.add(line_label_gr)
        def line_label_gr_updater(mob):
            new_line_ac = Line(point_a.get_center(),point_c.get_center(), color=self.radial_line_color)
            new_line_bc = Line(point_b.get_center(),point_c.get_center(), color=self.radial_line_color)
            new_label_c = MathTex("C").next_to(point_c, UP)
            line_ac.become(new_line_ac)
            line_bc.become(new_line_bc)
            label_c.become(new_label_c)

        # 上圆添加更新器
        move_lines.add_updater(move_lines_updater)
        # 下圆添加更新器
        line_label_gr.add_updater(line_label_gr_updater)


        # 播放动画：点沿圆周运动
        self.play(Rotate(circle_point, PI, about_point=circle_1.get_center(), rate_func=linear),
                  Rotate(point_c, 2*PI/4, about_point=circle_2.get_center(), rate_func=linear), 
                  run_time=2) 
        self.wait()

        self.play(Rotate(circle_point, -PI, about_point=circle_1.get_center(), rate_func=linear),
                    Rotate(point_c, -PI, about_point=circle_2.get_center(), rate_func=linear), 
                    run_time=3)
        self.wait()
        pass

    # 解决问题
    def solve(self):
        triangle = Polygon(self.coord_c_shift, 
                           self.coord_a_shift, 
                           self.coord_b_shift, 
                           color=self.line_color,
                           stroke_width= 3)
        
        ver_c = MathTex("C", color=self.label_color).next_to(self.coord_c_shift, DOWN)
        ver_a = MathTex("A", color=self.label_color).next_to(self.coord_a_shift, DOWN)
        ver_b = MathTex("B", color=self.label_color).next_to(self.coord_b_shift, RIGHT)
        ver_ani = list(map(FadeIn, [ver_c, ver_a, ver_b]))

        self.play(*ver_ani, 
                  ShowCreation(triangle),
                  run_time=1)
        self.wait()

        origin = Dot(triangle.get_center())
        origin_lable = MathTex("O").next_to(origin, DOWN)
        self.play(ShowCreation(origin),
                  Write(origin_lable),
                  run_time=1)
        
        # 以origin为圆心，以OC为半径画圆
        circle = Circle(
            radius = 2.5,
            stroke_color = self.stroke_color
        ).move_to(origin)   
        self.play(ShowCreation(circle), run_time=2)
        self.wait()

        # 绘制三条辅助线,EB,EA,EF
        coord_e_shift = circle.get_left()
        coord_f_shift = 0.5*(self.coord_a_shift + self.coord_b_shift)
        line_eb = Line(coord_e_shift, self.coord_b_shift, color=self.line_color_auxiliary)
        line_ea = Line(coord_e_shift, self.coord_a_shift, color=self.line_color_auxiliary)
        line_ef = Line(coord_e_shift, coord_f_shift, color=self.line_color_auxiliary)
        e_label = MathTex("E", color=self.label_color_auxiliary).next_to(coord_e_shift, LEFT)
        f_label = MathTex("F", color=self.label_color_auxiliary).next_to(coord_f_shift, LEFT)

        self.play(ShowCreation(line_eb),
                    ShowCreation(line_ea),
                    ShowCreation(line_ef),
                    Write(e_label),
                    Write(f_label),
                    run_time=1)
        
        text1 = Tex("It is evident that \\\\ EF is the median line of triangle BCA").next_to(circle, DOWN, buff=1).scale(self.text_scale)
        self.play(Write(text1), run_time=1)
        self.wait()
        text2 = MathTex(r"EF=ED+DF=\frac{5}{2}+2=\frac{9}{2}").next_to(text1, DOWN, buff=0.5).scale(self.text_scale)
        self.play(Write(text2), run_time=1)
        self.wait()
        text3 = MathTex(r"\tan(\frac{\theta}{2})=\frac{BF}{EF}=\frac{1}{3}").next_to(text2, DOWN, buff=0.5).scale(self.text_scale)
        self.play(Write(text3), run_time=1)
        self.wait()


        pass

    # 在圆上任取一点, 连接和直径的端点
    # 已合并到show_two_property中
    def right_angle(self):
        self.clear()
        self.add(self.circle_gr)

        # 获取重要元素
        circle, line_diameter, origin, origin_lable = self.circle_gr
        self.wait()

        # 创建一个圆周上的点
        circle_point = Dot(point=circle.point_at_angle(PI/3), color=RED)
        circle_point_lable = MathTex("C").next_to(circle_point, UP)
        self.play(ShowCreation(circle_point),
                  Write(circle_point_lable),
                  run_time=1)   

        # 创建两条线段，从圆周上的点指向圆的直径的两端
        line_1 = Line(circle_point.get_center(), line_diameter.get_left(), color=self.radial_line_color)
        line_2 = Line(circle_point.get_center(), line_diameter.get_right(), color=self.radial_line_color)
        
        move_lines = VGroup(line_1, line_2)
        """
        这里有一个非常奇怪的点
        如果删除self.add(move_lines)
        更新动画就会异常

        猜想:
        move_lines必须显示的添加到场景中, 后续的更新动画才会起作用
        可以是self.add(move_lines)
        也可以是self.play(ShowCreation(move_lines))
        但不能仅仅是
        self.play(ShowCreation(line_1),
                  ShowCreation(line_2))
        因为这种方式仅仅添加了line_1和line_2, 而没有添加move_lines
        """
        self.add(move_lines)
        self.play(ShowCreation(line_1),
                  ShowCreation(line_2))
        
        # 更新器
        def move_lines_updater(mob):
            new_line_1 = Line(circle_point.get_center(), line_diameter.get_left(), color=self.radial_line_color)
            new_line_2 = Line(circle_point.get_center(), line_diameter.get_right(), color=self.radial_line_color)
            line_1.become(new_line_1)
            line_2.become(new_line_2)

        def circle_point_lable_updater(mob):
            circle_point_lable.next_to(circle_point, UP) 

        # 添加更新器
        move_lines.add_updater(move_lines_updater)
        circle_point_lable.add_updater(circle_point_lable_updater)

        # 播放动画：点沿圆周运动
        self.play(Rotate(circle_point, PI, about_point=circle.get_center(), rate_func=linear), run_time=4)

        # 移除更新器
        move_lines.remove_updater(move_lines_updater)
        circle_point_lable.remove_updater(circle_point_lable_updater)

    # 圆心角和圆周角之间的关系
    # 已合并到show_two_property中
    def double_relation(self):
        self.clear()
        circle, line_diameter, origin, origin_lable = self.circle_gr
        self.add(circle, origin, origin_lable)
        self.wait()

        # 显示圆周角和圆心角
        point_a = Dot(circle.point_at_angle(PI + PI/6), color=RED)
        point_b = Dot(circle.point_at_angle(PI + 5*PI/6), color=RED)
        point_c = Dot(circle.point_at_angle(PI/2), color=RED)
        label_a = MathTex("A").next_to(point_a, LEFT)
        label_b = MathTex("B").next_to(point_b, RIGHT)
        label_c = MathTex("C").next_to(point_c, UP)

        line_ao = Line(point_a.get_center(),origin, color=self.radial_line_color)
        line_bo = Line(point_b.get_center(),origin, color=self.radial_line_color)
        line_ac = Line(point_a.get_center(),point_c.get_center(), color=self.radial_line_color)
        line_bc = Line(point_b.get_center(),point_c.get_center(), color=self.radial_line_color)

        self.play(ShowCreation(point_a),
                  ShowCreation(point_b),
                  ShowCreation(point_c),
                  Write(label_a),
                  Write(label_b),
                  Write(label_c),
                  run_time=1)
        self.wait()

        self.play(ShowCreation(line_ao),
                    ShowCreation(line_bo),
                    ShowCreation(line_ac),
                    ShowCreation(line_bc))
        self.wait()

        # 将line_ac, line_bc, label_c打包
        line_label_gr = VGroup(line_ac, line_bc, label_c)
        self.add(line_label_gr)

        # 更新器
        def line_label_gr_updater(mob):
            new_line_ac = Line(point_a.get_center(),point_c.get_center(), color=self.radial_line_color)
            new_line_bc = Line(point_b.get_center(),point_c.get_center(), color=self.radial_line_color)
            new_label_c = MathTex("C").next_to(point_c, UP)
            line_ac.become(new_line_ac)
            line_bc.become(new_line_bc)
            label_c.become(new_label_c)

        line_label_gr.add_updater(line_label_gr_updater)

        # 播放动画：点沿圆周运动
        self.play(Rotate(point_c, 2*PI/4, about_point=circle.get_center(), rate_func=linear), run_time=2)
        self.wait()
        self.play(Rotate(point_c, -PI, about_point=circle.get_center(), rate_func=linear), run_time=3)

