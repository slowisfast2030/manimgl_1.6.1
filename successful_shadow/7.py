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
    return 0.5 * sum(
        get_norm(sm.get_area_vector())
        for sm in shadow.get_family()
    )


def get_convex_hull(mobject):
    points = mobject.get_all_points()
    hull = scipy.spatial.ConvexHull(points[:, :2])
    return points[hull.vertices]


def sort_to_camera(mobject, camera_frame):
    cl = camera_frame.get_implied_camera_location()
    mobject.sort(lambda p: -get_norm(p - cl))
    return mobject


def cube_sdf(point, cube):
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


class IntroduceShadow(ShadowScene):
    area_label_center = [-2.5, -2, 0]
    plane_dims = (28, 20)

    def construct(self):
        # Setup
        light = self.light
        light.move_to([0, 0, 20])
        self.add(light)
        cube = self.solid
        cube.scale(0.945)  # Hack to make the appropriate area 1
        shadow = self.shadow
        outline = self.get_shadow_outline()
        frame = self.camera.frame
        frame.add_updater(lambda f, dt: f.increment_theta(0.01 * dt))  # Ambient rotation
        area_label = self.get_shadow_area_label()
        light_lines = self.get_light_lines(outline)

        # Question
        question = Text(
            "Puzzle: Find the average area of a cube's shadow",
            font_size=48,
        )
        question.to_corner(UL)
        question.fix_in_frame()
        subquestion = Text("(Averaged over all orientations)")
        subquestion.match_width(question)
        subquestion.next_to(question, DOWN, MED_LARGE_BUFF)
        subquestion.set_fill(BLUE_D)
        subquestion.fix_in_frame()
        subquestion.set_backstroke()

        # Introductory animations
        self.shadow.update()
        self.play(
            FadeIn(question, UP),
            *(
                LaggedStartMap(DrawBorderThenFill, mob, lag_ratio=0.1, run_time=3)
                for mob in (cube, shadow)
            )
        )
        self.random_toss(run_time=3, angle=TAU)

        # Change size and orientation
        outline.update()
        area_label.update()
        self.play(
            FadeIn(area_label),
            ShowCreation(outline),
        )
        self.play(
            cube.animate.scale(0.5),
            run_time=2,
            rate_func=there_and_back,
        )
        self.random_toss(run_time=2, angle=PI)
        self.wait()
        self.begin_ambient_rotation(cube)
        self.play(FadeIn(subquestion, 0.5 * DOWN))
        self.wait(7)

        # Where is the light?
        light_comment = Text("Where is the light?")
        light_comment.set_color(YELLOW)
        light_comment.to_corner(UR)
        light_comment.set_backstroke()
        light_comment.fix_in_frame()

        cube.clear_updaters()
        cube.add_updater(lambda m: self.sort_to_camera(cube))
        self.play(
            FadeIn(light_comment, 0.5 * UP),
            light.animate.next_to(cube, OUT, buff=1.5),
            run_time=2,
        )
        light_lines.update()
        self.play(
            ShowCreation(light_lines, lag_ratio=0.01, run_time=3),
        )
        self.play(
            light.animate.shift(1.0 * IN),
            rate_func=there_and_back,
            run_time=3
        )
        self.play(
            light.animate.shift(4 * RIGHT),
            run_time=5
        )
        self.play(
            Rotate(light, PI, about_point=light.get_z() * OUT),
            run_time=8,
        )
        self.play(light.animate.shift(4 * RIGHT), run_time=5)
        self.wait()

        # Light straight above
        self.play(
            frame.animate.set_height(12).set_z(4),
            light.animate.set_z(10),
            run_time=3,
        )
        self.wait()
        self.play(light.animate.move_to(75 * OUT), run_time=3)
        self.wait()
        self.play(
            frame.animate.set_height(8).set_z(2),
            LaggedStart(*map(FadeOut, (question, subquestion, light_comment))),
            run_time=2
        )

        # Flat projection
        verts = np.array([*cube[0].get_vertices(), *cube[5].get_vertices()])
        vert_dots = DotCloud(verts)
        vert_dots.set_glow_factor(0.5)
        vert_dots.set_color(WHITE)
        proj_dots = vert_dots.copy()
        proj_dots.apply_function(flat_project)
        proj_dots.set_color(GREY_B)
        vert_proj_lines = VGroup(*(
            DashedLine(*pair)
            for pair in zip(verts, proj_dots.get_points())
        ))
        vert_proj_lines.set_stroke(WHITE, 1, 0.5)

        point = verts[np.argmax(verts[:, 0])]
        xyz_label = Tex("(x, y, z)")
        xy0_label = Tex("(x, y, 0)")
        for label in xyz_label, xy0_label:
            label.rotate(PI / 2, RIGHT)
            label.set_backstroke()
        xyz_label.next_to(point, RIGHT)
        xy0_label.next_to(flat_project(point), RIGHT)

        vert_dots.save_state()
        vert_dots.set_glow_factor(5)
        vert_dots.set_radius(0.5)
        vert_dots.set_opacity(0)
        self.play(
            Restore(vert_dots),
            Write(xyz_label),
        )
        self.wait()
        self.play(
            TransformFromCopy(
                cube.deepcopy().clear_updaters().set_opacity(0.5),
                shadow.deepcopy().clear_updaters().set_opacity(0),
                remover=True
            ),
            TransformFromCopy(vert_dots, proj_dots),
            TransformFromCopy(xyz_label, xy0_label),
            *map(ShowCreation, vert_proj_lines),
        )
        self.wait(3)
        self.play(LaggedStart(*map(FadeOut, (
            vert_dots, vert_proj_lines, proj_dots,
            xyz_label, xy0_label
        ))))

        # Square projection
        top_face = cube[np.argmax([f.get_z() for f in cube])]
        normal_vect = top_face.get_unit_normal()
        theta = np.arccos(normal_vect[2])
        axis = normalize(rotate_vector([*normal_vect[:2], 0], PI / 2, OUT))

        self.play(Rotate(cube, -theta, axis))
        top_face = cube[np.argmax([f.get_z() for f in cube])]
        verts = top_face.get_vertices()
        vect = verts[3] - verts[2]
        angle = angle_of_vector(vect)
        self.play(Rotate(cube, -angle, OUT))
        self.wait()

        corner = cube.get_corner(DL + OUT)
        edge_lines = VGroup(
            Line(corner, cube.get_corner(DR + OUT)),
            Line(corner, cube.get_corner(UL + OUT)),
            Line(corner, cube.get_corner(DL + IN)),
        )
        edge_lines.set_stroke(RED, 2)
        s_labels = Tex("s").replicate(3)
        s_labels.set_color(RED)
        s_labels.rotate(PI / 2, RIGHT)
        s_labels.set_stroke(BLACK, 3, background=True)
        for label, line, vect in zip(s_labels, edge_lines, [OUT, LEFT, LEFT]):
            label.next_to(line, vect, buff=SMALL_BUFF)
        s_labels[1].next_to(edge_lines[1], OUT)
        s_labels[2].next_to(edge_lines[2], LEFT)

        s_squared = Tex("s^2")
        s_squared.match_style(s_labels[0])
        s_squared.move_to(self.shadow)

        frame.generate_target()
        frame.target.reorient(10, 60)
        frame.target.set_height(6.5)

        self.play(
            LaggedStartMap(ShowCreation, edge_lines),
            LaggedStartMap(FadeIn, s_labels, scale=2),
            MoveToTarget(frame, run_time=3)
        )
        self.wait()
        self.play(
            TransformFromCopy(s_labels[:2], s_squared),
        )
        self.wait(2)

        rect = SurroundingRectangle(area_label)
        rect.fix_in_frame()
        rect.set_stroke(YELLOW, 3)
        s_eq = Tex("s = 1")
        s_eq.next_to(area_label, DOWN)
        s_eq.set_color(RED)
        s_eq.set_stroke(BLACK, 3, background=True)
        s_eq.fix_in_frame()

        self.play(ShowCreation(rect))
        self.play(FadeIn(s_eq, 0.5 * DOWN))
        self.wait()
        self.play(LaggedStart(*map(FadeOut, (
            rect, s_eq, *edge_lines, *s_labels, s_squared,
        ))))
        self.wait()

        # Hexagonal orientation
        axis = UL
        angle = np.arccos(1 / math.sqrt(3))
        area_label.suspend_updating()
        self.play(
            Rotate(cube, -angle, axis),
            frame.animate.reorient(-10, 70),
            ChangeDecimalToValue(area_label[1], math.sqrt(3)),
            UpdateFromFunc(area_label[1], lambda m: m.fix_in_frame()),
            run_time=2
        )
        self.add(area_label)

        diagonal = Line(cube.get_nadir(), cube.get_zenith())
        diagonal.set_stroke(WHITE, 2)
        diagonal.scale(2)
        diagonal.move_to(ORIGIN, IN)
        self.add(diagonal, cube)
        self.play(ShowCreation(diagonal))

        self.wait(2)
        frame.save_state()
        cube_opacity = cube[0].get_fill_opacity()
        cube.save_state()
        angle = angle_of_vector(outline.get_anchors()[-1] - outline.get_anchors()[-2])
        self.play(
            frame.animate.reorient(0, 0),
            cube.animate.rotate(-angle).set_opacity(0.2),
            run_time=3,
        )
        frame.suspend_updating()
        outline_copy = outline.copy().clear_updaters()
        outline_copy.set_stroke(RED, 5)
        title = Text("Regular hexagon")
        title.set_color(RED)
        title.next_to(outline_copy, UP)
        title.set_backstroke()
        self.play(
            ShowCreationThenFadeOut(outline_copy),
            Write(title, run_time=1),
        )
        self.play(
            FadeOut(title),
            Restore(frame),
            cube.animate.set_opacity(cube_opacity).rotate(angle),
            run_time=3,
        )
        frame.resume_updating()

        hex_area_label = Tex("\\sqrt{3} s^2")
        hex_area_label.set_color(RED)
        hex_area_label.move_to(self.shadow)
        hex_area_label.shift(0.35 * DOWN)
        self.play(Write(hex_area_label))
        self.wait(10)
        area_label.resume_updating()
        self.play(
            Uncreate(diagonal),
            FadeOut(hex_area_label),
            Rotate(cube, 4, RIGHT)
        )

        # Talk about averages
        light_lines.clear_updaters()
        self.begin_ambient_rotation(cube)
        self.play(
            FadeOut(light_lines),
            FadeIn(question, 0.5 * UP),
            ApplyMethod(frame.set_height, 8, run_time=2)
        )
        self.play(FadeIn(subquestion, 0.5 * UP))
        self.wait(7)

        cube.clear_updaters()
        cube.add_updater(lambda m: self.sort_to_camera(m))
        samples = VGroup(VectorizedPoint())
        samples.to_corner(UR)
        samples.shift(1.5 * LEFT)
        self.add(samples)
        for x in range(9):
            self.random_toss()
            sample = area_label[1].copy()
            sample.clear_updaters()
            sample.fix_in_frame()
            self.play(
                sample.animate.next_to(samples, DOWN),
                run_time=0.5
            )
            samples.add(sample)

        v_dots = Tex("\\vdots")
        v_dots.next_to(samples, DOWN)
        v_dots.fix_in_frame()
        samples.add(v_dots)
        brace = Brace(samples, LEFT)
        brace.fix_in_frame()
        brace.next_to(samples, LEFT, SMALL_BUFF)
        text = TexText(
            "Take the mean.", "\\\\What does that\\\\approach?",
            font_size=30
        )
        text[0].shift(MED_SMALL_BUFF * UP)
        text.next_to(brace, LEFT)
        text.fix_in_frame()
        VGroup(text, brace).set_stroke(BLACK, 3, background=True)

        self.play(
            GrowFromCenter(brace),
            FadeIn(text),
            Write(v_dots),
        )
        self.wait()

        for x in range(10):
            self.random_toss()
            self.wait()