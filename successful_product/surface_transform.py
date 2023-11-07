from manimlib import *

class test(ThreeDScene):
    def construct(self):
        frame = self.camera.frame
        frame.reorient(20, 70)
        def update_frame(frame, dt):
            frame.increment_theta(-0.2 * dt)
        frame.add_updater(update_frame)

        axes = ThreeDAxes(x_range=[-3, 3, 1], 
                        y_range=[-3, 3, 1], 
                        z_range=[-3, 3, 1],
                        width=10,
                        height=10)
        self.add(axes)

        def uv_func_up(u:float, v:float) -> np.ndarray:
            return np.array([
                u,
                v,
                u**2 + v**2 + 1
            ])

        def uv_func_down(u:float, v:float) -> np.ndarray:
            return np.array([
                u,
                v,
                0
            ])

        s_up = ParametricSurface(
            uv_func_up,
            u_range=[-1, 1],
            v_range=[-1, 1]
        ).set_color(BLUE_E)

        s_down = ParametricSurface(
            uv_func_down,
            u_range=[-2, 2],
            v_range=[-2, 2]
        ).set_color(BLUE_E)

        self.play(ShowCreation(s_up))
        self.play(Transform(s_up, s_down), run_time=3)
        self.wait(3)


class test1(ThreeDScene):
    def construct(self):
        frame = self.camera.frame
        frame.reorient(20, 70)
        def update_frame(frame, dt):
            frame.increment_theta(-0.2 * dt)
        frame.add_updater(update_frame)

        axes = ThreeDAxes(x_range=[-5, 5, 1], 
                        y_range=[-5, 5, 1], 
                        z_range=[-5, 5, 1])
        self.add(axes)

        def uv_func_down(u:float, v:float) -> np.ndarray:
            return np.array([
                u,
                v,
                0
            ])

        s_up = Sphere().set_color(BLUE_E).scale(2)

        s_down = Cylinder().set_color(BLUE_E).scale(2)

        self.play(ShowCreation(s_up))
        self.play(Transform(s_up, s_down))
        self.wait(3)

class test2(ThreeDScene):
    def construct(self):
        frame = self.camera.frame
        frame.reorient(20, 70)
        def update_frame(frame, dt):
            frame.increment_theta(-0.2 * dt)
        frame.add_updater(update_frame)

        axes = ThreeDAxes(x_range=[-3, 3, 1], 
                        y_range=[-3, 3, 1], 
                        z_range=[-3, 3, 1],
                        width=10,
                        height=10)
        self.add(axes)

        def func_down(t):
            return [np.cos(t), np.sin(t), 0]
        
        def func_up(t):
            return [np.cos(t), np.sin(t), 0.5*np.sin(2*t) + 1]
        

        curve_down = ParametricCurve(func_down,
                                t_range=[0, 2*PI]).scale(2)
        
        curve_up = ParametricCurve(func_up,
                                t_range=[0, 2*PI]).scale(2).shift(OUT)
        
        self.play(ShowCreation(curve_down), run_time=2)
        self.play(TransformFromCopy(curve_down, curve_up), run_rime=3)

        self.wait(1)

        