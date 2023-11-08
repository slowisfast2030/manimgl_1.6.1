from manimlib import *

"""
这个场景想实现的功能：
一条直线上均匀分布着一些点，随着时间的前进，点的密度会变大
我们可以从每一帧的角度进行分析
假设第一帧的直线上有5个点
第二帧的直线上有10个点
第三帧的直线上有15个点
...
实现动画主要有两种方式：
1.updater
2.animation

当前代码采取了updater的方式来实现
一般而言，updater只是作用于单个对象
但是这里创造性的将其作用于一个VGroup
updater有一个极其重要的参数dt：每一帧的间隔
我们可以定义另一个变量time，来记录时间的前进
time += dt
如果我们提前确定updater的持续时间，就可以将time转化为动画的执行比例alpha
mob.add_updater(update_func)
self.wait() or self.play()
mob.remove_updater(update_func)
对于上述这种写法就可以精确控制updater的执行时间

updater是一种控制力很强的动画实现方式
可以精确控制每一帧的行为

如果采取animation的方法来实现，我们需要将每一帧的点集看做一个整体
可以借助UpdateFromAlphaFunc类来实现
在一般的animation的代码示例中，一般都是作用于单个对象，比如一个点
将点集看做是一个整体，比较少见

个人觉得，Transform类更适合单个对象的变换
why？因为Transform需要指定当前对象和目标对象，在动画的过程中涉及点与点的对应关系
而当前动画最大的特点是，点的个数是不断变化的
Transform非常不适合VGroup之间的变换

当Transform作用于单个对象的时候，是一种很省力的创作动画的方式
因为只给出了目标对象，动画过程中如何插值已经被封装好了

而UpdateFromAlphaFunc类可以说，是一种比较底层的动画实现方式
因为它需要指定每一帧的动画过程，而不是只指定目标对象
由于精确到每一帧的控制，所以UpdateFromAlphaFunc类的灵活性是非常高的
既适合单个对象，也适合VGroup
如果做进一步的深入分析，会发现UpdateFromAlphaFunc类和updater的本质是一样的
只不过前者是通过alpha做插值，后者是通过dt做插值

---------------
考虑两类动画：
1.对象的数目不发生变化，但每一个对象的属性会发生变化
2.对象的数目会发生变化

对于第一种实现方式就多了。最简单的就是为每一个对象找到其对应的目标对象，然后使用Transform类
self.play()一次可以传输很多个animation
也可以将这些对像当做整体VGroup，使用UpdateFromAlphaFunc类，也可以实现
用updater也可以。不论是单个对象还是VGroup。

对于第二类动画，已经讨论过了
需要将这个对象当做整体VGruop，使用UpdateFromAlphaFunc类或者updater

"""
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
        points = self.get_dots_on_line(density, line)

        # Add points on the line
        def update_points(points, dt):
            # 这一步确实很亮眼
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
