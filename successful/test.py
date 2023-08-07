from manimlib import *

class test(Scene):
    def construct(self):

        g = Group()
        c = Circle()
        s = Square()
        t = Triangle()

        g.add(c)
        g.add(s)
        g.add(t)
        
        print("*"*100)
        print(g.submobjects)

            

        g.arrange(LEFT, center=False)

        self.add(g)
        self.wait(1)

class test1(Scene):
    def construct(self):
        c = Circle()
        s = Square().center()
        cc = c.copy().set_color(TEAL)

        c.next_to(s, UP, buff=0)
        self.add(c, s)
        self.wait(1)

        d1_target_point = Dot(np.array([0., 1., 0.])).set_color(RED)
        d2_point_to_align = Dot(np.array([0., -1., 0.])).set_color(BLUE)
        self.add(d1_target_point, d2_point_to_align)
        self.add(cc)



