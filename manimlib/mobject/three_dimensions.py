from __future__ import annotations

import math

from manimlib.constants import *
from manimlib.mobject.types.surface import Surface
from manimlib.mobject.types.surface import SGroup
from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.mobject.types.vectorized_mobject import VMobject
from manimlib.mobject.geometry import Square
from manimlib.mobject.geometry import Polygon
from manimlib.utils.bezier import interpolate
from manimlib.utils.config_ops import digest_config
from manimlib.utils.iterables import adjacent_pairs
from manimlib.utils.space_ops import get_norm
from manimlib.utils.space_ops import z_to_vector
from manimlib.utils.space_ops import compass_directions


class SurfaceMesh(VGroup):
    CONFIG = {
        "resolution": (21, 11),
        "stroke_width": 1,
        "normal_nudge": 1e-2,
        "depth_test": True,
        "flat_stroke": False,
    }

    def __init__(self, uv_surface: Surface, **kwargs):
        if not isinstance(uv_surface, Surface):
            raise Exception("uv_surface must be of type Surface")
        self.uv_surface = uv_surface
        super().__init__(**kwargs)

    def init_points(self) -> None:
        """
        对uv_surface的point进行采样
        """
        uv_surface = self.uv_surface

        # 曲面在u方向和v方向的采样点数
        full_nu, full_nv = uv_surface.resolution
        # mesh在u方向和v方向的采样点数
        part_nu, part_nv = self.resolution
        # 'indices' are treated as floats. Later, there will be
        # an interpolation between the floor and ceiling of these
        # indices
        """
        numpy.linspace(start, stop, num=50, endpoint=True, retstep=False, dtype=None, axis=0)
        在start和stop之间均匀采取num个值
        包含start和end
        """
        # (0, 100, 21)
        u_indices = np.linspace(0, full_nu - 1, part_nu)
        # (0, 50, 11)
        v_indices = np.linspace(0, full_nv - 1, part_nv)
        # print(u_indices, v_indices)
        # [  0.   5.  10.  15.  20.  25.  30.  35.  40.  45.  50.  55.  60.  65. 70.  75.  80.  85.  90.  95. 100.] 
        # [ 0.  5. 10. 15. 20. 25. 30. 35. 40. 45. 50.]

        points, du_points, dv_points = uv_surface.get_surface_points_and_nudged_points()
        #print(points.shape)
        normals = uv_surface.get_unit_normals()
        # nudge是什么？定义在类的CONFIG中
        nudge = self.normal_nudge
        # 给平面上每个点添加少许分割面的法向量。有什么用吗？
        nudged_points = points + nudge * normals

        for ui in u_indices:
            path = VMobject()
            low_ui = full_nv * int(math.floor(ui))
            high_ui = full_nv * int(math.ceil(ui))
            path.set_points_smoothly(interpolate(
                nudged_points[low_ui:low_ui + full_nv],
                nudged_points[high_ui:high_ui + full_nv],
                ui % 1
            ))
            self.add(path)
        # v_indices = [ 0.  5. 10. 15. 20. 25. 30. 35. 40. 45. 50.]
        # nudged_points: 5151列表（是101*51矩阵reshape而成，特别注意是一行一行的拼接）
        # nudged_points[0::51]对应于101*51矩阵的第0列数据
        # nudged_points[5::51]对应于101*51矩阵的第5列数据
        # 依此类推 
        for vi in v_indices:
            path = VMobject()
            path.set_points_smoothly(interpolate(
                nudged_points[int(math.floor(vi))::full_nv],
                nudged_points[int(math.ceil(vi))::full_nv],
                vi % 1
            ))
            self.add(path)


# 3D shapes

