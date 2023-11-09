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
            u_range=[-2, 2],
            v_range=[-2, 2]
        ).set_color(BLUE_E).set_opacity(0.5)
        self.add(s)

        c = Circle(radius=1.8).set_color(RED)
        self.add(c)