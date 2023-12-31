from __future__ import annotations

from typing import Iterable, Callable

import moderngl
import numpy as np
import numpy.typing as npt

from manimlib.constants import *
from manimlib.mobject.mobject import Mobject
from manimlib.utils.bezier import integer_interpolate
from manimlib.utils.bezier import interpolate
from manimlib.utils.images import get_full_raster_image_path
from manimlib.utils.iterables import listify
from manimlib.utils.space_ops import normalize_along_axis

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from manimlib.camera.camera import Camera


class Surface(Mobject):
    CONFIG = {
        "u_range": (0, 1),
        "v_range": (0, 1),
        # Resolution counts number of points sampled, which for
        # each coordinate is one more than the the number of
        # rows/columns of approximating squares
        "resolution": (101, 101),
        "color": GREY,
        "opacity": 1.0,
        "reflectiveness": 0.3,
        "gloss": 0.1,
        "shadow": 0.4,
        "prefered_creation_axis": 1,
        # For du and dv steps.  Much smaller and numerical error
        # can crop up in the shaders.
        "epsilon": 1e-5,
        "render_primitive": moderngl.TRIANGLES,
        "depth_test": True,
        "shader_folder": "surface", # 原来在这里，指定了着色器文件夹
        "shader_dtype": [
            ('point', np.float32, (3,)),
            ('du_point', np.float32, (3,)),
            ('dv_point', np.float32, (3,)),
            ('color', np.float32, (4,)),
        ]
    }
    """
    Depth test is a technique that determines which fragments are visible and 
    which are occluded by other objects in a 3D scene. It uses a depth buffer, 
    which is an image that stores the depth values of each fragment, to compare 
    the depth of a fragment with the existing depth at the same pixel location. 
    If the fragment is closer to the camera than the previous fragment, it passes 
    the depth test and is rendered; otherwise, it is discarded and not rendered.

    It ensures that only the closest visible objects are rendered on the screen, 
    simulating the occlusion that occurs in the real world.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 和着色器有关
        self.compute_triangle_indices()

    def uv_func(self, u: float, v: float) -> tuple[float, float, float]:
        # To be implemented in subclasses
        """
        完成(u, v) --> (x, y, z)空间变换

        (x, y, z)世界坐标系
        """
        return (u, v, 0.0)

    def init_points_linus(self):
        """
        效果很差
        这里改了points的规模, 以前是3*nu*nv
        为了达到理想的效果, 需要进一步修改compute_triangle_indices函数
        """
        nu, nv = self.resolution

        u_range = np.linspace(*self.u_range, nu)
        v_range = np.linspace(*self.v_range, nv)

        all_points = []
        uv_grid_filter = []
        
        uv_grid = np.array([[[u, v] for v in v_range] for u in u_range])
        for i in range(len(uv_grid)):
            for j in range(len(uv_grid[i])):
                u = uv_grid[i][j][0]
                v = uv_grid[i][j][1]
                if u - v <= 2:
                    uv_grid_filter.append([u, v])

        du = self.epsilon
        dv = self.epsilon
        for point in uv_grid_filter:
            u, v = point
            all_points.append(self.uv_func(u, v))
            all_points.append(self.uv_func(u+du, v))
            all_points.append(self.uv_func(u, v+dv))

        self.set_points(all_points)

    def init_points_turing(self):
        """
        def uv_func(u: float, v: float) -> np.ndarray:
            return np.array([
                u,
                v,
                2-u+v if u-v <=2 else 0
            ])

        只画出三角形范围
        """
        dim = self.dim
        nu, nv = self.resolution

        u_range = np.linspace(*self.u_range, nu)
        v_range = np.linspace(*self.v_range, nv)

        point_lists = []
        for (du, dv) in [(0, 0), (self.epsilon, 0), (0, self.epsilon)]:
            
            # uv_grid是一个矩形的范围，可以修改成三角形范围
            uv_grid = np.array([[[u + du, v + dv] for v in v_range] for u in u_range])
            for i in range(len(uv_grid)):
                for j in range(len(uv_grid[i])):
                    u = uv_grid[i][j][0]
                    v = uv_grid[i][j][1]
                    if u - v > 2:
                        # 思想: 将直线y = x - 2下方的点映射到直线的对称位置
                        # 这样就可以不用修改triangle_indices了
                        # 效果不错。边缘有微小锯齿感，可以通过提高resolution解决
                        uv_grid[i][j] = uv_grid[j][i] 
                        # 下面是最原始的思路，效果比较差
                        #uv_grid[i][j] = (0, 0)

            point_grid = np.apply_along_axis(lambda p: self.uv_func(*p), 2, uv_grid)

            point_lists.append(point_grid.reshape((nu * nv, dim)))
            
        self.set_points(np.vstack(point_lists))

    def init_points(self):
        dim = self.dim
        # 对于sphere的默认配置nu, nv = (101, 51)
        # 疑问：为何将nu和nv都设置为奇数？
        nu, nv = self.resolution
        #print(nu, nv)

        # 在u_range = [start, end]范围内，等间隔抽取nu个点，包含start和end
        u_range = np.linspace(*self.u_range, nu)
        # 在v_range = [start, end]范围内，等间隔抽取nv个点，包含start和end
        v_range = np.linspace(*self.v_range, nv)

        # Get three lists:
        # - Points generated by pure uv values
        # - Those generated by values nudged by du
        # - Those generated by values nudged by dv
        point_lists = []
        for (du, dv) in [(0, 0), (self.epsilon, 0), (0, self.epsilon)]:
            # u_range是101个数，v_range是51个数
            # uv_grid的大小就是101*51
            uv_grid = np.array([[[u + du, v + dv] for v in v_range] for u in u_range])
            # print(len(uv_grid))       # 101
            # print(len(uv_grid[0]))    # 51
            # print(len(uv_grid[0][0])) # 2
            
            # uv_grid是一个矩形的范围，可以修改成三角形范围。有锯齿
            # uv_grid = np.array([[[u + du, v + dv] for v in v_range] for u in u_range])
            # for i in range(len(uv_grid)):
            #     for j in range(len(uv_grid[i])):
            #         u = uv_grid[i][j][0]
            #         v = uv_grid[i][j][1]
            #         if u - v > 2:
            #             uv_grid[i][j] = [1,-1]

            # 对uv_grid矩阵中的每一个二维点进行uv_func运算，得到对应的三维点
            point_grid = np.apply_along_axis(lambda p: self.uv_func(*p), 2, uv_grid)
            # print(len(point_grid))       # 101
            # print(len(point_grid[0]))    # 51
            # print(len(point_grid[0][0])) # 3

            # 将二维矩阵压缩成列表
            # 可视化想象: 以前101*51的矩阵，现在5151的列表
            # for循环结束后，point_lists中是3个5151的列表
            point_lists.append(point_grid.reshape((nu * nv, dim)))
            
        # Rather than tracking normal vectors, the points list will hold on to the
        # infinitesimal nudged values alongside the original values.  This way, one
        # can perform all the manipulations they'd like to the surface, and normals
        # are still easily recoverable.
        self.set_points(np.vstack(point_lists))

    def compute_triangle_indices(self):
        # TODO, if there is an event which changes
        # the resolution of the surface, make sure
        # this is called.
        """
        效果同三角剖分
        """
        """
        目前manim所支持的surface的(u, v)空间是一个矩形空间
        比如:
        Surface
        "u_range": (0, 1),
        "v_range": (0, 1),

        Sphere
        "u_range": (0, TAU),
        "v_range": (0, PI),

        Torus
        "u_range": (0, TAU),
        "v_range": (0, TAU),

        Cylinder
        "u_range": (0, TAU),
        "v_range": (-1, 1),

        如果想把(u, v)空间修改成任意形状，比如三角形
        需要对这个函数进行修改。修改不容易啊        
        """
        nu, nv = self.resolution
        #print(nu, nv)
        if nu == 0 or nv == 0:
            self.triangle_indices = np.zeros(0, dtype=int)
            return
        """
        array([[   0,    1,    2, ...,   48,   49,   50],
               [  51,   52,   53, ...,   99,  100,  101],
               [ 102,  103,  104, ...,  150,  151,  152],
               ...,
               [4998, 4999, 5000, ..., 5046, 5047, 5048],
               [5049, 5050, 5051, ..., 5097, 5098, 5099],
               [5100, 5101, 5102, ..., 5148, 5149, 5150]])
        
        如何理解这个index_grid?

        我们在u和v方向分别采样了101和51次, 得到一个101*51的矩阵(忽略du_points和dv_points)
        这个index_grid就是和上述矩阵同等规模的编号矩阵(给每一个元素加了编号)

        这里给出indices[:18]
        array([ 0, 51,  1,  1, 51, 52,  1, 52,  2,  2, 52, 53,  2, 53,  3,  3, 53, 54])

        可以发现(0, 51, 1), (1, 51, 52)等就是三角形的顶点索引
        """
        index_grid = np.arange(nu * nv).reshape((nu, nv))
        """
        6*100*50 = 30000个零

        indices为何是30000的大小?
        因为对上述的index_grid可以采样100*50*2的三角形
        每个三角形3个顶点, 需要3个索引
        """
        indices = np.zeros(6 * (nu - 1) * (nv - 1), dtype=int)
        indices[0::6] = index_grid[:-1, :-1].flatten()  # Top left
        indices[1::6] = index_grid[+1:, :-1].flatten()  # Bottom left
        indices[2::6] = index_grid[:-1, +1:].flatten()  # Top right
        indices[3::6] = index_grid[:-1, +1:].flatten()  # Top right
        indices[4::6] = index_grid[+1:, :-1].flatten()  # Bottom left
        indices[5::6] = index_grid[+1:, +1:].flatten()  # Bottom right
        self.triangle_indices = indices

    def get_triangle_indices(self) -> np.ndarray:
        return self.triangle_indices

    def get_surface_points_and_nudged_points(
        self
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        在init_points方法中可以看到
        前1/3是平面上的点
        后2/3是辅助的点

        一个平面点 + 两个辅助点 = 三角面
        可以用来确定每一个分割面的法向量
        """
        points = self.get_points()
        # 地板除(floor division)，返回整数部分，舍弃小数部分
        k = len(points) // 3
        return points[:k], points[k:2 * k], points[2 * k:]

    def get_unit_normals(self) -> np.ndarray:
        '''获取每个分割面的法向量'''
        """
        严格来讲, 这里计算的是s_points处的法向量, 而且仅仅是近似(和计算切线的思想一样)

        s_points处真正的法向量是连接球心和s_points的向量
        3b1b为何不这么做呢?
        """
        #print("=="*200)
        s_points, du_points, dv_points = self.get_surface_points_and_nudged_points()
        normals = np.cross(
            (du_points - s_points) / self.epsilon,
            (dv_points - s_points) / self.epsilon,
        )
        return normalize_along_axis(normals, 1)

    def pointwise_become_partial(
        self,
        smobject: "Surface",
        a: float,
        b: float,
        axis: np.ndarray | None = None
    ):
        """
        这个函数竟然正确的返回了结果
        难道不需要设置三角形索引吗？
        还是说，之前计算的索引，在这里也能用？
        """
        assert(isinstance(smobject, Surface))
        if axis is None:
            axis = self.prefered_creation_axis
        if a <= 0 and b >= 1:
            self.match_points(smobject)
            return self

        nu, nv = smobject.resolution
        self.set_points(np.vstack([
            self.get_partial_points_array(arr.copy(), a, b, (nu, nv, 3), axis=axis)
            for arr in smobject.get_surface_points_and_nudged_points()
        ]))
        return self

    def get_partial_points_array(
        self,
        points: np.ndarray,
        a: float,
        b: float,
        resolution: npt.ArrayLike,
        axis: int
    ) -> np.ndarray:
        if len(points) == 0:
            return points
        nu, nv = resolution[:2]
        points = points.reshape(resolution)
        max_index = resolution[axis] - 1
        lower_index, lower_residue = integer_interpolate(0, max_index, a)
        upper_index, upper_residue = integer_interpolate(0, max_index, b)
        if axis == 0:
            points[:lower_index] = interpolate(
                points[lower_index],
                points[lower_index + 1],
                lower_residue
            )
            points[upper_index + 1:] = interpolate(
                points[upper_index],
                points[upper_index + 1],
                upper_residue
            )
        else:
            shape = (nu, 1, resolution[2])
            points[:, :lower_index] = interpolate(
                points[:, lower_index],
                points[:, lower_index + 1],
                lower_residue
            ).reshape(shape)
            points[:, upper_index + 1:] = interpolate(
                points[:, upper_index],
                points[:, upper_index + 1],
                upper_residue
            ).reshape(shape)
        return points.reshape((nu * nv, *resolution[2:]))

    def sort_faces_back_to_front(self, vect: np.ndarray = OUT):
        """
        目前还没明白这个函数的作用，但是能够看出:
        points和indices对于渲染出最终的图形来说
        两者一样重要
        """
        tri_is = self.triangle_indices
        indices = list(range(len(tri_is) // 3))
        points = self.get_points()

        def index_dot(index):
            return np.dot(points[tri_is[3 * index]], vect)

        indices.sort(key=index_dot)
        for k in range(3):
            tri_is[k::3] = tri_is[k::3][indices]
        return self

    def always_sort_to_camera(self, camera: Camera):
        self.add_updater(lambda m: m.sort_faces_back_to_front(
            camera.get_location() - self.get_center()
        ))

    # For shaders
    def get_shader_data(self) -> np.ndarray:
        """
        之前一直好奇du_points和dv_points的作用
        除了在这个类中计算每个分割面的法向量get_unit_normals()
        在shader/surface/vert.glsl下也用到了:
        v_normal = get_rotated_surface_unit_normal_vector(point, du_point, dv_point);

        vec3 get_rotated_surface_unit_normal_vector(vec3 point, vec3 du_point, vec3 dv_point){
            vec3 cp = cross(
                (du_point - point),
                (dv_point - point)
            );
            if(length(cp) == 0){
                // Instead choose a normal to just dv_point - point in the direction of point
                vec3 v2 = dv_point - point;
                cp = cross(cross(v2, point), v2);
            }
            return normalize(rotate_point_into_frame(cp));
        }
        传入point, du_point和dv_point, 计算法向量cp
        再通过rotate_point_into_frame函数, 将cp转换到相机坐标系
        """
        s_points, du_points, dv_points = self.get_surface_points_and_nudged_points()
        shader_data = self.get_resized_shader_data_array(len(s_points))
        if "points" not in self.locked_data_keys:
            shader_data["point"] = s_points
            shader_data["du_point"] = du_points
            shader_data["dv_point"] = dv_points
        self.fill_in_shader_color_info(shader_data)
        return shader_data

    def fill_in_shader_color_info(self, shader_data: np.ndarray) -> np.ndarray:
        self.read_data_to_shader(shader_data, "color", "rgbas")
        return shader_data

    def get_shader_vert_indices(self) -> np.ndarray:
        """
        三角形索引果然和着色器相关
        需要进一步研究
        """
        return self.get_triangle_indices()


class ParametricSurface(Surface):
    """
    需要注意, Surface类的父类是Mobject, 而不是VMobject
    一开始看源码的时候, 确实感到很奇怪

                Mobject
                |    |
         Vmobject    Surface

    注意观察mobject/types文件夹
    文件夹下的每一个python文件都对应shaders文件夹下的一份着色器代码
    surface.py和vectorized_mobject.py是并列的类型, 使用不同的着色器代码

    以前总是以为空间曲面和贝塞尔曲面有什么关系
    从这里的继承关系可以看出, Surface和贝塞尔曲面没有关系
    manim渲染曲面的思想很简单
    在曲面上采点, 将这些点发给着色器, 由着色器渲染
    
    尽管Surface类和Vmobject类有区别, 但是它们享有巨大的相似性: 
    它们都是点集
    所以, 玩好manim, 就是玩好点集, 就是玩好矩阵

    要将多个参数曲面打包在一起, 应该使用SGroup, 而不是VGroup
    """
    def __init__(
        self,
        uv_func: Callable[[float, float], Iterable[float]],
        u_range: tuple[float, float] = (0, 1),
        v_range: tuple[float, float] = (0, 1),
        **kwargs
    ):
        self.passed_uv_func = uv_func
        super().__init__(u_range=u_range, v_range=v_range, **kwargs)

    def uv_func(self, u, v):
        return self.passed_uv_func(u, v)


class SGroup(Surface):
    CONFIG = {
        "resolution": (0, 0),
    }

    def __init__(self, *parametric_surfaces: Surface, **kwargs):
        super().__init__(uv_func=None, **kwargs)
        self.add(*parametric_surfaces)

    def init_points(self):
        pass  # Needed?


class TexturedSurface(Surface):
    CONFIG = {
        "shader_folder": "textured_surface",
        "shader_dtype": [
            ('point', np.float32, (3,)),
            ('du_point', np.float32, (3,)),
            ('dv_point', np.float32, (3,)),
            ('im_coords', np.float32, (2,)),
            ('opacity', np.float32, (1,)),
        ]
    }

    def __init__(
        self,
        uv_surface: Surface,
        image_file: str,
        dark_image_file: str | None = None,
        **kwargs
    ):
        if not isinstance(uv_surface, Surface):
            raise Exception("uv_surface must be of type Surface")
        # Set texture information
        if dark_image_file is None:
            dark_image_file = image_file
            self.num_textures = 1
        else:
            self.num_textures = 2
        self.texture_paths = {
            "LightTexture": get_full_raster_image_path(image_file),
            "DarkTexture": get_full_raster_image_path(dark_image_file),
        }

        self.uv_surface = uv_surface
        self.uv_func = uv_surface.uv_func
        self.u_range: tuple[float, float] = uv_surface.u_range
        self.v_range: tuple[float, float] = uv_surface.v_range
        self.resolution: tuple[float, float] = uv_surface.resolution
        self.gloss: float = self.uv_surface.gloss
        super().__init__(**kwargs)

    def init_data(self):
        super().init_data()
        self.data["im_coords"] = np.zeros((0, 2))
        self.data["opacity"] = np.zeros((0, 1))

    def init_points(self):
        nu, nv = self.uv_surface.resolution
        self.set_points(self.uv_surface.get_points())
        """
        data["im_coords"]是纹理坐标
        nu和nv是surface的分辨率
        也就是说, 在u方向采样了nu个点, 在v方向采样了nv个点
        本质上, surface是nu * nv规模的矩阵

        所谓的纹理坐标, 就是为nu * nv的采样点设置对应的Texture的坐标
        """
        self.data["im_coords"] = np.array([
            [u, v]
            for u in np.linspace(0, 1, nu)
            for v in np.linspace(1, 0, nv)  # Reverse y-direction
        ])

    def init_uniforms(self):
        super().init_uniforms()
        # 纹理的数目
        self.uniforms["num_textures"] = self.num_textures

    def init_colors(self):
        self.data["opacity"] = np.array([self.uv_surface.data["rgbas"][:, 3]])

    def set_opacity(self, opacity: float, recurse: bool = True):
        for mob in self.get_family(recurse):
            mob.data["opacity"] = np.array([[o] for o in listify(opacity)])
        return self

    def pointwise_become_partial(
        self,
        tsmobject: "TexturedSurface",
        a: float,
        b: float,
        axis: int = 1
    ):
        super().pointwise_become_partial(tsmobject, a, b, axis)
        im_coords = self.data["im_coords"]
        im_coords[:] = tsmobject.data["im_coords"]
        if a <= 0 and b >= 1:
            return self
        nu, nv = tsmobject.resolution
        im_coords[:] = self.get_partial_points_array(
            im_coords, a, b, (nu, nv, 2), axis
        )
        return self

    def fill_in_shader_color_info(self, shader_data: np.ndarray) -> np.ndarray:
        self.read_data_to_shader(shader_data, "opacity", "opacity")
        self.read_data_to_shader(shader_data, "im_coords", "im_coords")
        return shader_data
