from manimlib import *

class ani_upd(Scene):
    def construct(self):
        plane = NumberPlane()
        self.add(plane)
        c = Triangle().set_color(RED)
        self.add(c)
        c.add_updater(lambda m, dt: m.shift(dt*RIGHT))

        self.play(
            Rotate(c, 50 * DEGREES, OUT, suspend_mobject_updating=True),
            run_time = 6
        ) 

        print("-"*100)
        print(self.mobjects)
        
class upd(Scene):
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