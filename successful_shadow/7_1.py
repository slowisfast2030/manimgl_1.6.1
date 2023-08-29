from manimlib import *
import scipy.spatial


"""
黑箱学习法：对于一个函数，只关心输入和输出，不关心内部的实现细节

很困惑light_source和self.light是不是一个对象
根据黑箱学习法, 这个不是重点
从效果上看,light_source和self.light是同一个对象
"""
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
    随着mobject和light_source的变化
    更新shadow的属性(主要是形状)
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
    # 注意，这里的shadow并不是mobject的投影
    # get_pre_shadow()函数的参数都没有光源，压根不能计算阴影
    shadow = get_pre_shadow(mobject, opacity)
    """
    updater的本质:
    每一帧都会调用update_shadow(s, mobject, light_source)函数
    调用的结果是会更新shadow的属性
    比较明显的是location
    比较隐晦的是points set(shape)
    """
    """
    为了在一开始的时候就获得正确的shadow
    因为已经为shadow添加了updater
    可以主动执行一次updater: shadow.update()
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
    # 无穷远光源
    inf_light = False
    glow_radius = 10
    glow_factor = 10
    area_label_center = [-2, -1, 0]
    unit_size = 2

    def setup(self):
        # 改变了相机的欧拉角
        self.camera.frame.reorient(-30, 75)
        # 困惑: 这里的效果应该是改变了相机的位置
        # 改变了欧拉角的相机，空间位置应该也发生了变化
        # 但这里的frame_center是[0, 0, 2]？
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
        # 问题：这里的light_source和self.light是不是一个对象，只是有不同的别名？
        # 应该是同一个对象，否则shadow随着self.light的变化而变化就讲不通
        # 如何测试自己的想法呢？很简单，注释掉下一行，执行light_source = self.light
        # 不够需要注意，在add_shadow函数执行的时候还没有self.light属性
        # 需要将setup_light_source函数提前执行
        light_source = None if self.inf_light else self.camera.light_source
        shadow = get_shadow(self.solid, light_source)

        self.add(shadow, self.solid)
        self.shadow = shadow

    def setup_light_source(self):
        # 这里的self.light是一个Dot
        self.light = self.camera.light_source
        if self.inf_light:
            self.light.move_to(100 * OUT)
        else:
            # glow是一个TrueDot（点云）
            glow = self.glow = TrueDot(
                radius=self.glow_radius,
                glow_factor=self.glow_factor,
            )
            # 这里的颜色竟然用了插值
            glow.set_color(interpolate_color(YELLOW, WHITE, 0.5))
            # 这里给glow添加了一个updater，暗示self.light的位置会发生变化（animation）
            glow.add_updater(lambda m: m.move_to(self.light))
            self.add(glow)

    def sort_to_camera(self, mobject):
        return sort_to_camera(mobject, self.camera.frame)

    def get_shadow_area_label(self):
        text = Text("Shadow area: ")
        """
        一开始随便付一个值
        添加了updater之后, 主动调用一次updater
        """
        decimal = DecimalNumber(100)

        label = VGroup(text, decimal)
        label.arrange(RIGHT)
        label.move_to(self.area_label_center - decimal.get_center())
        label.fix_in_frame()
        # 下面这行要是注释掉, plane上会投影出数字的阴影，很奇怪
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
        """
        启发：
        1.我们知道shadow的outline是一个VMobject, 随着shadow的变化而变化
        那么在初始化outline的时候, 只需要将outline设置为空的VMobject即可
        紧接着, 为outline添加一个updater, 这个updater的作用是将outline的形状设置为shadow的凸包
        可以试想下, 我们确实可以在添加updater之前就将outline的形状设置为shadow的凸包
        但是, 接下来的add_updater函数又会再一遍执行类似的操作, 代码上很冗余

        2.self.shadow是xoy平面的一个多边形, 为了获取shadow的outline, 我们可以自己写函数
        但是, 作者很善于使用开源库, 这里使用了scipy.spatial.ConvexHull
        这种意识真牛逼
        """
        outline = VMobject()
        outline.set_stroke(WHITE, stroke_width)
        outline.add_updater(lambda m: m.set_points_as_corners(get_convex_hull(self.shadow)).close_path())
        return outline

    def get_light_lines(self, outline=None, n_lines=1000, only_vertices=False):
        if outline is None:
            outline = self.get_shadow_outline()

        def update_lines(lines):
            lp = self.light.get_center()
            if only_vertices:
                points = outline.get_vertices()
            else:
                # 在outline上均匀取n_lines个点
                points = [outline.pfp(a) for a in np.linspace(0, 1, n_lines)]
            # 深度思考：这里的line是lines里对象的别名
            for line, point in zip(lines, points):
                if self.inf_light:
                    line.set_points_as_corners([point + 10 * OUT, point])
                else:
                    # 将line的起点设置为lp, 终点设置为point
                    line.set_points_as_corners([lp, point])

        line = Line(IN, OUT)
        # 这里的light_lines一开始并没有设置合适的初值
        # 为了获得合适的初值, 需要主动执行一次updater
        # 感觉这几乎成为了一个惯例
        light_lines = line.replicate(n_lines)
        light_lines.set_stroke(YELLOW, 0.5, 0.1)
        light_lines.add_updater(update_lines)
        return light_lines

    def random_toss(self, mobject=None, angle=TAU, about_point=None, meta_speed=5, **kwargs):
        """
        随机投掷mobject
        """
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

    # 没用到这个函数
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


class test2(ShadowScene):
    area_label_center = [-2.5, -2, 0]
    plane_dims = (28, 20)

    def construct(self):
        # Setup
        # light是一个点，没有视觉效果。glow是点云，有视觉效果
        # glow和light的位置进行了绑定。移动light，glow也会移动
        light = self.light
        light.move_to([0, 0, 20])
        self.add(light)
        cube = self.solid
        cube.scale(0.945)  # Hack to make the appropriate area 1
        shadow = self.shadow
        outline = self.get_shadow_outline()
        """
        这里需要特别注意, 再一次获取了self.camera.frame
        在setup函数中, 已经获取了self.camera.frame, 并且设置了欧拉角和location
        这里需要区分python中对象和别名的概念
        """
        frame = self.camera.frame
        # 为frame添加updater, 因为增加的theta比较小，所以看上去不明显。但这么做我觉得很有必要，否则画面太呆板
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
        question.set_backstroke() # 添加这一行, 似乎没什么特别明显的效果。3b1b很喜欢为文字添加这种效果
        subquestion = Text("(Averaged over all orientations)")
        subquestion.match_width(question)
        subquestion.next_to(question, DOWN, MED_LARGE_BUFF)
        subquestion.set_fill(BLUE_D)
        subquestion.fix_in_frame()
        # 好像字体的边框颜色靠后一点
        subquestion.set_backstroke()

        # Introductory animations
        # 疑问：整个场景一开始只有一个plane，然而之前已经添加了cube和shadow，为何一开始不显示呢
        # cube和shadow是以下面动画的形式添加到场景中的
        
        # 这一行如果注释掉，一开始的阴影会有一些奇怪的效果
        self.shadow.update() # 更新shadow的形状。一开始的shadow并不是cube的投影
        self.play(
            FadeIn(question, UP),
            *(
                LaggedStartMap(DrawBorderThenFill, mob, lag_ratio=0.1, run_time=3)
                for mob in (cube, shadow)
            )
        )
        self.random_toss(run_time=3, angle=TAU)

        # Change size and orientation
        """
        outline和area_label都添加了updater
        outline和area_label的初始值都是错误的
        需要主动执行一次updater, 以获得正确的初始值
        """
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
        # 下面这一行干嘛的？
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