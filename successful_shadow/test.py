from manimlib import *

class tri_test(ThreeDScene):
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
                #2-u+v
            ])
            
        s = ParametricSurface(uv_func,
                              u_range=(0,2),
                              v_range=(-2,0),
                              resolution=(101, 101) # 分辨率越高, 边缘的锯齿感越弱
                              )
        self.add(s.set_color(BLUE_E).set_opacity(0.5))
        
        # p1 = [0, -2, 0]
        # p2 = [2, 0, 0]
        # p3 = [0, 0, -2]
        # p = Polygon(p1, p2, p3)

        # self.add(p.set_color(BLUE_E).set_opacity(0.5).set_stroke(width=0))
        self.wait(8)

class tri_surface(ThreeDScene):
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
            if u-v<=2:
                return np.array([
                    u,
                    v,
                    2-u+v
                ])
            else:
                return np.array([u,v,0])
            
        s = ParametricSurface(uv_func,
                              u_range=(0,2),
                              v_range=(-2,0),
                              resolution=(100, 100)
                              )
        self.add(s.set_color(BLUE_E).set_opacity(0.5))
        
        p1 = [2, 2, 0]
        p2 = [2, -2, 0]
        p3 = [-2, -2, 0]
        p4 = [-2, 2, 0]
        p = Polygon(p1, p2, p3, p4).apply_depth_test()

        self.add(p.set_color(BLUE_E).set_opacity(0.3).set_stroke(width=0))
        self.wait(8)

class frame_test(ThreeDScene):
    object_center = [0, 0, 1]
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
            self.add(plane)

        def add_solid():
            cube = VCube()
            cube.deactivate_depth_test()
            cube.set_height(2)
            cube.set_style(**self.object_style)
            cube.space_out_submobjects(1.3)
            # Wrap in group so that strokes and fills
            # are rendered in separate passes
            cube = Group(*cube)
            cube.move_to(self.object_center)
            self.add(cube.deactivate_depth_test())

            sp = Sphere().set_color(BLUE_E).set_opacity(0.8).set_shadow(0.5)
            sp.move_to([-3,0,1])
            #sp = sp.space_out_submobjects(1.3)
            #self.add(sp)
        
        add_plane()
        add_solid()
 
    def construct(self):
        point1 = Sphere(radius=0.05).move_to([1,1,0]).set_color(GREEN)
        self.add(point1)

        point2 = Sphere(radius=0.05).move_to([0,0,0]).set_color(RED)
        self.add(point2)

        frame = self.camera.frame

        print("="*100)

        frame.reorient(30, 70)
        def update_frame(frame, dt):
            frame.increment_theta(-0.2 * dt)

        frame.add_updater(update_frame)

        print(frame.get_implied_camera_location())   #[0, 0, 16]
        print(frame.get_center())                    #[0, 0, 0]
        print(frame.get_focal_distance())            #16
        print(frame.get_shape())

        # print("\n")
        # frame.set_height(10)
        # print(frame.get_implied_camera_location())   #[0, 0, 20]
        # print(frame.get_center())                    #[0, 0, 0]
        # print(frame.get_focal_distance())            #20
        # print(frame.get_shape())
        
        # print("\n")
        # frame.set_height(8)
        # frame.shift(RIGHT)
        # print(frame.get_implied_camera_location())   #[1, 0, 16]
        # print(frame.get_center())                    #[1, 0, 0]
        # print(frame.get_focal_distance())            #16
        # print(frame.get_shape())

        self.wait(7)


class surface_test(ThreeDScene):
    object_center = [0, 0, 1]
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
            self.add(plane)

        def add_solid():
            cube = VCube()
            cube.deactivate_depth_test()
            cube.set_height(2)
            cube.set_style(**self.object_style)
            cube.space_out_submobjects(1.3)
            # Wrap in group so that strokes and fills
            # are rendered in separate passes
            cube = Group(*cube)
            cube.move_to(self.object_center)
            self.add(cube.deactivate_depth_test())
            self.cube = cube

            # sp = Sphere().set_color(BLUE_E).set_opacity(0.8).set_shadow(0.5)
            # sp.move_to([-3,0,1])
            #sp = sp.space_out_submobjects(1.3)
            #self.add(sp)
        
        add_plane()
        add_solid()
 
    def construct(self):
        point1 = Sphere(radius=0.05).move_to([1,1,0]).set_color(GREEN)
        self.add(point1)

        point2 = Sphere(radius=0.05).move_to([0,0,0]).set_color(RED)
        self.add(point2)

        frame = self.camera.frame

        frame.reorient(20, 70)
        def update_frame(frame, dt):
            frame.increment_theta(-0.2 * dt)

        frame.add_updater(update_frame)
        frame.set_height(10)
        frame.move_to([0,0,1])

        face0 = self.cube[0].move_to((0, 0, 0))
        self.remove(self.cube)
        self.add(face0)
        
        sphere = Sphere(radius=1, u_range=(3*TAU/4, TAU), v_range=(PI/2, PI)).move_to([0,0,1])
        sphere.set_color(BLUE_C, 0.8)
        sphere_mesh = SurfaceMesh(sphere, resolution=(21, 11))
        sphere_mesh.set_stroke(BLUE_E, 1, 1)
        self.add(sphere, sphere_mesh)

        n_lat_lines = 15
        theta_step = PI / n_lat_lines
        sphere_points = 2.5*np.array([
            sphere.uv_func(phi, theta + theta_step * (phi / TAU))
            for theta in np.arange(0, PI, theta_step)
            for phi in np.linspace(
                0, TAU, int(2 * n_lat_lines * math.sin(theta)) + 1
            )
        ])
        sphere_points[:, 2] *= -1
        sphere_points += [0,0,1]
        sphere_dots = DotCloud(sphere_points).set_color(RED)
        #sphere_dots.set_glow_factor(0.5)
        sphere_dots.make_3d()

        self.add(sphere_dots)

        # Show patch
        def get_patch(u, v, delta_u=0.05, delta_v=0.1):
            patch = ParametricSurface(
                sphere.uv_func,
                u_range=(u * TAU, (u + delta_u) * TAU),
                v_range=(v * PI, (v + delta_v) * PI),
            )
            patch.shift([0,0,1])
            patch.set_color(YELLOW, 0.75)
            patch.always_sort_to_camera(self.camera)
            return patch

        patch = get_patch(0.85, 0.6)
        self.add(patch)

        self.wait(8)