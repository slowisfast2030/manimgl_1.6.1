from manimlib import *

"""
屏幕大小16：9
屏幕中心是一个矩形面，矩形面中有一个圆
圆的中心有一个三维坐标系

整个视角一开始是俯视图
然后以特定角度观察
"""
class test(ThreeDScene):
    def construct(self) -> None:
        frame = self.camera.frame
        # frame.reorient(20, 70)
        # def update_frame(frame, dt):
        #     frame.increment_theta(-0.2 * dt)
        # frame.add_updater(update_frame)
        
        axes = ThreeDAxes(x_range=[-5, 5, 1], 
                        y_range=[-5, 5, 1], 
                        z_range=[-5, 5, 1])
        self.add(axes)

        #rec = Rectangle(width=4, height=4).set_color(BLUE_E).set_opacity(0.5)
        def uv_func(u:float, v:float) -> np.ndarray:
            return np.array([
                u,
                v,
                0
            ])

        s = ParametricSurface(
            uv_func,
            u_range=[-4, 4],
            v_range=[-4, 4]
        ).set_color(BLUE_E).set_opacity(0.1)
        self.add(s)

        # c = Circle(radius=3.8).set_color(RED)
        # self.add(c)

        def func_down(t):
            return np.array([3*np.cos(t), 3*np.sin(t), 0])
        
        def func_up(t):
            return np.array([3*np.cos(t), 3*np.sin(t), 0.8*np.sin(2*t) + 2])
        

        curve_down = ParametricCurve(func_down,
                                t_range=[0, 2*PI]).set_color(RED)
        
        
        
        self.play(ShowCreation(curve_down), run_time=1)
        

        self.play(frame.animate.reorient(20, 70), run_time=1)

        curve_up = ParametricCurve(func_up,
                                t_range=[0, 2*PI]).set_color(WHITE)
        self.play(TransformFromCopy(curve_down, curve_up), run_rime=1)

        """
        在底面的圆上浮现出均匀分布的红色小球
        """
        spheres = self.get_spheres_on_circle(30, curve_down)
        self.add(spheres)

        sphere_anim = []
        for sphere, i in zip(spheres, np.linspace(0, 2*PI, 30)):
            sphere_anim.append(sphere.animate.move_to(np.array(func_up(i))))
            
        self.play(*sphere_anim, run_time=2)
        self.play(FadeOut(spheres), run_time=1)

        """
        在底面的圆上浮现出均匀分布的蓝色直线
        """
        nums = 20
        time = 0

        lines = self.get_lines_on_circle(nums, curve_down)
        self.add(lines)

        def update_lines(lines, dt):
            nonlocal time, nums
            time += dt
            nums += time * 3
            new_lines = self.get_lines_on_circle(int(nums), curve_down)
            lines.become(new_lines)
        
        lines.add_updater(update_lines)
        self.play(frame.animate.reorient(-10, 70), run_time=2)

        # 蓝色直线高度变得一致
        



    def get_spheres_on_circle(self, nums, circle):
        return Group(*[
            Sphere(radius=0.15).move_to(circle.point_from_proportion(i / max(nums, 1))).set_color(RED)
            for i in range(1, nums)
        ])
    
    def get_lines_on_circle(self, nums, circle):
        return VGroup(*[
            Line(circle.point_from_proportion(i / max(nums, 1)), self.func(circle.point_from_proportion(i / max(nums, 1)), (i / max(nums, 1))*2*PI)).set_color(BLUE)
            for i in range(1, nums)
        ])
    
    def func(self,  point, t):
        return [point[0], point[1], 0.8*np.sin(2*t) + 2]