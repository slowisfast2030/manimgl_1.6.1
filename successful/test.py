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
        s = Square()

        c.next_to(s, LEFT)
        self.add(c, s)
        self.wait(1)
