from manimlib import *

class mesh_test(ThreeDScene):
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
        frame = self.camera.frame

        frame.reorient(70, 70)
        def update_frame(frame, dt):
            frame.increment_theta(-0.2 * dt)

        frame.add_updater(update_frame)
        frame.set_height(10)
        frame.move_to([0,0,1])

        face0 = self.cube[0].move_to((0, 0, 0)).scale(3)
        self.remove(self.cube)
        self.add(face0)
        self.remove(face0)
        
        sphere = Sphere(radius=3, u_range=(0, TAU), v_range=(0, PI)).move_to([0,0,1])
        sphere.set_color(BLUE_C, 0.8)
        # mesh需要研究下，可以进一步加深对曲面和曲线的理解
        sphere_mesh = SurfaceMesh(sphere, resolution=(21, 11))
        sphere_mesh.set_stroke(BLUE_E, 1, 1)
        self.add(sphere, sphere_mesh)

        # Show patch
        def get_patch(u, v, delta_u=0.05, delta_v=0.1):
            patch = ParametricSurface(
                sphere.uv_func,
                u_range=(u * TAU, (u + delta_u) * TAU),
                v_range=(v * PI, (v + delta_v) * PI),
            )
            patch.shift([0,0,1])
            patch.set_color(RED, 0.75)
            patch.always_sort_to_camera(self.camera)
            return patch

        patch = get_patch(0.85, 0.6)
        self.add(patch)

        self.wait(3)