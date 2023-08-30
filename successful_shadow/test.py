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
                2-u+v if u-v <=2 else 0
            ])
            
        s = ParametricSurface(uv_func,
                              u_range=(0,2),
                              v_range=(-2,0)
                              )
        self.add(s.set_color(BLUE_E).set_opacity(0.5))
        l1 = Line(start=(0,-2,0), end=(0,0,2))
        l2 = Line(start=(0,-2,0), end=(2,0,0))
        l3 = Line(start=(2,0,0), end=(0,0,2))
        vg = VGroup(l1, l2, l3)
        #self.add(vg.set_color(TEAL))
        self.wait(5)

class test2(ThreeDScene):
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
                0
            ])
            
        s = ParametricSurface(uv_func,
                              u_range=(0,2),
                              v_range=(-2,0)
                              )
        #self.add(s.set_color(BLUE_E).set_opacity(0.5))
        
        new_points = []
        for point in s.get_all_points():
            x = point[0]
            y = point[1]
            if x - y <= 2:
                new_points.append(point)
        print(len(s.get_all_points()))
        print(len(new_points))

        ss = VMobject()
        ss.set_points(new_points)
        self.add(ss.set_color(RED))
        self.wait(5)