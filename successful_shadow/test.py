from manimlib import *

class test(ThreeDScene):
    def construct(self):
        frame = self.camera.frame
        #frame.reorient(20, 70)
        axes = ThreeDAxes(x_range=[-2,2], y_range=[-3,3])
        self.add(axes)

        def uv_func(u: float, v: float) -> np.ndarray:
            return np.array([
            np.cos(u) * np.sin(v),
            np.sin(u) * np.sin(v),
            -np.cos(v)
            ])
        
        s = ParametricSurface(uv_func,
                              u_range=(0,TAU),
                              v_range=(0,PI)
                              )
        self.add(s.set_color(BLUE_E))
        self.wait()

class test1(ThreeDScene):
    def construct(self):
        frame = self.camera.frame
        frame.reorient(20, 70)
        def update_frame(frame, dt):
            frame.increment_theta(-0.2 * dt)

        frame.add_updater(update_frame)

        axes = ThreeDAxes(x_range=[-3,3], 
                          y_range=[-3,3],
                          z_range=[-3,3])
        self.add(axes)

        def uv_func(u: float, v: float) -> np.ndarray:
            return np.array([
                u,
                v,
                #2
                2-u+v if u-v <=2 else 0
            ])
            
        s = ParametricSurface(uv_func,
                              u_range=(0,2),
                              v_range=(-2,0),
                              resolution=(100, 100)
                              )
        self.add(s.set_color(BLUE_E).set_opacity(0.5))
        
        p1 = [0, -2, 0]
        p2 = [2, 0, 0]
        p3 = [0, 0, -2]
        p = Polygon(p1, p2, p3)

        self.add(p.set_color(BLUE_E).set_opacity(0.5).set_stroke(width=0))
        self.wait(8)