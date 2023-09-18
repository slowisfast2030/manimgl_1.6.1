from __future__ import annotations

import os
import hashlib
import itertools as it
from typing import Callable
from xml.etree import ElementTree as ET

import svgelements as se
import numpy as np

from manimlib.constants import RIGHT
from manimlib.mobject.geometry import Line
from manimlib.mobject.geometry import Circle
from manimlib.mobject.geometry import Polygon
from manimlib.mobject.geometry import Polyline
from manimlib.mobject.geometry import Rectangle
from manimlib.mobject.geometry import RoundedRectangle
from manimlib.mobject.types.vectorized_mobject import VMobject
from manimlib.utils.config_ops import digest_config
from manimlib.utils.directories import get_mobject_data_dir
from manimlib.utils.images import get_full_vector_image_path
from manimlib.utils.iterables import hash_obj
from manimlib.logger import log


SVG_HASH_TO_MOB_MAP: dict[int, VMobject] = {}


def _convert_point_to_3d(x: float, y: float) -> np.ndarray:
    return np.array([x, y, 0.0])


"""
SVGMobject就是取出svg文件里的命令, 绘制出对应的图形

所以, 你可以用inkscape等工具, 绘制出你想要的图形, 然后导出为svg文件, 再用SVGMobject读取, 就可以得到对应的图形了

也可以通过manim去绘制, 工作量比较大
"""
class SVGMobject(VMobject):
    """
    传入一个文件名指向输入的SVG文件
    """
    CONFIG = {
        "should_center": True,
        "height": 2,
        "width": None,
        "file_name": None,
        # Style that overrides the original svg
        "color": None,
        "opacity": None,
        "fill_color": None,
        "fill_opacity": None,
        "stroke_width": None,
        "stroke_color": None,
        "stroke_opacity": None,
        # Style that fills only when not specified
        # If None, regarded as default values from svg standard
        "svg_default": {
            "color": None,
            "opacity": None,
            "fill_color": None,
            "fill_opacity": None,
            "stroke_width": None,
            "stroke_color": None,
            "stroke_opacity": None,
        },
        "path_string_config": {},
    }

    def __init__(self, file_name: str | None = None, **kwargs):
        super().__init__(**kwargs)
        self.file_name = file_name or self.file_name
        self.init_svg_mobject()
        self.init_colors()
        self.move_into_position()

    """
    c = SingleStringTex("A  BC", organize_left_to_right=False)

    print(c.family)
    [<manimlib.mobject.svg.tex_mobject.SingleStringTex object at 0x7f793a79a760>, 
    <manimlib.mobject.svg.svg_mobject.VMobjectFromSVGPath object at 0x7f793a76e3d0>, 
    <manimlib.mobject.svg.svg_mobject.VMobjectFromSVGPath object at 0x7f793a961e50>, 
    <manimlib.mobject.svg.svg_mobject.VMobjectFromSVGPath object at 0x7f793a9822e0>]

    打印后发现后三个分别是A, B, C
    第一个是SingleStringTex对象, 没有点集, 是一个空对象
    """
    def init_svg_mobject(self) -> None:
        hash_val = hash_obj(self.hash_seed)
        if hash_val in SVG_HASH_TO_MOB_MAP:
            mob = SVG_HASH_TO_MOB_MAP[hash_val].copy()
            self.add(*mob)
            return

        self.generate_mobject()
        SVG_HASH_TO_MOB_MAP[hash_val] = self.copy()

    @property
    def hash_seed(self) -> tuple:
        # Returns data which can uniquely represent the result of `init_points`.
        # The hashed value of it is stored as a key in `SVG_HASH_TO_MOB_MAP`.
        return (
            self.__class__.__name__,
            self.svg_default,
            self.path_string_config,
            self.file_name
        )

    def generate_mobject(self) -> None:
        """
        解析svg文件, 获得vmobs, 并将其添加为submobs
        """
        file_path = self.get_file_path()
        element_tree = ET.parse(file_path)
        new_tree = self.modify_xml_tree(element_tree)
        # Create a temporary svg file to dump modified svg to be parsed
        root, ext = os.path.splitext(file_path)
        modified_file_path = root + "_" + ext
        new_tree.write(modified_file_path)

        svg = se.SVG.parse(modified_file_path)
        os.remove(modified_file_path)

        mobjects = self.get_mobjects_from(svg)
        # mobjects是vmob列表, 这里执行self.add方法, 就将其添加为submob 
        self.add(*mobjects)
        self.flip(RIGHT)  # Flip y

    def get_file_path(self) -> str:
        if self.file_name is None:
            raise Exception("Must specify file for SVGMobject")
        return get_full_vector_image_path(self.file_name)

    def modify_xml_tree(self, element_tree: ET.ElementTree) -> ET.ElementTree:
        config_style_dict = self.generate_config_style_dict()
        style_keys = (
            "fill",
            "fill-opacity",
            "stroke",
            "stroke-opacity",
            "stroke-width",
            "style"
        )
        root = element_tree.getroot()
        root_style_dict = {
            k: v for k, v in root.attrib.items()
            if k in style_keys
        }

        new_root = ET.Element("svg", {})
        config_style_node = ET.SubElement(new_root, "g", config_style_dict)
        root_style_node = ET.SubElement(config_style_node, "g", root_style_dict)
        root_style_node.extend(root)
        return ET.ElementTree(new_root)

    def generate_config_style_dict(self) -> dict[str, str]:
        keys_converting_dict = {
            "fill": ("color", "fill_color"),
            "fill-opacity": ("opacity", "fill_opacity"),
            "stroke": ("color", "stroke_color"),
            "stroke-opacity": ("opacity", "stroke_opacity"),
            "stroke-width": ("stroke_width",)
        }
        svg_default_dict = self.svg_default
        result = {}
        for svg_key, style_keys in keys_converting_dict.items():
            for style_key in style_keys:
                if svg_default_dict[style_key] is None:
                    continue
                result[svg_key] = str(svg_default_dict[style_key])
        return result

    def get_mobjects_from(self, svg: se.SVG) -> list[VMobject]:
        """
        https://www.runoob.com/svg/svg-path.html
        svg元素如下:
        1.<path>     最复杂，既包含简单的移动，也包含复杂的贝塞尔曲线
        2.<line>
        3.<rect>
        4.<circle>
        5.<ellipse>
        6.<polygon>  多边形
        7.<polyline> 多线段
        8.<text>     Todo
        """
        """
        解析svg, 获得vmob列表
        """
        result = []
        for shape in svg.elements():
            """
            每一个字母、数字等符号都是由贝塞尔曲线生成的
            当各种符号被latex渲染出来并保存为svg后
            每一个符号在svg文件中都是一个xml元素
            可以一个个被解析出来
            """
            if isinstance(shape, se.Group):
                continue
            elif isinstance(shape, se.Path):    # 字母、公式
                mob = self.path_to_mobject(shape)
            elif isinstance(shape, se.SimpleLine):
                mob = self.line_to_mobject(shape)
            elif isinstance(shape, se.Rect):
                mob = self.rect_to_mobject(shape)
            elif isinstance(shape, se.Circle):
                mob = self.circle_to_mobject(shape)
            elif isinstance(shape, se.Ellipse):
                mob = self.ellipse_to_mobject(shape)
            elif isinstance(shape, se.Polygon):
                mob = self.polygon_to_mobject(shape)
            elif isinstance(shape, se.Polyline):
                mob = self.polyline_to_mobject(shape)
            # elif isinstance(shape, se.Text):
            #     mob = self.text_to_mobject(shape)
            elif type(shape) == se.SVGElement:
                continue
            else:
                # 下面这一行总是报警，直接注释掉
                # 因为这里对svg的解析不是很全面, 只做了最基本形状的解析
                #log.warning(f"Unsupported element type: {type(shape)}")
                continue
            if not mob.has_points():
                continue
            self.apply_style_to_mobject(mob, shape)
            if isinstance(shape, se.Transformable) and shape.apply:
                self.handle_transform(mob, shape.transform)
            result.append(mob)
        return result

    @staticmethod
    def handle_transform(mob: VMobject, matrix: se.Matrix) -> VMobject:
        mat = np.array([
            [matrix.a, matrix.c],
            [matrix.b, matrix.d]
        ])
        vec = np.array([matrix.e, matrix.f, 0.0])
        mob.apply_matrix(mat)
        mob.shift(vec)
        return mob

    @staticmethod
    def apply_style_to_mobject(
        mob: VMobject,
        shape: se.GraphicObject
    ) -> VMobject:
        mob.set_style(
            stroke_width=shape.stroke_width,
            stroke_color=shape.stroke.hex,
            stroke_opacity=shape.stroke.opacity,
            fill_color=shape.fill.hex,
            fill_opacity=shape.fill.opacity
        )
        return mob

    @staticmethod
    def handle_transform(mob, matrix):
        mat = np.array([
            [matrix.a, matrix.c],
            [matrix.b, matrix.d]
        ])
        vec = np.array([matrix.e, matrix.f, 0.0])
        mob.apply_matrix(mat)
        mob.shift(vec)
        return mob

    def path_to_mobject(self, path: se.Path) -> VMobjectFromSVGPath:
        """
        <svg xmlns="http://www.w3.org/2000/svg" version="1.1">
        <path d="M150 0 L75 200 L225 200 Z" />
        </svg>
        """
        return VMobjectFromSVGPath(path, **self.path_string_config)

    def line_to_mobject(self, line: se.Line) -> Line:
        """
        <svg xmlns="http://www.w3.org/2000/svg" version="1.1">
        <line x1="0" y1="0" x2="200" y2="200"
        style="stroke:rgb(255,0,0);stroke-width:2"/>
        </svg>
        """
        return Line(
            start=_convert_point_to_3d(line.x1, line.y1),
            end=_convert_point_to_3d(line.x2, line.y2)
        )

    def rect_to_mobject(self, rect: se.Rect) -> Rectangle:
        """
        <svg xmlns="http://www.w3.org/2000/svg" version="1.1">
        <rect x="50" y="20" rx="20" ry="20" width="150"
        height="150"
        style="fill:red;stroke:black;stroke-width:5;opacity:0.5"/>
        </svg>
        """
        if rect.rx == 0 or rect.ry == 0:
            mob = Rectangle(
                width=rect.width,
                height=rect.height,
            )
        else:
            mob = RoundedRectangle(
                width=rect.width,
                height=rect.height * rect.rx / rect.ry,
                corner_radius=rect.rx
            )
            mob.stretch_to_fit_height(rect.height)
        mob.shift(_convert_point_to_3d(
            rect.x + rect.width / 2,
            rect.y + rect.height / 2
        ))
        return mob

    def circle_to_mobject(self, circle: se.Circle) -> Circle:
        # svgelements supports `rx` & `ry` but `r`
        mob = Circle(radius=circle.rx)
        mob.shift(_convert_point_to_3d(
            circle.cx, circle.cy
        ))
        return mob

    def ellipse_to_mobject(self, ellipse: se.Ellipse) -> Circle:
        """
        <svg xmlns="http://www.w3.org/2000/svg" version="1.1">
        <ellipse cx="300" cy="80" rx="100" ry="50"
        style="fill:yellow;stroke:purple;stroke-width:2"/>
        </svg>
        """
        mob = Circle(radius=ellipse.rx)
        mob.stretch_to_fit_height(2 * ellipse.ry)
        mob.shift(_convert_point_to_3d(
            ellipse.cx, ellipse.cy
        ))
        return mob

    def polygon_to_mobject(self, polygon: se.Polygon) -> Polygon:
        """
        <svg  height="210" width="500">
        <polygon points="200,10 250,190 160,210"
        style="fill:lime;stroke:purple;stroke-width:1"/>
        </svg>
        """
        points = [
            _convert_point_to_3d(*point)
            for point in polygon
        ]
        return Polygon(*points)

    def polyline_to_mobject(self, polyline: se.Polyline) -> Polyline:
        """
        <svg xmlns="http://www.w3.org/2000/svg" version="1.1">
        <polyline points="20,20 40,25 60,40 80,120 120,140 200,180"
        style="fill:none;stroke:black;stroke-width:3" />
        </svg>
        """
        points = [
            _convert_point_to_3d(*point)
            for point in polyline
        ]
        return Polyline(*points)

    def text_to_mobject(self, text: se.Text):
        """
        <svg xmlns="http://www.w3.org/2000/svg" version="1.1">
        <text x="0" y="15" fill="red">I love SVG</text>
        </svg>
        """
        pass

    def move_into_position(self) -> None:
        if self.should_center:
            self.center()
        if self.height is not None:
            self.set_height(self.height)
        if self.width is not None:
            self.set_width(self.width)


