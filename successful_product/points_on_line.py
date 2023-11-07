from manimlib import *

class PointsOnLine(Scene):
    def construct(self):
        # Define the start and end points of the line
        line_start = LEFT * 4
        line_end = RIGHT * 4
        line = Line(line_start, line_end)
        self.add(line)

        # Initial density and time
        density = 1
        time = 0
        increment = 0.1  # Increment the density linearly with time
        points = VGroup()
        points = self.get_dots_on_line(density, line)

        # Add points on the line
        def update_points(density):
            new_points = self.get_dots_on_line(density, line)
            #points.become(new_points)
            return new_points

        #points = self.get_dots_on_line(2, line)
        self.add(points)
        
        self.play(Transform(points, update_points(2), run_time=1))
        self.play(Transform(update_points(2), update_points(4), run_time=1))

    def get_dots_on_line(self, density, line):
        num_points = int(density * line.get_length())
        return VGroup(*[
            Dot(line.point_from_proportion(i / max(num_points, 1)), radius=0.05)
            for i in range(1, num_points)
        ])
