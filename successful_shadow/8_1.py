from manimlib import *
import scipy.spatial


# Helpers
"""
Draw a line from source to p1 to p2.  Where does it
intersect the xy plane?

注释不准确
"""
def project_to_xy_plane(p1, p2):
    """
    如何理解这个函数？
    函数目的: 求出从p1到p2的直线与xy平面的交点

    为了方便讨论, 假设p1和p2在xoy平面的上方, 且p1在p2之上
    vect是一条从p1指向p2的向量
    (z2 / vect[2]) * vect也就是
    (z1 / (z2-z1)) * vect, 就是把vect向量延长z1/(z1-z2)倍, 且取反方向
    从几何角度来看, 延长后的向量的起点(因为取反)恰好在xoy平面上
    假设起点为p3
    那么延长后的向量(z1 / (z1-z2)) * vect = p1 - p3
    进而: p3 = p1 - (p1 - p3)
    """
    x1, y1, z1 = p1
    x2, y2, z2 = p2
    if z2 < z1:
        z2 = z1 + 1e-2  # TODO, bad hack
    vect = p2 - p1
    return p1 - (z2 / vect[2]) * vect


def flat_project(point):
    # return [*point[:2], 0]
    """
    垂直投影?
    为何要对z坐标乘以0.05?
    """
    return [*point[:2], 0.05 * point[2]]  # TODO


def get_pre_shadow(mobject, opacity):
    """
    这里的pre shadow并没有对mobject进行投影
    主要是做了一些属性的修改
    """
    result = mobject.deepcopy()
    if isinstance(result, Group) and all((isinstance(sm, VMobject) for sm in mobject)):
        result = VGroup(*result)
    result.clear_updaters()

    for sm in result.family_members_with_points():
        color = interpolate_color(sm.get_color(), BLACK, opacity)
        sm.set_color(color)
        sm.set_opacity(opacity)
        if isinstance(sm, VMobject):
            sm.set_stroke(
                interpolate_color(sm.get_stroke_color(), BLACK, opacity)
            )
        sm.set_gloss(sm.get_gloss() * 0.5)
        sm.set_shadow(0)
        sm.set_reflectiveness(0)
    return result


def update_shadow(shadow, mobject, light_source):
    """
    随着mobject的变化
    更新shadow的属性
    """
    # 获取光源的中心坐标
    lp = light_source.get_center() if light_source is not None else None

    def project(point):
        if lp is None:
            return flat_project(point)
        else:
            return project_to_xy_plane(lp, point)

    for sm, mm in zip(shadow.family_members_with_points(), mobject.family_members_with_points()):
        """
        The np.apply_along_axis function in NumPy is used to apply a function along 
        a specified axis of a NumPy array. This function is particularly useful when 
        you want to apply a custom function to each slice of the array along a specific 
        axis, rather than applying it element-wise. (0 for columns, 1 for rows)
        """
        sm.set_points(np.apply_along_axis(project, 1, mm.get_points()))
        if isinstance(sm, VMobject) and sm.get_unit_normal()[2] < 0:
            sm.reverse_points()
        if isinstance(sm, VMobject):
            sm.set_fill(opacity=mm.get_fill_opacity())
        else:
            sm.set_opacity(mm.get_opacity())


def get_shadow(mobject, light_source=None, opacity=0.7):
    shadow = get_pre_shadow(mobject, opacity)
    """
    updater的本质:
    每一帧都会调用update_shadow(s, mobject, light_source)函数
    调用的结果是会更新shadow的属性
    比较明显的是location
    比较隐晦的是points set(shape)
    """
    shadow.add_updater(lambda s: update_shadow(s, mobject, light_source))
    return shadow


def get_area(shadow):
    """
    不是很理解这个函数的作用
    对area_vector取模长, 然后乘以0.5?
    """
    return 0.5 * sum(
        get_norm(sm.get_area_vector())
        for sm in shadow.get_family()
    )


