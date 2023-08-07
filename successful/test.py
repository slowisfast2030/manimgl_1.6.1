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

        c.next_to(s, LEFT, buff=0)
        self.add(c, s)
        self.wait(1)

        d1 = Dot(np.array([-1., 0., 0.])).set_color(RED)
        d2 = Dot(np.array([1., 0., 0.])).set_color(BLUE)
        self.add(d1, d2)