class Sphere(Surface):
    CONFIG = {
        "resolution": (101, 51),
        "radius": 1,
        "u_range": (0, TAU),
        "v_range": (0, PI),
    }

    """
    圆的参数方程：
    x = r * sin(v)* cos(u) 
    y = r * sin(v)* sin(u) 
    z = -r * cos(v)

    0 <= u <= 2π
    0 <= v <= π

    通过对u,v的遍历, 可以得到球体的点
    疑问: 给出几何体的参数方程后, manim是如何绘制的呢?
    """
    """
    曲面的参数方程完成的是(u, v)空间到(x, y, z)空间的映射
    是一个函数关系

    以球体为例
    在平面直角坐标系下, 球体的图像不是函数
    但是在球坐标系下, 球体的图像是函数

    """
    def uv_func(self, u: float, v: float) -> np.ndarray:
        return self.radius * np.array([
            np.cos(u) * np.sin(v),
            np.sin(u) * np.sin(v),
            -np.cos(v)
        ])


class Torus(Surface):
    CONFIG = {
        "u_range": (0, TAU),
        "v_range": (0, TAU),
        "r1": 3,
        "r2": 1,
    }

    def uv_func(self, u: float, v: float) -> np.ndarray:
        """
        尽管数学公式比较复杂
        但本质上仍然是(u, v) --> (x, y, z)
        两个空间的映射
        """
        P = np.array([math.cos(u), math.sin(u), 0])
        return (self.r1 - self.r2 * math.cos(v)) * P - math.sin(v) * OUT


class Cylinder(Surface):
    CONFIG = {
        "height": 2,
        "radius": 1,
        "axis": OUT,
        "u_range": (0, TAU),
        "v_range": (-1, 1),
        "resolution": (101, 11),
    }

    def init_points(self):
        super().init_points()
        self.scale(self.radius)
        self.set_depth(self.height, stretch=True)
        self.apply_matrix(z_to_vector(self.axis))
        return self

    def uv_func(self, u: float, v: float) -> np.ndarray:
        """
        柱坐标系下的(u, v) --> (x, y, z)空间映射
        """
        return np.array([np.cos(u), np.sin(u), v])


class Line3D(Cylinder):
    CONFIG = {
        "width": 0.05,
        "resolution": (21, 25)
    }

    def __init__(self, start: np.ndarray, end: np.ndarray, **kwargs):
        digest_config(self, kwargs)
        axis = end - start
        super().__init__(
            height=get_norm(axis),
            radius=self.width / 2,
            axis=axis
        )
        self.shift((start + end) / 2)


class Disk3D(Surface):
    CONFIG = {
        "radius": 1,
        "u_range": (0, 1),
        "v_range": (0, TAU),
        "resolution": (2, 25),
    }

    def init_points(self) -> None:
        super().init_points()
        self.scale(self.radius)

    def uv_func(self, u: float, v: float) -> np.ndarray:
        return np.array([
            u * np.cos(v),
            u * np.sin(v),
            0
        ])


class Square3D(Surface):
    CONFIG = {
        "side_length": 2,
        "u_range": (-1, 1),
        "v_range": (-1, 1),
        "resolution": (2, 2),
    }

    def init_points(self) -> None:
        super().init_points()
        self.scale(self.side_length / 2)

    def uv_func(self, u: float, v: float) -> np.ndarray:
        return np.array([u, v, 0])


class Cube(SGroup):
    CONFIG = {
        "color": BLUE,
        "opacity": 1,
        "gloss": 0.5,
        "square_resolution": (2, 2),
        "side_length": 2,
        "square_class": Square3D,
    }

    def init_points(self) -> None:
        face = Square3D(
            resolution=self.square_resolution,
            side_length=self.side_length,
        )
        self.add(*self.square_to_cube_faces(face))

    @staticmethod
    def square_to_cube_faces(square: Square3D) -> list[Square3D]:
        radius = square.get_height() / 2
        square.move_to(radius * OUT)
        result = [square]
        result.extend([
            square.copy().rotate(PI / 2, axis=vect, about_point=ORIGIN)
            for vect in compass_directions(4)
        ])
        result.append(square.copy().rotate(PI, RIGHT, about_point=ORIGIN))
        return result

    def _get_face(self) -> Square3D:
        return Square3D(resolution=self.square_resolution)


