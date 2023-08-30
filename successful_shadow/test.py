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

class frame_test(ThreeDScene):
    object_center = [1, 0, 0]
    plane_dims = (20, 20)
    plane_style = {
        "stroke_width": 0,
        "fill_color": GREY_A,
        "fill_opacity": 0.5,
        "gloss": 0.5,
        "shadow": 0.2,
    }
    limited_plane_extension = 0
    object_style = {
        "stroke_color": WHITE,
        "stroke_width": 0.5,
        "fill_color": BLUE_E,
        "fill_opacity": 0.7,
        "reflectiveness": 0.3,
        "gloss": 0.1,
        "shadow": 0.5,
    }
    def setup(self):
        
        def add_plane():
            width, height = self.plane_dims

            grid = NumberPlane(
                x_range=(-width // 2, width // 2, 2),
                y_range=(-height // 2, height // 2, 2),
                background_line_style={
                    "stroke_color": GREY_B,
                    "stroke_width": 1,
                },
                faded_line_ratio=4,
            )
            grid.shift(-grid.get_origin())
            grid.set_width(width)
            grid.axes.match_style(grid.background_lines)
            grid.set_flat_stroke(True)
            grid.insert_n_curves(3)

            plane = Rectangle()
            plane.replace(grid, stretch=True)
            plane.set_style(**self.plane_style)
            plane.set_stroke(width=0)
            if self.limited_plane_extension > 0:
                plane.set_height(height // 2 + self.limited_plane_extension, about_edge=UP, stretch=True)
            self.plane = plane

            plane.add(grid)
            self.add(plane.shift(RIGHT))

        def add_solid():
            cube = VCube()
            cube.deactivate_depth_test()
            cube.set_height(2)
            cube.set_style(**self.object_style)
            # Wrap in group so that strokes and fills
            # are rendered in separate passes
            cube = Group(*cube)
            cube.move_to(self.object_center)
            self.add(cube)
        
        add_plane()
        add_solid()
 
    def construct(self):
        frame = self.camera.frame

        print("="*100)

        frame.reorient(0, 0)
        print(frame.get_implied_camera_location())   #[0, 0, 16]
        print(frame.get_center())                    #[0, 0, 0]
        print(frame.get_focal_distance())            #16

        print("\n")
        frame.set_height(10)
        print(frame.get_implied_camera_location())   #[0, 0, 20]
        print(frame.get_center())                    #[0, 0, 0]
        print(frame.get_focal_distance())            #20
        
        print("\n")
        frame.set_height(8)
        frame.shift(RIGHT)
        print(frame.get_implied_camera_location())   #[1, 0, 16]
        print(frame.get_center())                    #[1, 0, 0]
        print(frame.get_focal_distance())            #16

        self.wait(1)