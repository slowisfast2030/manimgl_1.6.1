from __future__ import annotations

import numpy as np
from PIL import Image

from manimlib.constants import *
from manimlib.mobject.mobject import Mobject
from manimlib.utils.bezier import inverse_interpolate
from manimlib.utils.images import get_full_raster_image_path
from manimlib.utils.iterables import listify


class ImageMobject(Mobject):
    """
    以前也好奇, image是如何被显示出来的
    image的点集的概念不是很明显

    image在数学本质上是一个矩形, 包含四个点
    点的颜色由纹理决定

    ImageMobject继承至Mobject
    Mobject的"render_primitive": moderngl.TRIANGLE_STRIP 
    """
    CONFIG = {
        "height": 4,
        "opacity": 1,
        "shader_folder": "image",
        "shader_dtype": [
            ('point', np.float32, (3,)),
            ('im_coords', np.float32, (2,)),
            ('opacity', np.float32, (1,)),
        ]
    }

    def __init__(self, filename: str, **kwargs):
        self.set_image_path(get_full_raster_image_path(filename))
        super().__init__(**kwargs)

    def set_image_path(self, path: str) -> None:
        self.path = path
        self.image = Image.open(path)
        self.texture_paths = {"Texture": path}

    def init_data(self) -> None:
        """
        对比下TexturedSurface类的纹理坐标
        self.data["im_coords"] = np.array([
            [u, v]
            for u in np.linspace(0, 1, nu)
            for v in np.linspace(1, 0, nv)  # Reverse y-direction
        ])
        纹理的规模: nu * nv

        而这里
        self.data["im_coords"] = np.array([(0, 0), (0, 1), (1, 0), (1, 1)])
        也就是说, 传入image文件夹下的顶点着色器的顶点只有4个
        顶点的颜色就是对应的纹理的颜色
        到了片段着色器部分, 全靠插值
        """
        self.data = {
            "points": np.array([UL, DL, UR, DR]),
            "im_coords": np.array([(0, 0), (0, 1), (1, 0), (1, 1)]),
            #"im_coords": np.array([(0, 0), (0, 1/4), (1/4, 0), (1/4, 1/4)]),
            "opacity": np.array([[self.opacity]], dtype=np.float32),
        }

    def init_points(self) -> None:
        """
        并没有初始化点集
        设置了矩形框的大小
        """
        size = self.image.size
        self.set_width(2 * size[0] / size[1], stretch=True)
        self.set_height(self.height)

    def set_opacity(self, opacity: float, recurse: bool = True):
        for mob in self.get_family(recurse):
            mob.data["opacity"] = np.array([[o] for o in listify(opacity)])
        return self

    def set_color(self, color, opacity=None, recurse=None):
        return self

    def point_to_rgb(self, point: np.ndarray) -> np.ndarray:
        x0, y0 = self.get_corner(UL)[:2]
        x1, y1 = self.get_corner(DR)[:2]
        x_alpha = inverse_interpolate(x0, x1, point[0])
        y_alpha = inverse_interpolate(y0, y1, point[1])
        if not (0 <= x_alpha <= 1) and (0 <= y_alpha <= 1):
            # TODO, raise smarter exception
            raise Exception("Cannot sample color from outside an image")

        pw, ph = self.image.size
        rgb = self.image.getpixel((
            int((pw - 1) * x_alpha),
            int((ph - 1) * y_alpha),
        ))
        return np.array(rgb) / 255

    def get_shader_data(self) -> np.ndarray:
        shader_data = super().get_shader_data()
        self.read_data_to_shader(shader_data, "im_coords", "im_coords")
        self.read_data_to_shader(shader_data, "opacity", "opacity")
        return shader_data
