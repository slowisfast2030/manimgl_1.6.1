from manimlib import *

class test(ThreeDScene):
    def construct(self) -> None:
        frame = self.camera.frame
        frame.reorient(20, 70)
        def update_frame(frame, dt):
            frame.increment_theta(-0.2 * dt)
        frame.add_updater(update_frame)

        axes = ThreeDAxes(x_range=[-5, 5, 1],
                          y_range=[-5, 5, 1],
                          z_range=[-3.5, 4, 1],
                          axis_config={"include_tip": True, "tick_size": 0.05})
        self.add(axes)

        def uv_func(u:float, v:float) -> np.ndarray:
            return np.array([
                u,
                v,
                u**2 + v**2 - 2
            ])

        s = ParametricSurface(
            uv_func,
            u_range=[-2, 2],
            v_range=[-2, 2]
        ).set_color(BLUE_E).set_opacity(0.5)
        
        self.add(s)

        self.wait(3)
        