def get_convex_hull(mobject):
    """
    The convex hull of a set of points is the smallest convex polygon 
    or polyhedron that contains all the points.
    一组点的凸包是包含所有点的最小凸多边形或凸多面体。
    """
    points = mobject.get_all_points()
    hull = scipy.spatial.ConvexHull(points[:, :2])
    return points[hull.vertices]


def sort_to_camera(mobject, camera_frame):
    # 获取相机的位置（个人猜测，是在世界坐标系）
    cl = camera_frame.get_implied_camera_location()
    # 对子物件进行排序
    mobject.sort(lambda p: -get_norm(p - cl))
    return mobject


def cube_sdf(point, cube):
    """
    The key idea behind signed distance is that each point in space is 
    associated with a distance value, and this value is signed to indicate 
    whether the point is inside or outside the object. 
    
    If the point is inside the object, the signed distance is negative; 
    if the point is outside, the signed distance is positive. 
    This allows for an efficient representation of the geometry while also 
    capturing information about the object's interior and exterior.
    """
    c = cube.get_center()
    vect = point - c
    face_vects = [face.get_center() - c for face in cube]
    return max(*(
        abs(np.dot(fv, vect) / np.dot(fv, fv))
        for fv in face_vects
    )) - 1


def is_in_cube(point, cube):
    return cube_sdf(point, cube) < 0


def get_overline(mob):
    overline = Underline(mob).next_to(mob, UP, buff=0.05)
    overline.set_stroke(WHITE, 2)
    return overline


def get_key_result(solid_name, color=BLUE):
    eq = Tex(
        "\\text{Area}\\big(\\text{Shadow}(\\text{" + solid_name + "})\\big)",
        "=",
        "\\frac{1}{2}", "{c}", "\\cdot",
        "(\\text{Surface area})",
        tex_to_color_map={
            "\\text{Shadow}": GREY_B,
            f"\\text{{{solid_name}}}": color,
            "\\text{Solid}": BLUE,
            "{c}": RED,
        }
    )
    eq.add_to_back(get_overline(eq[:5]))
    return eq


def get_surface_area(solid):
    return sum(get_norm(f.get_area_vector()) for f in solid)


# Scenes

