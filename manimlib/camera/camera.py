from __future__ import annotations

import moderngl
from colour import Color
import OpenGL.GL as gl
import math

import itertools as it

import numpy as np
from scipy.spatial.transform import Rotation
from PIL import Image

from manimlib.constants import *
from manimlib.mobject.mobject import Mobject
from manimlib.mobject.mobject import Point
from manimlib.utils.config_ops import digest_config
from manimlib.utils.simple_functions import fdiv
from manimlib.utils.space_ops import normalize

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from manimlib.shader_wrapper import ShaderWrapper


"""
核心函数: capture
在scene.py的update_frame函数中被调用
这个函数将着色器有关的部分链接了进来
"""

"""
frame = self.camera.frame
frame2 = frame.copy()

# 从实际效果来看
# theta是绕z轴旋转
# phi是绕x轴旋转

# 假设camera距离世界坐标系的原点的距离是r
# 那么camera运动的轨迹是一个以世界坐标系原点为圆心, 半径为r的圆

frame2.set_euler_angles(theta=-30*DEGREES, phi=70*DEGREES)
self.play(Transform(frame, frame2))

for i in range(200):
    frame.increment_theta(0.01)
    self.wait(0.001)
"""
"""
深度思考:
默认情况下,
camera的位置(0, 0, 16)
tan(vfov/2) = 1/2
aspect_ratio = 16:9
focal_distance = 16
frame.height = 8
投影面z=0
视锥的范围(-inf, 16)
在此范围内, 
离camera越近, object会放大
离camera越远, object会缩小
投影面的object保持不变

frame.set_height
frame.move_to
frame.reorient
等函数会改变camera的位置

疑惑: 上述frame的函数为何会改变camera视角呢?
在Camera类中, 会把CameraFrame对象的属性写入uniform
"""
class CameraFrame(Mobject):
    '''相机所拍摄到的帧'''
    CONFIG = {
        "frame_shape": (FRAME_WIDTH, FRAME_HEIGHT),
        "center_point": ORIGIN,
        "focal_dist_to_height": 2,
    }

    def init_uniforms(self) -> None:
        super().init_uniforms()
        # As a quaternion
        self.uniforms["orientation"] = Rotation.identity().as_quat()
        self.uniforms["focal_dist_to_height"] = self.focal_dist_to_height

    def init_points(self) -> None:
        """
        这里设置points很有趣
        self.frame对象并不是一个具体的mob, 而是对所有的mob进行的一个拍摄
        self.frame对象存在的目的是为这些mob提供统一的uniform
        从这个角度来说, 似乎并不需要set points

        从后面的代码来看, 这里设置points
        主要是为了方便获取frame的中心、宽度和高度
        不过感觉没什么必要
        """
        self.set_points([ORIGIN, LEFT, RIGHT, DOWN, UP])
        """
        set_width、set_height和move_to函数
        表面上看是为了给frame设置属性
        实质上是给uniform准备属性
        """
        self.set_width(self.frame_shape[0], stretch=True)
        self.set_height(self.frame_shape[1], stretch=True)
        self.move_to(self.center_point)

    """
    Euler angles and quaternions are both ways of representing the orientation 
    of a rigid body in three-dimensional space. They have different advantages 
    and disadvantages, and they can be converted from one to another. 
    """
    def set_orientation(self, rotation: Rotation):
        '''
        设置相机旋转（使用四元数）
        '''
        self.uniforms["orientation"][:] = rotation.as_quat()
        return self

    def get_orientation(self):
        '''
        获取相机旋转
        '''
        return Rotation.from_quat(self.uniforms["orientation"])

    def to_default_state(self):
        '''相机恢复到默认位置'''
        self.center()
        self.set_height(FRAME_HEIGHT)
        self.set_width(FRAME_WIDTH)
        self.set_orientation(Rotation.identity())
        return self

    def get_euler_angles(self):
        '''
        获取相机的欧拉角
        '''
        return self.get_orientation().as_euler("zxz")[::-1]

    """
    下面三个欧拉角的获取是为了方便使用，这个版本的代码没有
    """
    def get_theta(self):
        '''
        获取相机的欧拉角的 theta 值
        '''
        return self.get_euler_angles()[0]

    def get_phi(self):
        '''
        获取相机的欧拉角的 phi 值
        '''
        return self.get_euler_angles()[1]

    def get_gamma(self):
        '''
        获取相机的欧拉角的 gamma 值
        '''
        return self.get_euler_angles()[2]

    def get_inverse_camera_rotation_matrix(self):
        return self.get_orientation().as_matrix().T

    def rotate(self, angle: float, axis: np.ndarray = OUT, **kwargs):
        rot = Rotation.from_rotvec(angle * normalize(axis))
        self.set_orientation(rot * self.get_orientation())
        return self

    def set_euler_angles(
        self,
        theta: float | None = None,
        phi: float | None = None,
        gamma: float | None = None,
        units: float = RADIANS
    ):
        '''
        设置相机的欧拉角
        '''
        eulers = self.get_euler_angles()  # theta, phi, gamma
        for i, var in enumerate([theta, phi, gamma]):
            if var is not None:
                eulers[i] = var * units
        self.set_orientation(Rotation.from_euler("zxz", eulers[::-1]))
        return self

    def reorient(
        self,
        theta_degrees: float | None = None,
        phi_degrees: float | None = None,
        gamma_degrees: float | None = None,
    ):
        """
        Shortcut for set_euler_angles, defaulting to taking
        in angles in degrees
        """
        """
        设置相机的欧拉角, set_euler_angles 的另一种写法
        """
        self.set_euler_angles(theta_degrees, phi_degrees, gamma_degrees, units=DEGREES)
        return self

    def set_theta(self, theta: float):
        '''
        设置相机的欧拉角的 theta 值
        '''
        return self.set_euler_angles(theta=theta)

    def set_phi(self, phi: float):
        '''
        设置相机的欧拉角的 phi 值
        '''
        return self.set_euler_angles(phi=phi)

    def set_gamma(self, gamma: float):
        '''
        设置相机的欧拉角的 gamma 值
        '''
        return self.set_euler_angles(gamma=gamma)

    def increment_theta(self, dtheta: float):
        '''
        增加相机的欧拉角的 theta 值
        '''
        self.rotate(dtheta, OUT)
        return self

    def increment_phi(self, dphi: float):
        '''
        增加相机的欧拉角的 phi 值
        '''
        self.rotate(dphi, self.get_inverse_camera_rotation_matrix()[0])
        return self

    def increment_gamma(self, dgamma: float):
        '''
        增加相机的欧拉角的 gamma 值
        '''
        self.rotate(dgamma, self.get_inverse_camera_rotation_matrix()[2])
        return self

    def set_focal_distance(self, focal_distance: float):
        '''
        设置相机的焦距
        '''
        """
        这里并不是设置焦距, 而是计算焦距与高度的比值
        """
        self.uniforms["focal_dist_to_height"] = focal_distance / self.get_height()
        return self

    def set_field_of_view(self, field_of_view: float):
        '''
        设置相机的视野vfov(垂直视野)
        '''
        """
        这里绝对写错了！
        按照公式, 这里应该是
        self.uniforms["height_to_focal_dist"] = 2 * math.tan(field_of_view / 2)
        """
        self.uniforms["focal_dist_to_height"] = 2 * math.tan(field_of_view / 2)
        return self

    def get_shape(self):
        '''获取相机帧宽高'''
        return (self.get_width(), self.get_height())

    def get_center(self) -> np.ndarray:
        '''
        获取frame的中心坐标(相机坐标系)
        '''
        # Assumes first point is at the center
        return self.get_points()[0]

    def get_width(self) -> float:
        '''
        获取相机的宽度
        '''
        points = self.get_points()
        return points[2, 0] - points[1, 0]

    def get_height(self) -> float:
        '''
        获取frame的高度
        '''
        points = self.get_points()
        return points[4, 1] - points[3, 1]

    def get_focal_distance(self) -> float:
        '''
        获取相机的焦距
        '''
        return self.uniforms["focal_dist_to_height"] * self.get_height()

    def get_field_of_view(self) -> float:
        '''
        获取相机的视野(vfov)
        '''
        """
        写错了。换成下面的就很合理:
        return 2 * math.atan(self.uniforms["height_to_focal_dist"] / 2)
        """
        return 2 * math.atan(self.uniforms["focal_dist_to_height"] / 2)

    def get_implied_camera_location(self) -> np.ndarray:
        '''
        获取相机的位置(世界坐标系)
        '''
        to_camera = self.get_inverse_camera_rotation_matrix()[2]
        dist = self.get_focal_distance()
        return self.get_center() + dist * to_camera