class VMobjectFromSVGPath(VMobject):
    """传入svg的path元素的字符串, 得到一个由其生成的VMobject, 即只处理path
    
    下面的命令可用于路径数据：
    M = moveto
    L = lineto
    H = horizontal lineto
    V = vertical lineto
    C = curveto
    S = smooth curveto
    Q = quadratic Bézier curve
    T = smooth quadratic Bézier curveto
    A = elliptical Arc
    Z = closepath

    示例：
    <svg xmlns="http://www.w3.org/2000/svg" version="1.1">
        <path d="M150 0 L75 200 L225 200 Z" />
        </svg>
    """
    CONFIG = {
        "long_lines": False,
        "should_subdivide_sharp_curves": False,
        "should_remove_null_curves": False,
    }

    def __init__(self, path_obj: se.Path, **kwargs):
        # Get rid of arcs
        path_obj.approximate_arcs_with_quads()
        self.path_obj = path_obj
        super().__init__(**kwargs)

    def init_points(self) -> None:
        # After a given svg_path has been converted into points, the result
        # will be saved to a file so that future calls for the same path
        # don't need to retrace the same computation.
        path_string = self.path_obj.d()
        hasher = hashlib.sha256(path_string.encode())
        path_hash = hasher.hexdigest()[:16]
        points_filepath = os.path.join(get_mobject_data_dir(), f"{path_hash}_points.npy")
        tris_filepath = os.path.join(get_mobject_data_dir(), f"{path_hash}_tris.npy")

        if os.path.exists(points_filepath) and os.path.exists(tris_filepath):
            self.set_points(np.load(points_filepath))
            self.triangulation = np.load(tris_filepath)
            self.needs_new_triangulation = False
        else:
            self.handle_commands()
            if self.should_subdivide_sharp_curves:
                # For a healthy triangulation later
                self.subdivide_sharp_curves()
            if self.should_remove_null_curves:
                # Get rid of any null curves
                self.set_points(self.get_points_without_null_curves())
            # Save to a file for future use
            np.save(points_filepath, self.get_points())
            np.save(tris_filepath, self.get_triangulation())

    def handle_commands(self) -> None:
        segment_class_to_func_map = {
            se.Move: (self.start_new_path, ("end",)),
            se.Close: (self.close_path, ()),
            se.Line: (self.add_line_to, ("end",)),
            se.QuadraticBezier: (self.add_quadratic_bezier_curve_to, ("control", "end")),
            se.CubicBezier: (self.add_cubic_bezier_curve_to, ("control1", "control2", "end"))
        }
        for segment in self.path_obj:
            segment_class = segment.__class__
            func, attr_names = segment_class_to_func_map[segment_class]
            points = [
                _convert_point_to_3d(*segment.__getattribute__(attr_name))
                for attr_name in attr_names
            ]
            func(*points)

        # Get rid of the side effect of trailing "Z M" commands.
        if self.has_new_path_started():
            self.resize_points(self.get_num_points() - 1)
