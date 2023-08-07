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

        print("&"*100)
        print(c.get_bounding_box())
        print(s.get_bounding_box())



class test2(Scene):
    def construct(self):
        c = Square()
        print("&"*100)
        print(c.get_bounding_box())

        self.add(c)
        self.wait(1)

        l = c.get_bounding_box_point(LEFT)
        d_left = Dot(l).set_color(RED)

        r = c.get_bounding_box_point(RIGHT)
        d_right = Dot(r).set_color(TEAL)

        u = c.get_bounding_box_point(UP)
        d_up = Dot(u).set_color(YELLOW)

        d = c.get_bounding_box_point(DOWN)
        d_down = Dot(d).set_color(BLUE)

        self.add(d_left, d_right, d_up, d_down)


class test3(Scene):
    def construct(self):
        c = Square()
        print("&"*100)
        print(c.get_bounding_box())

        self.add(c)
        self.wait(1)

        l = c.get_bounding_box_point(RIGHT)
        d = Dot(l).set_color(RED)

        self.add(d)
        self.wait()