class ShadowScene(ThreeDScene):
    object_center = [0, 0, 3]
    frame_center = [0, 0, 2]
    area_label_center = [0, -1.5, 0]
    surface_area = 6.0
    num_reorientations = 10
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
    inf_light = False
    glow_radius = 10
    glow_factor = 10
    area_label_center = [-2, -1, 0]
    unit_size = 2

    def setup(self):
        self.camera.frame.reorient(-30, 75)
        self.camera.frame.move_to(self.frame_center)
        self.add_plane()
        self.add_solid()
        self.add_shadow()
        self.setup_light_source()

    def add_plane(self):
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

    def add_solid(self):
        self.solid = self.get_solid()
        self.solid.move_to(self.object_center)
        self.add(self.solid)

    def get_solid(self):
        cube = VCube()
        cube.deactivate_depth_test()
        cube.set_height(2)
        cube.set_style(**self.object_style)
        # Wrap in group so that strokes and fills
        # are rendered in separate passes
        cube = self.cube = Group(*cube)
        cube.add_updater(lambda m: self.sort_to_camera(m))
        return cube

    def add_shadow(self):
        light_source = None if self.inf_light else self.camera.light_source
        shadow = get_shadow(self.solid, light_source)

        self.add(shadow, self.solid)
        self.shadow = shadow

    def setup_light_source(self):
        self.light = self.camera.light_source
        if self.inf_light:
            self.light.move_to(100 * OUT)
        else:
            glow = self.glow = TrueDot(
                radius=self.glow_radius,
                glow_factor=self.glow_factor,
            )
            glow.set_color(interpolate_color(YELLOW, WHITE, 0.5))
            glow.add_updater(lambda m: m.move_to(self.light))
            self.add(glow)

    def sort_to_camera(self, mobject):
        return sort_to_camera(mobject, self.camera.frame)

    def get_shadow_area_label(self):
        text = Text("Shadow area: ")
        decimal = DecimalNumber(100)

        label = VGroup(text, decimal)
        label.arrange(RIGHT)
        label.move_to(self.area_label_center - decimal.get_center())
        label.fix_in_frame()
        label.set_backstroke()
        decimal.add_updater(lambda d: d.set_value(
            get_area(self.shadow) / (self.unit_size**2)
        ).set_backstroke())
        return label

    def begin_ambient_rotation(self, mobject, speed=0.2, about_point=None, initial_axis=[1, 1, 1]):
        mobject.rot_axis = np.array(initial_axis)

        def update_mob(mob, dt):
            mob.rotate(speed * dt, mob.rot_axis, about_point=about_point)
            mob.rot_axis = rotate_vector(mob.rot_axis, speed * dt, OUT)
            return mob
        mobject.add_updater(update_mob)
        return mobject

    def get_shadow_outline(self, stroke_width=1):
        outline = VMobject()
        outline.set_stroke(WHITE, stroke_width)
        outline.add_updater(lambda m: m.set_points_as_corners(get_convex_hull(self.shadow)).close_path())
        return outline

    def get_light_lines(self, outline=None, n_lines=100, only_vertices=False):
        if outline is None:
            outline = self.get_shadow_outline()

        def update_lines(lines):
            lp = self.light.get_center()
            if only_vertices:
                points = outline.get_vertices()
            else:
                points = [outline.pfp(a) for a in np.linspace(0, 1, n_lines)]
            for line, point in zip(lines, points):
                if self.inf_light:
                    line.set_points_as_corners([point + 10 * OUT, point])
                else:
                    line.set_points_as_corners([lp, point])

        line = Line(IN, OUT)
        light_lines = line.replicate(n_lines)
        light_lines.set_stroke(YELLOW, 0.5, 0.1)
        light_lines.add_updater(update_lines)
        return light_lines

    def random_toss(self, mobject=None, angle=TAU, about_point=None, meta_speed=5, **kwargs):
        if mobject is None:
            mobject = self.solid

        mobject.rot_axis = normalize(np.random.random(3))
        mobject.rot_time = 0

        def update(mob, time):
            dt = time - mob.rot_time
            mob.rot_time = time
            mob.rot_axis = rotate_vector(mob.rot_axis, meta_speed * dt, normalize(np.random.random(3)))
            mob.rotate(angle * dt, mob.rot_axis, about_point=about_point)

        self.play(
            UpdateFromAlphaFunc(mobject, update),
            **kwargs
        )

    def randomly_reorient(self, solid=None, about_point=None):
        solid = self.solid if solid is None else solid
        solid.rotate(
            random.uniform(0, TAU),
            axis=normalize(np.random.uniform(-1, 1, 3)),
            about_point=about_point,
        )
        return solid

    def init_frame_rotation(self, factor=0.0025, max_speed=0.01):
        frame = self.camera.frame
        frame.d_theta = 0

        def update_frame(frame, dt):
            frame.d_theta += -factor * frame.get_theta()
            frame.increment_theta(clip(
                factor * frame.d_theta,
                -max_speed * dt,
                max_speed * dt
            ))

        frame.add_updater(update_frame)
        return frame


