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
        self.add(t)

        s = Square().set_color(YELLOW)
        self.add(s) 
        
        ani_t = t.animate.apply_function(lambda point: point+RIGHT*3).build()
        ani_s = s.animate.apply_points_function(lambda points: points+LEFT*3).build()

        self.play(ani_t,
                  ani_s,
                  run_time=3)

        print("-"*100)
        print(self.mobjects)