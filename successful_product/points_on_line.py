from manimlib import *

# from gpt4
class test(Scene):
    def construct(self):
        # Define the start and end points of the line
        line_start = LEFT * 4
        line_end = RIGHT * 4
        line = Line(line_start, line_end)
        self.add(line)

        # Initial density and time
        density = 1
        time = 0
        increment = 0.8  # Increment the density linearly with time
        #points = VGroup()
        points = self.get_dots_on_line(density, line)

        # Add points on the line
        def update_points(points, dt):
            nonlocal time, density
            time += dt
            density += increment * dt
            new_points = self.get_dots_on_line(density, line)
            points.become(new_points)
            #points.shift(dt * RIGHT)

        points.add_updater(update_points)
        self.add(points)

        self.wait(5)  # The animation will last for 5 seconds

    def get_dots_on_line(self, density, line):
        num_points = int(density * line.get_length())
        return VGroup(*[
            Dot(line.point_from_proportion(i / max(num_points, 1)), radius=0.05)
            for i in range(1, num_points)
        ])


class test1(Scene):
    def construct(self):
        # Define the start and end points of the line
        line_start = LEFT * 4
        line_end = RIGHT * 4
        line = Line(line_start, line_end)
        self.add(line)

        # Initial density and time
        density = 1
        time = 0
        increment = 0.8  # Increment the density linearly with time
        #points = VGroup()
        points = self.get_dots_on_line(density, line)

        # Add points on the line
        def update_points(points, dt):
            nonlocal time, density
            time += dt
            density += increment * dt
            new_points = self.get_dots_on_line(density, line)
            points.become(new_points)
            #points.shift(dt * RIGHT)

        points.add_updater(update_points)
        self.add(points)

        self.wait(3)  # The animation will last for 5 seconds

        ani_list = []
        for point in points:
            point_copy = Line(point.get_start(), point.get_start()+UP*2)

            ani_list.append(Transform(point, point_copy))

        self.play(*ani_list, run_time=2)


    def func(self,  point):
        return [point[0], 2+np.sin(point[0]), point[2]]

    def get_dots_on_line(self, density, line):
        num_points = int(density * line.get_length())
        return VGroup(*[
            Line(line.point_from_proportion(i / max(num_points, 1)), self.func(line.point_from_proportion(i / max(num_points, 1))))
            for i in range(1, num_points)
        ])
    

# gpt4
class EqualizeLines(Scene):
    def construct(self):
        # Initial data for lines
        line_lengths = [2, 3, 1, 4, 0.5, 3, 1, 2, 4, 0.5]
        lines_start = ORIGIN + LEFT * len(line_lengths) / 2  # starting point for the first line
        
        # Create the lines
        lines = VGroup(*[
            Line(start=lines_start + RIGHT * i, end=lines_start + RIGHT * i + UP * length, stroke_width=10)
            for i, length in enumerate(line_lengths)
        ])
        
        # Show the original lines
        self.play(ShowCreation(lines))
        self.wait(1)
        
        # The target length for all lines
        target_length = 3
        
        # Create a list of animations to change the length of each line
        length_change_animations = []
        for line in lines:
            # The new end point for the line with the desired length
            start_point = line.get_start()
            end_point = start_point + UP * target_length
            # Create the animation and add to the list
            length_change_animations.append(ApplyMethod(line.put_start_and_end_on, start_point, end_point))
        
        # Play all animations simultaneously
        self.play(*length_change_animations, run_time=2)
        self.wait(2)
