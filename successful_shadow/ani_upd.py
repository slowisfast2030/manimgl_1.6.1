from manimlib import *

class ani_upd(Scene):
    def construct(self):
        plane = NumberPlane()
        self.add(plane)
        c = Triangle().set_color(RED)
        self.add(c)
        c.add_updater(lambda m, dt: m.shift(dt*RIGHT))

        s = Square().set_color(YELLOW)
        self.add(s)

        self.play(
            Rotate(c, 50 * DEGREES, OUT, suspend_mobject_updating=True),
            s.animate.move_to(UP*2.5),
            run_time = 6,
        ) 

        #print("-"*100)
        #print(self.mobjects)
        
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