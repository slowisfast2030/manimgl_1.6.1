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

        # Probability expression
        patch_copy = patch.deepcopy()
        sphere_copy = sphere.deepcopy()
        sphere_copy.set_color(GREY_D, 0.7)
        for mob in patch_copy, sphere_copy:
            mob.apply_matrix(frame.get_inverse_camera_rotation_matrix())
            mob.fix_in_frame()
            mob.center()
        patch_copy2 = patch_copy.copy()

        prob = Group(*Tex(
            "P(", "0.", ")", "=", "{Num ", "\\over ", "Den}",
            font_size=60
        ))
        prob.fix_in_frame()
        prob.to_corner(UR)
        prob.shift(DOWN)
        for i, mob in [(1, patch_copy), (4, patch_copy2), (6, sphere_copy)]:
            mob.replace(prob[i], dim_to_match=1)
            prob.replace_submobject(i, mob)
        sphere_copy.scale(3, about_edge=UP)

        self.play(FadeIn(prob, lag_ratio=0.1))
        self.wait()
        for i in (4, 6):
            self.play(ShowCreationThenFadeOut(
                SurroundingRectangle(prob[i], stroke_width=2).fix_in_frame()
            ))
            self.wait()

        # Many patches
        patches = Group(
            get_patch(0.65, 0.5),
            get_patch(0.55, 0.8),
            get_patch(0.85, 0.8),
            get_patch(0.75, 0.4, 0.1, 0.2),
        )

        patch.deactivate_depth_test()
        self.add(sphere, patch)
        for new_patch in patches:
            self.play(
                Transform(patch, new_patch),
            )
            self.wait()

        # Non-specified orientation
        self.play(
            LaggedStart(*map(FadeOut, (sphere, sphere_mesh, patch, *prob, uniform_words)))
        )
        self.play(
            square.animate.set_fill(opacity=0.5),
            frame.animate.reorient(-30),
            run_time=3,
        )
        self.play(
            Rotate(square, TAU, normal_vect.get_vector()),
            run_time=8,
        )
        self.wait()

        # Show theta
        def get_normal():
            return normal_vect.get_vector()

        def get_theta():
            return np.arccos(get_normal()[2] / get_norm(get_normal()))

        def get_arc():
            result = Arc(PI / 2, -get_theta(), radius=0.25)
            result.rotate(PI / 2, RIGHT, about_point=ORIGIN)
            result.rotate(angle_of_vector([*get_normal()[:2], 0]), OUT, about_point=ORIGIN)
            result.shift(fc)
            result.set_stroke(WHITE, 1)
            result.apply_depth_test()
            return result

        arc = always_redraw(get_arc)

        theta = Tex("\\theta", font_size=20)
        theta.rotate(PI / 2, RIGHT)
        theta.set_backstroke(width=2)
        theta.add_updater(lambda m: m.next_to(arc.pfp(0.5), OUT + RIGHT, buff=0.05))

        z_axis = Line(ORIGIN, 10 * OUT)
        z_axis.set_stroke(WHITE, 1)
        z_axis.apply_depth_test()

        self.add(z_axis, face, theta, arc)
        self.play(
            ShowCreation(z_axis),
            ShowCreation(arc),
            FadeIn(theta, 0.5 * OUT),
        )
        self.wait()

        # Show shadow area
        #shadow_area = Text("Shadow area =", "$|\\cos(\\theta)|s^2$")
        shadow_area = Text("Shadow area =")
        shadow_area.fix_in_frame()
        shadow_area.to_edge(RIGHT)
        shadow_area.set_y(-3)
        shadow_area.set_backstroke()

        self.play(
            Write(shadow_area, run_time=3),
            Rotate(face, TAU, normal_vect.get_vector(), run_time=10),
        )
        self.wait(4)

        shadow_area[1].generate_target()
        shadow_area[1].target.to_corner(UR, buff=MED_LARGE_BUFF)
        shadow_area[1].target.shift(LEFT)
        brace = Brace(shadow_area[1].target, DOWN)
        brace_text = Text("How do you average this\\\\over the sphere?", font_size=36)
        brace_text.next_to(brace, DOWN, SMALL_BUFF)
        brace.fix_in_frame()
        brace_text.fix_in_frame()

        self.play(
            GrowFromCenter(brace),
            MoveToTarget(shadow_area[1]),
            FadeOut(shadow_area[0]),
            square.animate.set_fill(opacity=0),
        )
        face.generate_target()
        face.target[1].set_length(0.98, about_point=fc)
        sphere.set_opacity(0.35)
        sphere_mesh.set_stroke(width=0.5)
        self.play(
            MoveToTarget(face),
            FadeIn(brace_text, 0.5 * DOWN),
            Write(sphere_mesh, run_time=2, stroke_width=1),
            FadeIn(sphere),
        )

        # Sum expression
        def update_theta_ring(ring):
            theta = get_theta()
            phi = angle_of_vector([*get_normal()[:2], 0])
            ring.set_width(max(2 * 1.01 * math.sin(theta), 1e-3))
            ring.rotate(phi - angle_of_vector([*ring.get_start()[:2], 0]))
            ring.move_to(fc + math.cos(theta) * OUT)
            return ring

        theta_ring = Circle()
        theta_ring.set_stroke(YELLOW, 2)
        theta_ring.apply_depth_test()
        theta_ring.uniforms["anti_alias_width"] = 0

        loose_sum = Tex(
            "\\sum_{\\theta \\in [0, \\pi]}",
            "P(\\theta)",
            "\\cdot ",
            "|\\cos(\\theta)|s^2"
        )
        loose_sum.fix_in_frame()
        loose_sum.next_to(brace_text, DOWN, LARGE_BUFF)
        loose_sum.to_edge(RIGHT)
        prob_words = Text("How likely is a given value of $\\theta$?", font_size=36)
        prob_words.fix_in_frame()
        prob_words.next_to(loose_sum[1], DOWN)
        prob_words.to_edge(RIGHT, buff=MED_SMALL_BUFF)

        finite_words = Text("If finite...")
        finite_words.next_to(brace_text, DOWN, LARGE_BUFF).fix_in_frame()
        self.add(finite_words)
        face.rotate(-angle_of_vector([*get_normal()[:2], 0]))
        face.shift(fc - normal_vect.get_start())
        for d_theta in (*[-0.2] * 10, *[0.2] * 10):
            face.rotate(d_theta, np.cross(get_normal(), OUT), about_point=fc)
            self.wait(0.25)

        self.play(
            Write(loose_sum.get_part_by_tex("P(\\theta)")),
            FadeIn(prob_words, 0.5 * DOWN),
            FadeOut(finite_words),
            ApplyMethod(frame.set_x, 1, run_time=2)
        )
        update_theta_ring(theta_ring)
        self.add(theta_ring, sphere)
        self.play(
            Rotate(face, TAU, OUT, about_point=fc, run_time=4),
            ShowCreation(theta_ring, run_time=4),
        )
        theta_ring.add_updater(update_theta_ring)
        self.wait()
        self.play(
            FadeTransform(shadow_area[1].copy(), loose_sum.get_part_by_tex("cos")),
            Write(loose_sum.get_part_by_tex("\\cdot")),
            FadeOut(prob_words, 0.5 * DOWN)
        )
        self.wait(2)
        self.play(
            Write(loose_sum[0], run_time=2),
            run_time=3,
        )
        face.rotate(get_theta(), axis=np.cross(get_normal(), OUT), about_point=fc)
        for x in np.arange(0.2, PI, 0.2):
            face.rotate(0.2, UP, about_point=fc)
            self.wait(0.5)
        self.wait(5)

        # Continuous
        sum_brace = Brace(loose_sum[0], DOWN, buff=SMALL_BUFF)
        continuum = Text("Continuum\\\\(uncountably infinite)", font_size=36)
        continuum.next_to(sum_brace, DOWN, SMALL_BUFF)
        zero = Tex('0')
        zero.next_to(loose_sum[1], DOWN, buff=1.5)
        zero.shift(1.5 * RIGHT)
        zero_arrow = Arrow(loose_sum[1], zero, buff=SMALL_BUFF)
        nonsense_brace = Brace(loose_sum, UP)
        nonsense = nonsense_brace.get_text("Not really a sensible expression", font_size=36)

        for mob in [sum_brace, continuum, zero, zero_arrow, nonsense_brace, nonsense]:
            mob.fix_in_frame()
            mob.set_color(YELLOW)
        VGroup(nonsense_brace, nonsense).set_color(RED)

        face.start_time = self.time
        face.clear_updaters()
        face.add_updater(lambda f, dt: f.rotate(
            angle=0.25 * dt * math.cos(0.1 * (self.time - f.start_time)),
            axis=np.cross(get_normal(), OUT),
            about_point=fc,
        ).shift(fc - f[1].get_start()))

        self.play(
            GrowFromCenter(sum_brace),
            FadeIn(continuum, 0.5 * DOWN)
        )
        self.wait(4)
        self.play(
            ShowCreation(zero_arrow),
            GrowFromPoint(zero, zero_arrow.get_start()),
        )
        self.wait(2)
        inf_sum_group = VGroup(
            nonsense_brace, nonsense,
            sum_brace, continuum,
            zero_arrow, zero,
            loose_sum,
        )
        top_part = inf_sum_group[:2]
        top_part.set_opacity(0)
        self.play(
            inf_sum_group.animate.to_corner(UR),
            FadeOut(VGroup(brace, brace_text, shadow_area[1])),
            run_time=2,
        )
        top_part.set_fill(opacity=1)
        self.play(
            GrowFromCenter(nonsense_brace),
            Write(nonsense),
        )
        self.wait(10)

        # Swap for an integral
        integral = Tex(
            "\\int_0^\\pi ",
            "p(\\theta)",
            "\\cdot ",
            "|\\cos(\\theta)| s^2",
            "d\\theta",
        )
        integral.shift(loose_sum[-1].get_right() - integral[-1].get_right())
        integral.fix_in_frame()

        self.play(LaggedStart(*map(FadeOut, inf_sum_group[:-1])))
        self.play(
            TransformMatchingShapes(
                loose_sum[0], integral[0],
                fade_transform_mismatches=True,

            )
        )
        self.play(
            FadeTransformPieces(loose_sum[1:4], integral[1:4]),
            Write(integral[4])
        )
        self.wait(5)
        face.clear_updaters()
        self.wait(5)

        # Show 2d slice
        back_half_sphere = Sphere(u_range=(0, PI))
        back_half_sphere.match_color(sphere)
        back_half_sphere.set_opacity(sphere.get_opacity())
        back_half_sphere.shift(fc)
        back_half_mesh = SurfaceMesh(back_half_sphere, resolution=(11, 11))
        back_half_mesh.set_stroke(BLUE_D, 1, 0.75)

        circle = Circle()
        circle.set_stroke(TEAL, 1)
        circle.rotate(PI / 2, RIGHT)
        circle.move_to(fc)

        frame.clear_updaters()
        theta_ring.deactivate_depth_test()
        theta_ring.uniforms.pop("anti_alias_width")
        theta_ring.set_stroke(width=1)
        self.play(
            FadeOut(sphere),
            sphere_mesh.animate.set_stroke(opacity=0.25),
            FadeIn(circle),
            theta_ring.animate.set_stroke(width=1),
            frame.animate.reorient(-6, 87).set_height(4),
            integral.animate.set_height(0.5).set_opacity(0).to_corner(UR),
            run_time=2,
        )
        self.remove(integral)

        # Finite sample
        def get_tick_marks(theta_samples, tl=0.05):
            return VGroup(*(
                Line((1 - tl / 2) * p, (1 + tl / 2) * p).shift(fc)
                for theta in theta_samples
                for p in [np.array([math.sin(theta), 0, math.cos(theta)])]
            )).set_stroke(YELLOW, 1)

        factor = 1
        theta_samples = np.linspace(0, PI, factor * sphere_mesh.resolution[0])
        dtheta = theta_samples[1] - theta_samples[0]
        tick_marks = get_tick_marks(theta_samples)

        def set_theta(face, theta):
            face.apply_matrix(rotation_between_vectors(
                normal_vect.get_vector(), OUT
            ), about_point=fc)
            face.rotate(theta, UP, about_point=fc)

        self.play(
            ShowIncreasingSubsets(tick_marks[:-1]),
            UpdateFromAlphaFunc(
                face, lambda f, a: set_theta(face, theta_samples[int(a * (len(theta_samples) - 2))])
            ),
            run_time=4
        )
        self.add(tick_marks)
        self.wait(2)

        tsi = factor * 6  # theta sample index
        dt_line = Line(tick_marks[tsi].get_center(), tick_marks[tsi + 1].get_center())
        dt_brace = Brace(
            Line(ORIGIN, RIGHT), UP
        )
        dt_brace.scale(0.5)
        dt_brace.set_width(dt_line.get_length(), stretch=True)
        dt_brace.rotate(PI / 2, RIGHT)
        dt_brace.rotate(theta_samples[tsi], UP)
        dt_brace.move_to(dt_line)
        dt_brace.shift(SMALL_BUFF * normalize(dt_line.get_center() - fc))
        dt_label = Tex("\\Delta\\theta", font_size=24)
        dt_label.rotate(PI / 2, RIGHT)
        dt_label.next_to(dt_brace, OUT + RIGHT, buff=0.05)

        self.play(
            Write(dt_brace),
            Write(dt_label),
            run_time=1,
        )
        sphere.set_opacity(0.1)
        self.play(
            frame.animate.reorient(10, 70),
            Rotate(face, -get_theta() + theta_samples[tsi], UP, about_point=fc),
            sphere_mesh.animate.set_stroke(opacity=0.5),
            FadeIn(sphere),
            run_time=3
        )
        frame.add_updater(update_frame)
        self.wait()

        # Latitude band
        def get_band(index):
            band = Sphere(
                u_range=(0, TAU), v_range=theta_samples[index:index + 2],
                prefered_creation_axis=1,
            )
            band.set_color(YELLOW, 0.5)
            band.stretch(-1, 2, about_point=ORIGIN)
            band.shift(fc)
            return band

        band = get_band(tsi)

        self.add(band, sphere_mesh, sphere)
        self.play(
            ShowCreation(band),
            Rotate(face, dtheta, UP, about_point=fc),
            run_time=3,
        )
        self.play(Rotate(face, -dtheta, UP, about_point=fc), run_time=3)
        self.wait(2)

        area_question = Text("Area of this band?")
        area_question.set_color(YELLOW)
        area_question.fix_in_frame()
        area_question.set_y(1.75)
        area_question.to_edge(RIGHT, buff=2.5)
        self.play(Write(area_question))
        self.wait()

        random_points = [sphere.pfp(random.random()) - fc for x in range(30)]
        random_points.append(normal_vect.get_end() - fc)
        glow_dots = Group(*(TrueDot(p) for p in random_points))
        for dot in glow_dots:
            dot.shift(fc)
            dot.set_radius(0.2)
            dot.set_color(BLUE)
            dot.set_glow_factor(2)

        theta_ring.suspend_updating()
        last_dot = VectorizedPoint()
        for dot in glow_dots:
            face.apply_matrix(rotation_between_vectors(
                get_normal(), dot.get_center() - fc,
            ), about_point=fc)
            self.add(dot)
            self.play(FadeOut(last_dot), run_time=0.25)
            last_dot = dot
        self.play(FadeOut(last_dot))
        self.wait()

        # Find the area of the band
        frame.clear_updaters()
        self.play(
            frame.animate.reorient(-7.5, 78),
            sphere_mesh.animate.set_stroke(opacity=0.2),
            band.animate.set_opacity(0.2),
        )

        one = Tex("1", font_size=24)
        one.rotate(PI / 2, RIGHT)
        one.next_to(normal_vect.get_center(), IN + RIGHT, buff=0.05)
        radial_line = Line(
            [0, 0, normal_vect.get_end()[2]],
            normal_vect.get_end()
        )
        radial_line.set_stroke(BLUE, 2)
        r_label = Tex("r", font_size=20)
        sin_label = Tex("\\sin(\\theta)", font_size=16)
        for label in r_label, sin_label:
            label.rotate(PI / 2, RIGHT)
            label.next_to(radial_line, OUT, buff=0.05)
            label.set_color(BLUE)
            label.set_backstroke()

        self.play(Write(one))
        self.wait()
        self.play(
            TransformFromCopy(normal_vect, radial_line),
            FadeTransform(one.copy(), r_label)
        )
        self.wait()
        self.play(FadeTransform(r_label, sin_label))
        self.wait()

        band_area = Tex("2\\pi \\sin(\\theta)", "\\Delta\\theta")
        band_area.next_to(area_question, DOWN, LARGE_BUFF)
        band_area.set_backstroke()
        band_area.fix_in_frame()
        circ_label, dt_copy = band_area
        circ_brace = Brace(circ_label, DOWN, buff=SMALL_BUFF)
        circ_words = circ_brace.get_text("Circumference")
        approx = Tex("\\approx")
        approx.rotate(PI / 2)
        approx.move_to(midpoint(band_area.get_top(), area_question.get_bottom()))
        VGroup(circ_brace, circ_words, approx).set_backstroke().fix_in_frame()

        self.play(
            frame.animate.reorient(10, 60),
        )
        theta_ring.update()
        self.play(
            ShowCreation(theta_ring),
            Rotate(face, TAU, OUT, about_point=fc),
            FadeIn(circ_label, 0.5 * DOWN, rate_func=squish_rate_func(smooth, 0, 0.5)),
            GrowFromCenter(circ_brace),
            Write(circ_words),
            run_time=3,
        )
        self.wait()
        self.play(frame.animate.reorient(-5, 75))
        self.play(FadeTransform(area_question[-1], approx))
        area_question.remove(area_question[-1])
        self.play(Write(dt_copy))
        self.wait(3)

        # Probability of falling in band
        prob = Tex(
            "P(\\text{Vector} \\text{ in } \\text{Band})", "=",
            "{2\\pi \\sin(\\theta) \\Delta\\theta", "\\over", " 4\\pi}",
            tex_to_color_map={
                "\\text{Vector}": GREY_B,
                "\\text{Band}": YELLOW,
            }
        )
        prob.fix_in_frame()
        prob.to_edge(RIGHT)
        prob.set_y(1)
        prob.set_backstroke()
        numer = prob.get_part_by_tex("\\sin")
        numer_rect = SurroundingRectangle(numer, buff=0.05)
        numer_rect.set_stroke(YELLOW, 1)
        numer_rect.fix_in_frame()
        area_question.generate_target()
        area_question.target.match_width(numer_rect)
        area_question.target.next_to(numer_rect, UP, SMALL_BUFF)
        denom_rect = SurroundingRectangle(prob.get_part_by_tex("4\\pi"), buff=0.05)
        denom_rect.set_stroke(BLUE, 2)
        denom_rect.fix_in_frame()
        denom_label = Text("Surface area of\\\\a unit sphere")
        denom_label.scale(area_question.target[0].get_height() / denom_label[0][0].get_height())
        denom_label.set_color(BLUE)
        denom_label.next_to(denom_rect, DOWN, SMALL_BUFF)
        denom_label.fix_in_frame()

        i = prob.index_of_part_by_tex("sin")
        self.play(
            FadeTransform(band_area, prob.get_part_by_tex("sin"), remover=True),
            MoveToTarget(area_question),
            FadeIn(prob[:i]),
            FadeIn(prob[i + 1:]),
            FadeIn(numer_rect),
            *map(FadeOut, [approx, circ_brace, circ_words]),
            frame.animate.set_x(1.5),
        )
        self.add(prob)
        self.remove(band_area)
        self.wait()
        self.play(
            ShowCreation(denom_rect),
            FadeIn(denom_label, 0.5 * DOWN),
        )
        sc = sphere.copy().flip(UP).scale(1.01).set_color(BLUE, 0.5)
        self.add(sc, sphere_mesh)
        self.play(ShowCreation(sc), run_time=3)
        self.play(FadeOut(sc))
        self.wait()

        # Expression for average
        sphere_group = Group(
            sphere, sphere_mesh, theta_ring, band,
            circle, radial_line, sin_label, one, tick_marks,
            dt_brace, dt_label,
        )

        average_eq = Tex(
            "\\text{Average shadow} \\\\",
            "\\sum_{\\theta}",
            "{2\\pi", "\\sin(\\theta)", " \\Delta\\theta", "\\over", " 4\\pi}",
            "\\cdot", "|\\cos(\\theta)|", "s^2"
        )
        average_eq.fix_in_frame()
        average_eq.move_to(prob).to_edge(UP)
        average_eq[0].scale(1.25)
        average_eq[0].shift(MED_SMALL_BUFF * UP)
        average_eq[0].match_x(average_eq[1:])

        new_prob = average_eq[2:7]
        prob_rect = SurroundingRectangle(new_prob)
        prob_rect.set_stroke(YELLOW, 2)
        prob_rect.fix_in_frame()

        self.play(
            FadeIn(average_eq[:1]),
            FadeIn(prob_rect),
            prob[:5].animate.match_width(prob_rect).next_to(prob_rect, DOWN, buff=0.15),
            FadeTransform(prob[-3:], new_prob),
            *map(FadeOut, [prob[5], numer_rect, denom_rect, area_question, denom_label])
        )
        self.wait()
        self.play(
            FadeOut(sphere_group),
            FadeIn(average_eq[-3:]),
            UpdateFromAlphaFunc(face, lambda f, a: f[0].set_fill(opacity=0.5 * a))
        )
        self.wait()
        band.set_opacity(0.5)
        bands = Group(*(get_band(i) for i in range(len(theta_samples) - 1)))
        sphere_mesh.set_stroke(opacity=0.5)
        self.add(sphere_mesh, sphere, bands)
        self.play(
            FadeIn(average_eq[1]),
            UpdateFromAlphaFunc(face, lambda f, a: f[0].set_fill(opacity=0.5 * (1 - a))),
            FadeIn(sphere),
            FadeIn(tick_marks),
            FadeIn(sphere_mesh),
            LaggedStartMap(
                FadeIn, bands,
                rate_func=there_and_back,
                lag_ratio=0.5,
                run_time=8,
                remover=True
            ),
        )

        # Simplify
        average2 = Tex(
            "{2\\pi", "\\over", "4\\pi}", "s^2",
            "\\sum_{\\theta}",
            "\\sin(\\theta)", "\\Delta\\theta",
            "\\cdot", "|\\cos(\\theta)|"
        )
        average2.fix_in_frame()
        average2.move_to(average_eq[1:], RIGHT)
        half = Tex("1 \\over 2")
        pre_half = average2[:3]
        half.move_to(pre_half, RIGHT)
        half_rect = SurroundingRectangle(pre_half, buff=SMALL_BUFF)
        half_rect.set_stroke(RED, 1)
        VGroup(half, half_rect).fix_in_frame()

        self.play(
            FadeOut(prob_rect),
            FadeOut(prob[:5]),
            *(
                FadeTransform(average_eq[i], average2[j], path_arc=10 * DEGREES)
                for i, j in [
                    (1, 4),
                    (2, 0),
                    (3, 5),
                    (4, 6),
                    (5, 1),
                    (6, 2),
                    (7, 7),
                    (8, 8),
                    (9, 3),
                ]
            ),
            run_time=2,
        )
        self.play(ShowCreation(half_rect))
        self.play(
            FadeTransform(pre_half, half),
            FadeOut(half_rect),
        )
        sin, dt, dot, cos = average2[5:]
        tail = VGroup(cos, dot, sin, dt)
        tail.generate_target()
        tail.target.arrange(RIGHT, buff=SMALL_BUFF)
        tail.target.move_to(tail, LEFT)
        tail.target[-1].align_to(sin[0], DOWN)
        self.play(
            MoveToTarget(tail, path_arc=PI / 2),
        )
        self.wait(2)

        integral = Tex("\\int_0^\\pi ")
        integral.next_to(tail, LEFT, SMALL_BUFF)
        integral.fix_in_frame()
        dtheta = Tex("d\\theta").fix_in_frame()
        dtheta.move_to(tail[-1], LEFT)

        average_copy = VGroup(half, average2[3:]).copy()
        average_copy.set_backstroke()
        self.play(
            VGroup(half, average2[3]).animate.next_to(integral, LEFT, SMALL_BUFF),
            FadeTransform(average2[4], integral),
            FadeTransform(tail[-1], dtheta),
            average_copy.animate.shift(2.5 * DOWN),
            frame.animate.set_phi(80 * DEGREES),
        )
        self.wait()
        self.play(LaggedStart(
            ShowCreationThenFadeOut(SurroundingRectangle(average_copy[1][-3]).fix_in_frame()),
            ShowCreationThenFadeOut(SurroundingRectangle(dtheta).fix_in_frame()),
            lag_ratio=0.5
        ))
        self.wait()

        # The limit
        brace = Brace(average_copy, UP, buff=SMALL_BUFF)
        brace_text = brace.get_text(
            "What does this approach for finer subdivisions?",
            font_size=30
        )
        arrow = Arrow(integral.get_bottom(), brace_text)
        VGroup(brace, brace_text, arrow).set_color(YELLOW).fix_in_frame()
        brace_text.set_backstroke()

        self.play(
            GrowFromCenter(brace),
            ShowCreation(arrow),
            FadeIn(brace_text, lag_ratio=0.1)
        )

        for n in range(1, 4):
            new_ticks = get_tick_marks(
                np.linspace(0, PI, sphere_mesh.resolution[0] * 2**n),
                tl=0.05 / n
            )
            self.play(
                ShowCreation(new_ticks),
                FadeOut(tick_marks),
                run_time=2,
            )
            self.wait()
            tick_marks = new_ticks

        # Make room for computation
        face[0].set_fill(BLUE_D, opacity=0.75)
        face[0].set_stroke(WHITE, 0.5, 1)
        rect = Rectangle(fill_color=BLACK, fill_opacity=1, stroke_width=0)
        rect.replace(self.plane, stretch=True)
        rect.stretch(4 / 12, dim=0, about_edge=RIGHT)
        rect.scale(1.01)
        top_line = VGroup(half, average2[3], integral, tail[:-1], dtheta)
        self.add(face[0], sphere)
        self.play(
            LaggedStart(*map(FadeOut, [arrow, brace_text, brace, average_copy])),
            # UpdateFromAlphaFunc(face, lambda f, a: f[0].set_fill(opacity=0.5 * a)),
            GrowFromCenter(face[0], remover=True),
            frame.animate.set_height(6).set_x(3.5),
            FadeIn(rect),
            FadeOut(tick_marks),
            top_line.animate.set_width(4).to_edge(UP).to_edge(RIGHT, buff=LARGE_BUFF),
            FadeOut(average_eq[0], UP),
            run_time=2,
        )
        self.add(face, sphere)
        self.begin_ambient_rotation(face, about_point=fc, speed=0.1)

        # Computation
        new_lines = VGroup(
            Tex("{1 \\over 2} s^2 \\cdot 2 \\int_0^{\\pi / 2} \\cos(\\theta)\\sin(\\theta)\\,d\\theta"),
            Tex("{1 \\over 2} s^2 \\cdot \\int_0^{\\pi / 2} \\sin(2\\theta)\\,d\\theta"),
            Tex("{1 \\over 2} s^2 \\cdot \\left[ -\\frac{1}{2} \\cos(2\\theta) \\right]_0^{\\pi / 2}"),
            Tex("{1 \\over 2} s^2 \\cdot \\left(-\\left(-\\frac{1}{2}\\right) - \\left(-\\frac{1}{2}\\right)\\right)"),
            Tex("{1 \\over 2} s^2"),
        )
        new_lines.scale(top_line.get_height() / new_lines[0].get_height())
        kw = {"buff": 0.35, "aligned_edge": LEFT}
        new_lines.arrange(DOWN, **kw)
        new_lines.next_to(top_line, DOWN, **kw)
        new_lines.fix_in_frame()

        annotations = VGroup(
            Text("To avoid the annoying absolute value, just\\\\cover the northern hemisphere and double it."),
            Text("Trig identity: $\\sin(2\\theta) = 2\\cos(\\theta)\\sin(\\theta)$"),
            Text("Antiderivative"),
            Text("Try not to get lost in\\\\the sea of negatives..."),
            Text("Whoa, that turned out nice!"),
        )
        annotations.fix_in_frame()
        annotations.set_color(YELLOW)
        annotations.scale(0.5)

        rect = SurroundingRectangle(new_lines[-1], buff=SMALL_BUFF)
        rect.set_stroke(YELLOW, 2).fix_in_frame()

        for note, line in zip(annotations, new_lines):
            note.next_to(line, LEFT, MED_LARGE_BUFF)

        self.play(
            LaggedStartMap(FadeIn, new_lines, lag_ratio=0.7),
            LaggedStartMap(FadeIn, annotations, lag_ratio=0.7),
            run_time=5,
        )
        self.wait(20)
        self.play(
            new_lines[:-1].animate.set_opacity(0.5),
            annotations[:-1].animate.set_opacity(0.5),
            ShowCreation(rect),
        )
        self.wait(10)

    def get_solid(self):
        face = Square(side_length=2)
        face.set_fill(BLUE, 0.5)
        face.set_stroke(width=0)
        normal = Vector(OUT)
        normal.shift(2e-2 * OUT)
        face = VGroup(face, normal)
        face.set_stroke(background=True)
        face.apply_depth_test()
        return face
