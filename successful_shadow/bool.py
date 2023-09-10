from manimlib import *
from manimlib.mobject.boolean_ops import Union
#from manimlib import Union # 报错

class bl(Scene):
    def construct(self):
        c1 = Circle().shift(LEFT*0.7)
        c2 = Circle().shift(RIGHT*0.7)
        self.add(c1, c2)

        #c = Intersection(c1, c2).set_fill(TEAL, 0)
        c = Union(c1, c2).set_fill(TEAL, 0).set_stroke(GREEN, 3)
        self.add(c)

        self.wait()


class align(Scene):
    def construct(self):
        p = NumberPlane()
        c = Circle()
        t = Triangle().shift(RIGHT*2)
        s = Square().shift(LEFT*2)
        self.add(p, c, t, s)
        
        subpath = s.get_subpaths()
        print(subpath)
        print(s.get_points())
        for point in subpath[0]:
        #for point in c.get_points(): 
            dot = Dot().move_to(point)
            self.add(dot)
        
        self.wait()

class insert(Scene):
    def construct(self):
        p = NumberPlane()
        c = Circle().scale(3)
        self.add(p, c)

        points = c.insert_n_curves_to_point_list(2, c.get_points())
        for point in points: 
            dot = Dot().move_to(point)
            self.add(dot)

        self.wait()


class insert2(Scene):
    def construct(self):
        p = NumberPlane()
        # c = Circle().scale(3).insert_n_curves(-7)\
        #                      .set_fill(RED, 1)\
        #                      .set_stroke(GREEN, 0)
        
        c = VMobject()
        points = [[1.2,0,0], [1.7, 1.5, 0], [0,0.9,0]]
        c.set_points(points)
        c.set_fill(RED, 1).set_stroke(GREEN, 0)
        self.add(p, c)

        for point in c.get_points(): 
            dot = Dot().move_to(point)
            self.add(dot) 

class line(Scene):
    def construct(self):
        p = NumberPlane()
        
        c = VMobject()
        points = [[0,0,0],
                  [1,1,0],
                  [2,2,0]]
        c.set_points(points)
        self.add(c,p)

class cubic(Scene):
    def construct(self):
        p = NumberPlane()
        
        c = VMobject()
        points = [[0,0,0],
                  [1,1,0],
                  [2,1,0],
                  [3,0,0]]
        for point in points: 
            dot = Dot().move_to(point)
            self.add(dot)  
        
        c.add_cubic_bezier_curve(*points)

        c.add_line_to(np.array([5,1,0]))
        self.add(p, c)

        for point in c.get_points(): 
            dot = Dot().move_to(point).set_color(RED)
            self.add(dot)  