class AllPossibleOrientations(ShadowScene):
    inf_light = True
    limited_plane_extension = 6
    plane_dims = (12, 8)

    def construct(self):
        # Setup
        frame = self.camera.frame
        frame.reorient(-20, 80)
        frame.set_height(5)
        frame.d_theta = 0

        def update_frame(frame, dt):
            frame.d_theta += -0.0025 * frame.get_theta()
            frame.increment_theta(clip(0.0025 * frame.d_theta, -0.01 * dt, 0.01 * dt))

        frame.add_updater(update_frame)
        face = self.solid
        square, normal_vect = face
        normal_vect.set_flat_stroke()
        self.solid = square
        self.remove(self.shadow)
        self.add_shadow()
        self.shadow.deactivate_depth_test()
        self.solid = face
        fc = square.get_center().copy()

        # Sphere points
        sphere = Sphere(radius=1)
        sphere.set_color(GREY_E, 0.7)
        sphere.move_to(fc)
        sphere.always_sort_to_camera(self.camera)

        n_lat_lines = 40
        theta_step = PI / n_lat_lines
        sphere_points = np.array([
            sphere.uv_func(phi, theta + theta_step * (phi / TAU))
            for theta in np.arange(0, PI, theta_step)
            for phi in np.linspace(
                0, TAU, int(2 * n_lat_lines * math.sin(theta)) + 1
            )
        ])
        sphere_points[:, 2] *= -1
        original_sphere_points = sphere_points.copy()
        sphere_points += fc

        sphere_dots = DotCloud(sphere_points)
        sphere_dots.set_radius(0.0125)
        sphere_dots.set_glow_factor(0.5)
        sphere_dots.make_3d()
        sphere_dots.apply_depth_test()
        sphere_dots.add_updater(lambda m: m)

        sphere_lines = VGroup(*(
            Line(sphere.get_center(), p)
            for p in sphere_dots.get_points()
        ))
        sphere_lines.set_stroke(WHITE, 1, 0.05)

        sphere_words = Text("All normal vectors = Sphere")
        uniform_words = Text("All points equally likely")
        for words in [sphere_words, uniform_words]:
            words.fix_in_frame()
            words.to_edge(UP)

        # Trace sphere
        N = len(original_sphere_points)
        self.play(FadeIn(sphere_words))
        self.play(
            ShowCreation(sphere_dots),
            ShowIncreasingSubsets(sphere_lines),
            UpdateFromAlphaFunc(
                face,
                lambda m, a: m.apply_matrix(
                    rotation_between_vectors(
                        normal_vect.get_vector(),
                        original_sphere_points[int(a * (N - 1))],
                    ),
                    about_point=fc
                )
            ),
            run_time=30,
            rate_func=smooth,
        )
        self.play(
            FadeOut(sphere_words, UP),
            FadeIn(uniform_words, UP),
        )
        last_dot = Mobject()
        for x in range(20):
            point = random.choice(sphere_points)
            dot = TrueDot(
                point,
                radius=1,
                glow_factor=10,
                color=YELLOW,
            )
            self.add(dot)
            self.play(
                face.animate.apply_matrix(rotation_between_vectors(
                    normal_vect.get_vector(),
                    point - fc
                ), about_point=fc),
                FadeOut(last_dot, run_time=0.25),
                FadeIn(dot),
                run_time=0.5,
            )
            self.wait(0.25)
            last_dot = dot
        self.play(FadeOut(last_dot))
        self.wait()

        # Sphere itself
        sphere_mesh = SurfaceMesh(sphere, resolution=(21, 11))
        sphere_mesh.set_stroke(BLUE_E, 1, 1)
        for sm in sphere_mesh.get_family():
            sm.uniforms["anti_alias_width"] = 0
        v1 = normal_vect.get_vector()
        normal_vect.scale(0.99, about_point=fc)
        v2 = DR + OUT
        frame.reorient(-5)
        self.play(
            Rotate(
                face, angle_between_vectors(v1, v2),
                axis=normalize(cross(v1, v2))
            ),
            UpdateFromAlphaFunc(
                self.plane, lambda m, a: square.scale(0.9).set_opacity(0.5 - a * 0.5)
            ),
        )
        self.play(
            ShowCreation(sphere_mesh, lag_ratio=0.5),
            FadeIn(sphere),
            sphere_dots.animate.set_radius(0),
            FadeOut(sphere_lines),
            frame.animate.reorient(0),
            run_time=3,
        )
        self.remove(sphere_dots)

        # Show patch
        def get_patch(u, v, delta_u=0.05, delta_v=0.1):
            patch = ParametricSurface(
                sphere.uv_func,
                u_range=(u * TAU, (u + delta_u) * TAU),
                v_range=(v * PI, (v + delta_v) * PI),
            )
            patch.shift(fc)
            patch.set_color(YELLOW, 0.75)
            patch.always_sort_to_camera(self.camera)
            return patch

        patch = get_patch(0.85, 0.6)
        self.add(patch, sphere)

        self.play(
            ShowCreation(patch),
            frame.animate.reorient(10, 75),
            run_time=2,
        )
