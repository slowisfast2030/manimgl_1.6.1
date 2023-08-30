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
        axes = ThreeDAxes(x_range=[-2,2], y_range=[-3,3])
        self.add(axes)

        def uv_func(u: float, v: float) -> np.ndarray:
            return np.array([
                u,
                v,
                2-u+v
            ])
            
        s = ParametricSurface(uv_func,
                              u_range=(0,2),
                              v_range=(-2,0)
                              )
        self.add(s.set_color(BLUE_E).set_opacity(0.5))
        self.wait()