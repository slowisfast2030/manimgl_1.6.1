from manimlib import *

class test(Scene):
    def construct(self):

        c = Circle()
        print(c.get_points())
        for p in c.get_points():
            self.add(Dot(p).set_color(YELLOW_E).set_opacity(0.5))

        c.resize_points(300)
        print("-"*100)
        print(c.get_points())
        for p in c.get_points():
            self.add(Dot(p).set_color(RED))

        # cc = Circle().set_points(c.get_points())
        # self.add(cc)
        self.wait(1)    


class test1(Scene):
    def construct(self):

        c = Tex(r"\pi").scale(0.2).set_color(TEAL)
        cg = c.get_grid(10, 10, 5)
        self.add(cg)
        self.wait(1)

class test2(Scene):
    def construct(self):
        c = Circle().set_color([RED, GREEN, BLUE]).set_opacity(0.5)
        c.set_color_by_gradient([RED, GREEN, BLUE])
        print(c.data)
        print("-"*100)
        print(c.uniforms)

        # c.data["fill_rgba"] = np.array([[0, 1, 0., 1     ],
        #                                 [1, 0, 0., 1     ],
        #                                 [0, 0, 1., 1     ],
        #                                 [0, 1, 0., 1     ],
        #                                 [1, 0, 0., 1     ],
        #                                 [0, 0, 1., 1     ]])
        
        d = Mobject()
        d.set_rgba_array_by_color(color=[RED, GREEN, BLUE], opacity=0.5)
        print('+'*100)
        print(d.data['rgbas'])
        


        self.add(c)
        self.wait(1)

        print(color_to_rgb(RED))
        print(color_to_rgb(GREEN))
        print(color_to_rgb(BLUE))

        print(color_gradient([RED, GREEN, BLUE],3))
        