class Prism(Cube):
    def __init__(self, width: float = 3.0, height: float = 2.0, depth: float = 1.0, **kwargs):
        super().__init__(**kwargs)
        for dim, value in enumerate([width, height, depth]):
            self.rescale_to_fit(value, dim, stretch=True)


class VCube(VGroup):
    CONFIG = {
        "fill_color": BLUE_D,
        "fill_opacity": 1,
        "stroke_width": 0,
        "gloss": 0.5,
        "shadow": 0.5,
        "joint_type": "round",
    }

    def __init__(self, side_length: float = 2.0, **kwargs):
        face = Square(side_length=side_length)
        super().__init__(*Cube.square_to_cube_faces(face), **kwargs)
        self.init_colors()
        self.set_joint_type(self.joint_type)
        self.apply_depth_test()
        self.refresh_unit_normal()


class VPrism(VCube):
    def __init__(self, width: float = 3.0, height: float = 2.0, depth: float = 1.0, **kwargs):
        super().__init__(**kwargs)
        for dim, value in enumerate([width, height, depth]):
            self.rescale_to_fit(value, dim, stretch=True)


class Dodecahedron(VGroup):
    CONFIG = {
        "fill_color": BLUE_E,
        "fill_opacity": 1,
        "stroke_width": 1,
        "reflectiveness": 0.2,
        "gloss": 0.3,
        "shadow": 0.2,
        "depth_test": True,
    }

    def init_points(self) -> None:
        # Star by creating two of the pentagons, meeting
        # back to back on the positive x-axis
        phi = (1 + math.sqrt(5)) / 2
        x, y, z = np.identity(3)
        pentagon1 = Polygon(
            [phi, 1 / phi, 0],
            [1, 1, 1],
            [1 / phi, 0, phi],
            [1, -1, 1],
            [phi, -1 / phi, 0],
        )
        pentagon2 = pentagon1.copy().stretch(-1, 2, about_point=ORIGIN)
        pentagon2.reverse_points()
        x_pair = VGroup(pentagon1, pentagon2)
        z_pair = x_pair.copy().apply_matrix(np.array([z, -x, -y]).T)
        y_pair = x_pair.copy().apply_matrix(np.array([y, z, x]).T)

        self.add(*x_pair, *y_pair, *z_pair)
        for pentagon in list(self):
            pc = pentagon.copy()
            pc.apply_function(lambda p: -p)
            pc.reverse_points()
            self.add(pc)

        # # Rotate those two pentagons by all the axis permuations to fill
        # # out the dodecahedron
        # Id = np.identity(3)
        # for i in range(3):
        #     perm = [j % 3 for j in range(i, i + 3)]
        #     for b in [1, -1]:
        #         matrix = b * np.array([Id[0][perm], Id[1][perm], Id[2][perm]])
        #         self.add(pentagon1.copy().apply_matrix(matrix, about_point=ORIGIN))
        #         self.add(pentagon2.copy().apply_matrix(matrix, about_point=ORIGIN))


class Prismify(VGroup):
    CONFIG = {
        "apply_depth_test": True,
    }

    def __init__(self, vmobject, depth=1.0, direction=IN, **kwargs):
        # At the moment, this assume stright edges
        super().__init__(**kwargs)
        vect = depth * direction
        self.add(vmobject.copy())
        points = vmobject.get_points()[::vmobject.n_points_per_curve]
        for p1, p2 in adjacent_pairs(points):
            wall = VMobject()
            wall.match_style(vmobject)
            wall.set_points_as_corners([p1, p2, p2 + vect, p1 + vect])
            self.add(wall)
        self.add(vmobject.copy().shift(vect).reverse_points())
