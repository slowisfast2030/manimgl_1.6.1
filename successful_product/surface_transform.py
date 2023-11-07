from manimlib import *

class test(ThreeDScene):
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
        )
        s_down = ParametricSurface(
            uv_func_down,
            u_range=[-1, 1],
            v_range=[-1, 1]
        )

        self.play(ShowCreation(s_up))
        self.play(Transform(s_up, s_down))
        self.wait(3)
