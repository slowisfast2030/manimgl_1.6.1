from manimlib import *

class LinusSector(Arc):
    CONFIG = {
        "inner_radius": 1,
        "outer_radius": 2,
        "angle": TAU / 4,
        "start_angle": 0,
        "fill_opacity": 1,
        "stroke_width": 0,
        "color": WHITE,
    }

    def init_points(self):
        inner_arc, outer_arc = [
            Arc(
                start_angle=self.start_angle,
                angle=self.angle,
                radius=radius,
                arc_center=self.arc_center,
            )
            for radius in (self.inner_radius, self.outer_radius)
        ]
        """
        一个巨大的疑问:
        不应该是内环的点集倒序吗？
        """
        # 需要将点集的顺序反过来
        inner_arc.reverse_points()
        self.append_points(outer_arc.get_points())
        # 需要在两段弧线之间添加一条直线
        self.add_line_to(inner_arc.get_points()[0])
        self.append_points(inner_arc.get_points())
        self.add_line_to(outer_arc.get_points()[0])

class test(Scene):
    def construct(self):
        # annular_sector = AnnularSector(inner_radius=1, outer_radius=2, start_angle=0, angle=TAU/4, color=BLUE, stroke_width=1) 
        annular_sector = LinusSector(inner_radius=1, outer_radius=2, start_angle=0, angle=TAU/4, color=BLUE, stroke_width=1) 
        self.add(annular_sector)

        for i, point in enumerate(annular_sector.get_points()):
            dot = Dot(point).scale(0.5).set_fill(RED, 1)
            
            if i % 3 == 0:
                print(i)
                dot.set_fill(YELLOW, 1)
                label = Text(str(i)).next_to(dot, UP).scale(0.3)
            
            self.add(dot, label)