"""
思考:
Camera类中有与着色器相关的代码
可以打print, 看看哪些被调用了以及是怎样的调用顺序
"""
class Camera(object):
    '''
    摄像机
    '''
    CONFIG = {
        "background_image": None,
        "frame_config": {},
        "pixel_width": DEFAULT_PIXEL_WIDTH,
        "pixel_height": DEFAULT_PIXEL_HEIGHT,
        "frame_rate": DEFAULT_FRAME_RATE,
        # Note: frame height and width will be resized to match
        # the pixel aspect ratio
        "background_color": BLACK,
        "background_opacity": 1,
        # Points in vectorized mobjects with norm greater
        # than this value will be rescaled.
        "max_allowable_norm": FRAME_WIDTH,
        "image_mode": "RGBA",
        "n_channels": 4,
        "pixel_array_dtype": 'uint8',
        "light_source_position": [-10, 10, 10],
        # Measured in pixel widths, used for vector graphics
        "anti_alias_width": 1.5,
        # Although vector graphics handle antialiasing fine
        # without multisampling, for 3d scenes one might want
        # to set samples to be greater than 0.
        "samples": 0,
    }

    def __init__(self, ctx: moderngl.Context | None = None, **kwargs):
        '''
        - ``frame_config`` : 相机帧参数
        - ``pixel_width`` : 像素宽度，默认 1920
        - ``pixel_height`` : 像素高度，默认 1080
        - ``frame_rate`` : 相机帧率，默认 30
        - ``light_source_position`` : 光源位置
        - ``anti_alias_width`` : 抗锯齿
        '''
        # 为何不能正确解析pw和ph参数呢？
        # 因为命令行参数优先级更高
        # 除了修改constants.py文件, 还需要修改default_config.yml文件
        digest_config(self, kwargs, locals())
        # 在好几个地方尝试修改pw和ph，这里是源头
        # self.pixel_width = 1080
        # self.pixel_height = 1920
        # print(self.pixel_width, self.pixel_height)

        self.rgb_max_val: float = np.iinfo(self.pixel_array_dtype).max
        self.background_rgba: list[float] = [
            *Color(self.background_color).get_rgb(),
            self.background_opacity
        ]
        self.init_frame()
        self.init_context(ctx)
        self.init_shaders()
        self.init_textures()
        self.init_light_source()
        self.refresh_perspective_uniforms()
        self.static_mobject_to_render_group_list = {}


    def init_frame(self) -> None:
        '''
        初始化相机帧
        '''
        self.frame = CameraFrame(**self.frame_config)

    def init_context(self, ctx: moderngl.Context | None = None) -> None:
        '''
        初始化上下文
        '''
        if ctx is None:
            ctx = moderngl.create_standalone_context()
            fbo = self.get_fbo(ctx, 0)
            #print(fbo.viewport)
        else:
            fbo = ctx.detect_framebuffer()
        self.ctx = ctx
        self.fbo = fbo
        self.set_ctx_blending()

        # For multisample antialiasing
        fbo_msaa = self.get_fbo(ctx, self.samples)
        fbo_msaa.use()
        self.fbo_msaa = fbo_msaa

    def set_ctx_blending(self, enable: bool = True) -> None:
        '''
        设置上下文混合
        '''
        if enable:
            self.ctx.enable(moderngl.BLEND)
        else:
            self.ctx.disable(moderngl.BLEND)
        self.ctx.blend_func = (
            moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA,
            # moderngl.ONE, moderngl.ONE
        )

    def set_ctx_depth_test(self, enable: bool = True) -> None:
        '''
        设置上下文深度测试
        '''
        if enable:
            self.ctx.enable(moderngl.DEPTH_TEST)
        else:
            self.ctx.disable(moderngl.DEPTH_TEST)

    def init_light_source(self) -> None:
        # "light_source_position": [-10, 10, 10]
        self.light_source = Point(self.light_source_position)

    # Methods associated with the frame buffer
    def get_fbo(
        self,
        ctx: moderngl.Context,
        samples: int = 0
    ) -> moderngl.Framebuffer:
        '''获取帧缓冲'''
        pw = self.pixel_width
        ph = self.pixel_height
        
        #print(pw, ph)
        # 一旦返回了framebuffer，viewport也就定下来了
        return ctx.framebuffer(
            color_attachments=ctx.texture(
                (pw, ph),
                components=self.n_channels,
                samples=samples,
            ),
            depth_attachment=ctx.depth_renderbuffer(
                (pw, ph),
                samples=samples
            )
        )

    def clear(self) -> None:
        '''清空帧缓冲'''
        self.fbo.clear(*self.background_rgba)
        self.fbo_msaa.clear(*self.background_rgba)

    def reset_pixel_shape(self, new_width: int, new_height: int) -> None:
        '''重置像素宽高'''
        self.pixel_width = new_width
        self.pixel_height = new_height
        self.refresh_perspective_uniforms()

    def get_raw_fbo_data(self, dtype: str = 'f1') -> bytes:
        '''获取源缓冲数据'''
        # Copy blocks from the fbo_msaa to the drawn fbo using Blit
        """
        这里的fbo数据
        1.用来生成图片, 比如scene_file_writer.py中的get_image函数
        2.用来生成视频, 比如scene_file_writer.py中的write_frame函数

        这里的fbo数据, 就是视频的每一帧的数据。至于是生成图片还是视频, 取决于调用的函数
        """
        # 为什么在这里设置像素宽度和像素高度？个人感觉应该在viewport变化的时候指定啊
        pw, ph = (self.pixel_width, self.pixel_height)
        gl.glBindFramebuffer(gl.GL_READ_FRAMEBUFFER, self.fbo_msaa.glo)
        gl.glBindFramebuffer(gl.GL_DRAW_FRAMEBUFFER, self.fbo.glo)
        gl.glBlitFramebuffer(0, 0, pw, ph, 0, 0, pw, ph, gl.GL_COLOR_BUFFER_BIT, gl.GL_LINEAR)
        # 没想到viewport在这里！
        #print(pw, ph)
        #print(self.fbo.viewport)
        return self.fbo.read(
            viewport=self.fbo.viewport,
            components=self.n_channels,
            dtype=dtype,
        )

    def get_image(self) -> Image.Image:
        '''获取当前帧图片'''
        """
        由fbo数据生成图片
        """
        return Image.frombytes(
            'RGBA',
            self.get_pixel_shape(),
            self.get_raw_fbo_data(),
            'raw', 'RGBA', 0, -1
        )

    def get_pixel_array(self) -> np.ndarray:
        '''获取当前帧 RGB 像素矩阵'''
        raw = self.get_raw_fbo_data(dtype='f4')
        flat_arr = np.frombuffer(raw, dtype='f4')
        arr = flat_arr.reshape([*self.fbo.size, self.n_channels])
        # Convert from float
        return (self.rgb_max_val * arr).astype(self.pixel_array_dtype)

    # Needed?
    def get_texture(self) -> moderngl.Texture:
        '''获取贴图资源'''
        texture = self.ctx.texture(
            size=self.fbo.size,
            components=4,
            data=self.get_raw_fbo_data(),
            dtype='f4'
        )
        return texture

    # Getting camera attributes
    def get_pixel_shape(self) -> tuple[int, int]:
        '''获取画面像素大小'''
        return self.fbo.viewport[2:4]
        # return (self.pixel_width, self.pixel_height)

    def get_pixel_width(self) -> int:
        '''获取画面像素宽度'''
        return self.get_pixel_shape()[0]

    def get_pixel_height(self) -> int:
        '''获取画面像素高度'''
        return self.get_pixel_shape()[1]

    def get_frame_height(self) -> float:
        '''获取相机帧高度'''
        return self.frame.get_height()

    def get_frame_width(self) -> float:
        '''获取相机帧宽度'''
        return self.frame.get_width()

    def get_frame_shape(self) -> tuple[float, float]:
        '''获取相机帧宽高'''
        return (self.get_frame_width(), self.get_frame_height())

    def get_frame_center(self) -> np.ndarray:
        '''获取相机帧中心'''
        return self.frame.get_center()

    def get_location(self) -> tuple[float, float, float]:
        '''
        获取相机位置(世界坐标系)
        '''
        return self.frame.get_implied_camera_location()

    def resize_frame_shape(self, fixed_dimension: bool = False) -> None:
        """
        重置帧大小以匹配画面像素比

        ``fixed_dimension`` 控制高度不变宽度变化，或宽度不变高度变化
        """
        """
        Changes frame_shape to match the aspect ratio
        of the pixels, where fixed_dimension determines
        whether frame_height or frame_width
        remains fixed while the other changes accordingly.
        """
        pixel_height = self.get_pixel_height()
        pixel_width = self.get_pixel_width()
        frame_height = self.get_frame_height()
        frame_width = self.get_frame_width()
        aspect_ratio = fdiv(pixel_width, pixel_height)
        if not fixed_dimension:
            frame_height = frame_width / aspect_ratio
        else:
            frame_width = aspect_ratio * frame_height
        self.frame.set_height(frame_height)
        self.frame.set_width(frame_width)

    # Rendering
    def capture(self, *mobjects: Mobject, **kwargs) -> None:
        """
        给场景中的mobs拍照
        
        核心函数, 在scene.py中被调用
        """
        self.refresh_perspective_uniforms()
        for mobject in mobjects:
            for render_group in self.get_render_group_list(mobject):
                self.render(render_group)

    def render(self, render_group: dict[str]) -> None:
        '''渲染'''
        shader_wrapper = render_group["shader_wrapper"]
        shader_program = render_group["prog"]
        # 设置传入shader的uniform变量
        self.set_shader_uniforms(shader_program, shader_wrapper)
        self.set_ctx_depth_test(shader_wrapper.depth_test)
        render_group["vao"].render(int(shader_wrapper.render_primitive))
        if render_group["single_use"]:
            self.release_render_group(render_group)

    def get_render_group_list(self, mobject: Mobject) -> list[dict[str]] | map[dict[str]]:
        try:
            return self.static_mobject_to_render_group_list[id(mobject)]
        except KeyError:
            return map(self.get_render_group, mobject.get_shader_wrapper_list())

    def get_render_group(
        self,
        shader_wrapper: ShaderWrapper,
        single_use: bool = True
    ) -> dict[str]:
        '''获取渲染所包含的成员

        - ``vbo`` : vertex data buffer 
        - ``ibo`` : vertex index data buffer
        - ``vao`` : vertex array
        - ``prog`` : shader program
        - ``shader_wrapper`` : 材质包装
        - ``single_use`` : 单次使用
        '''
        # Data buffers
        vbo = self.ctx.buffer(shader_wrapper.vert_data.tobytes())
        if shader_wrapper.vert_indices is None:
            ibo = None
        else:
            vert_index_data = shader_wrapper.vert_indices.astype('i4').tobytes()
            if vert_index_data:
                ibo = self.ctx.buffer(vert_index_data)
            else:
                ibo = None

        # Program and vertex array
        shader_program, vert_format = self.get_shader_program(shader_wrapper)
        vao = self.ctx.vertex_array(
            program=shader_program,
            content=[(vbo, vert_format, *shader_wrapper.vert_attributes)],
            index_buffer=ibo,
        )
        return {
            "vbo": vbo,
            "ibo": ibo,
            "vao": vao,
            "prog": shader_program,
            "shader_wrapper": shader_wrapper,
            "single_use": single_use,
        }

    def release_render_group(self, render_group: dict[str]) -> None:
        '''释放渲染'''
        for key in ["vbo", "ibo", "vao"]:
            if render_group[key] is not None:
                render_group[key].release()

    def set_mobjects_as_static(self, *mobjects: Mobject) -> None:
        # Creates buffer and array objects holding each mobjects shader data
        for mob in mobjects:
            self.static_mobject_to_render_group_list[id(mob)] = [
                self.get_render_group(sw, single_use=False)
                for sw in mob.get_shader_wrapper_list()
            ]

    def release_static_mobjects(self) -> None:
        for rg_list in self.static_mobject_to_render_group_list.values():
            for render_group in rg_list:
                self.release_render_group(render_group)
        self.static_mobject_to_render_group_list = {}

    # Shaders
    def init_shaders(self) -> None:
        # Initialize with the null id going to None
        self.id_to_shader_program: dict[
            int | str, tuple[moderngl.Program, str] | None
        ] = {"": None}

    def get_shader_program(
        self,
        shader_wrapper: ShaderWrapper
    ) -> tuple[moderngl.Program, str]:
        '''获取着色器的代码'''
        sid = shader_wrapper.get_program_id()
        if sid not in self.id_to_shader_program:
            # Create shader program for the first time, then cache
            # in the id_to_shader_program dictionary
            program = self.ctx.program(**shader_wrapper.get_program_code())
            vert_format = moderngl.detect_format(program, shader_wrapper.vert_attributes)
            self.id_to_shader_program[sid] = (program, vert_format)
        return self.id_to_shader_program[sid]

    def set_shader_uniforms(
        self,
        shader: moderngl.Program,
        shader_wrapper: ShaderWrapper
    ) -> None:
        '''设置着色器的 ``uniform`` 变量'''
        for name, path in shader_wrapper.texture_paths.items():
            tid = self.get_texture_id(path)
            shader[name].value = tid
        for name, value in it.chain(self.perspective_uniforms.items(), shader_wrapper.uniforms.items()):
            try:
                if isinstance(value, np.ndarray) and value.ndim > 0:
                    value = tuple(value)
                shader[name].value = value
            except KeyError:
                pass

    def refresh_perspective_uniforms(self) -> None:
        '''更新透视uniform'''
        """
        着色器的顶点着色器代码中传入了很多uniform
        
        以前一直好奇, self.frame继承至Mobject, 在frame中执行
        self.frame.set_height
        self.move_to
        self.reorient
        等函数, 为何会影响计算机的视角呢？
        原来, self.frame对象设置了这些属性并不是直接对frame起作用
        而是对着色器的uniform变量进行了赋值
        frame --> shader --> frame
        总结来说: 对frame的属性设置, 直接改变uniform, 间接改变frame
        """
        frame = self.frame
        pw, ph = self.get_pixel_shape()
        fw, fh = frame.get_shape()
        # TODO, this should probably be a mobject uniform, with
        # the camera taking care of the conversion factor
        anti_alias_width = self.anti_alias_width / (ph / fh)
        # Orient light
        rotation = frame.get_inverse_camera_rotation_matrix()
        offset = frame.get_center()
        # 这里使用rotation对世界坐标系的light_source进行了坐标变换
        # 那么，可以猜测：在顶点着色器中，也会使用rotation对世界坐标系
        # 的点进行坐标变换
        # 需要进一步理解这里的rotation究竟是什么
        light_pos = np.dot(
            rotation, self.light_source.get_location() + offset
        )
        cam_pos = self.frame.get_implied_camera_location()  # TODO
        """
        一个疑问:
        这里的camera_rotation是列表
        但是在后面的着色器代码中又是mat3
        究竟哪里对其进行了修改
        """
        self.perspective_uniforms = {
            "frame_shape": frame.get_shape(),
            "anti_alias_width": anti_alias_width,
            "camera_offset": tuple(offset),
            "camera_rotation": tuple(np.array(rotation).T.flatten()),
            "camera_position": tuple(cam_pos),
            "light_source_position": tuple(light_pos),
            "focal_distance": frame.get_focal_distance(),
        }
        # print("~"*100)
        # for name, value in self.perspective_uniforms.items():
        #     if name == "camera_rotation":
        #         print("rotation: \n", rotation)
        #         continue 
        #     print("{}={}".format(name, value))

    def init_textures(self) -> None:
        self.n_textures: int = 0
        self.path_to_texture: dict[
            str, tuple[int, moderngl.Texture]
        ] = {}

    def get_texture_id(self, path: str) -> int:
        '''获取资源 id'''
        if path not in self.path_to_texture:
            if self.n_textures == 15:  # I have no clue why this is needed
                self.n_textures += 1
            tid = self.n_textures
            self.n_textures += 1
            im = Image.open(path).convert("RGBA")
            texture = self.ctx.texture(
                size=im.size,
                components=len(im.getbands()),
                data=im.tobytes(),
            )
            texture.use(location=tid)
            self.path_to_texture[path] = (tid, texture)
        return self.path_to_texture[path][0]

    def release_texture(self, path: str):
        '''释放资源'''
        tid_and_texture = self.path_to_texture.pop(path, None)
        if tid_and_texture:
            tid_and_texture[1].release()
        return self


# Mostly just defined so old scenes don't break
class ThreeDCamera(Camera):
    '''仅用于保证旧版场景不崩溃'''
    CONFIG = {
        "samples": 4,
        "anti_alias_width": 0,
    }
