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
        d = c.get_bounding_box_point(ORIGIN)
        d_down = Dot(d).set_color(BLUE)

        self.add(d_left, d_right, d_up, d_down)


class test3(Scene):
    def construct(self):

        frame = self.camera.frame
        frame.set_euler_angles(
            theta=30*DEGREES, 
            phi=70*DEGREES)

        c = Cube()
        c.set_opacity(0.5)
        print("&"*100)
        print(c.get_bounding_box())

        self.add(c)
        self.wait(1)

        l = c.get_bounding_box_point(DOWN+RIGHT+IN)
        l = c.get_bounding_box_point(ORIGIN)
        s = Sphere(radius=0.1).move_to(l).set_color(RED)

        self.add(s)
        self.wait()


class test4(Scene):
    def construct(self):
        c = Square()
        c.align_on_border(LEFT+UP, buff=0)

        self.add(c)
        self.wait(1)


class test5(Scene):
    def construct(self):
        c = Square().move_to([1,1,0])
        c.shift_onto_screen(buff=0)

        self.add(c)
        self.wait(1)

class test6(Scene):
    def construct(self):
        c = Square()
        for d in c.get_boundary_point(RIGHT):
            self.add(Dot(d).set_color(RED))

        self.add(c)
        self.wait(1)

class test7(Scene):
    def construct(self):
        c = Circle()
        p = c.point_from_proportion(0.81)
        d = Dot(p).set_color(TEAL)
        self.add(c, d)
        self.wait(1)

        for p in c.get_points():
            self.add(Dot(p).set_color(YELLOW_E))

        self.wait(1)

class test8(Scene):
    def construct(self):
        c = Circle()
        self.add(c)

        for p in c.get_points():
            self.add(Dot(p).set_color(YELLOW_E).set_opacity(0.5))

        self.wait(1)

        cc = c.copy()
        cc.resize_points(10)
        self.add(cc)

        for p in cc.get_points():
            self.add(Dot(p).set_color(RED))
        
        self.wait(1)

class test9(Scene):
    def construct(self):
        c = Circle()
        points = c.get_bezier_tuples()
        for point in points:
            print(point)

        self.add(c)
        self.wait(1)


class test10(Scene):
    def construct(self):
        c = Circle()
        s = Square()
        print(c.get_all_points())
        print("-"*100)
        print(s.get_all_points())

        for point in s.get_all_points():
            self.add(Dot(point).set_color(RED))

        ss = s.copy().shift(LEFT*4)
        print("&"*100)
        c.align_points(ss)
        print(c.get_all_points())
        print("-"*100)
        print(ss.get_all_points())

        for point in ss.get_all_points():
            self.add(Dot(point).set_color(TEAL))

        self.add(s, ss)
        self.wait(1)