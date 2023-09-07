from manimlib import *

class ani_upd(Scene):
    def construct(self):
        plane = NumberPlane()
        self.add(plane)
        c = Triangle().set_color(RED)
        
        c.add_updater(lambda m, dt: m.shift(dt*RIGHT))

        s = Square().set_color(YELLOW)
        
        """
        这里将self.add()函数注释掉, 不影响显示c和s对象
        因为在play动画的过程中, 会执行self.add()操作

        需要注意, 涉及到updater的时候
        需要主动执行self.add()操作, 否则不会显示

        这里给c同时添加了updater和animation
        故可以省略self.add()操作
        """
        # self.add(c)
        # self.add(s)

        self.play(
            Rotate(c, 50 * DEGREES, OUT, suspend_mobject_updating=True),
            # 如果为一个mob同时添加两个animation, 后一个会执行
            #Rotate(s, 50 * DEGREES, OUT, suspend_mobject_updating=True), 
            s.animate.move_to(UP*2.5),
            run_time = 4,
        ) 

        print("-"*100)
        print(self.mobjects)
        
class test(Scene):
    def construct(self):
        plane = NumberPlane()
        self.add(plane)
        c = Triangle().set_color(RED)
        
        self.add(c)
        # 通过为c添加两个updater，实现运动的合成
        c.add_updater(lambda m, dt: m.shift(dt*RIGHT))
        c.add_updater(lambda m, dt: m.shift(dt*DOWN))

        self.wait(3)

        print("-"*100)
        print(self.mobjects)

class apply(Scene):
    def construct(self):
        plane = NumberPlane()
        self.add(plane)
        
        t = Triangle().set_color(RED)
        s = Square().set_color(YELLOW)
        c = Circle().set_color(GREEN)

        tt = t.copy()
        
        ani_t = t.animate.apply_function(lambda point: point+RIGHT*3).build()
        ani_s = s.animate.apply_points_function(lambda points: points+LEFT*3).build()
        #ani_c = c.animate.apply_matrix(np.identity(3)*3, about_point=(1,1,0)).build()
        ani_c = c.animate.apply_function(lambda point: np.dot(point, np.identity(3)*3),about_point=(1,1,0)).build()

        self.play(ani_t,
                  ani_s,
                  ani_c,
                  tt.animate
                  .shift(UP*2)
                  .apply_function(
                        lambda p: [
                            p[0] + 1 * math.sin(p[1]),
                            p[1] + 1 * math.sin(p[0]),
                            p[2]
                        ], about_point=np.array((1,1,0))*3
                    ),
                  run_time=3)

        print("-"*100)
        print(self.mobjects)


class stroke(Scene):
    def construct(self):
        plane = NumberPlane()
        self.add(plane)
        
        t = Triangle().set_fill(GREEN, 0.5).set_stroke(RED, width=3).shift(LEFT)
        tt = Triangle().set_fill(GREEN, 0.5).set_backstroke(RED, width=3).shift(RIGHT)

        self.add(t, tt)
        self.wait()

class triangulation(Scene):
    def construct(self):
        plane = NumberPlane()
        self.add(plane)
        
        t = Circle().set_stroke(RED, width=3).set_fill(GREEN, opacity=0.5)
        self.add(t)
        t.needs_new_triangulation = True
        print(t.get_triangulation())

        self.wait()

class glsl(Scene):
    def construct(self):
        frame = self.camera.frame
        frame.scale(0.5)
        plane = NumberPlane(x_range=(-2,2), y_range=(-2,2), width=8, height=8)
        self.add(plane)
        
        vm = VMobject()
        points = [[0,0,0], [1,0,0], [0.7,0.9,0]] 
        vm.set_points(np.array(points))

        vm.set_fill(GREEN, 0.5).set_stroke(WHITE, 1.5)
        self.add(vm)

        b0 = Dot(points[0]).set_color(RED).scale(0.5)
        b1 = Dot(points[1]).set_color(RED).scale(0.5)
        b2 = Dot(points[2]).set_color(RED).scale(0.5) 
        self.add(b0, b1, b2)

        vm.needs_new_triangulation = True
        print(vm.get_triangulation())
        self.wait()