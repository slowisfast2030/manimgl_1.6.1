import random

from colour import Color
import numpy as np

from manimlib.constants import WHITE
from manimlib.constants import COLORMAP_3B1B
from manimlib.utils.bezier import interpolate
from manimlib.utils.iterables import resize_with_interpolation


"""
color_to_rgb(RED)
[0.98823529 0.38431373 0.33333333]
"""
def color_to_rgb(color):
    """
    颜色到rgb数组
    """
    if isinstance(color, str):
        return hex_to_rgb(color)
    elif isinstance(color, Color):
        return np.array(color.get_rgb())
    else:
        raise Exception("Invalid color type")


def color_to_rgba(color, alpha=1):
    """
    颜色到rgba数组
    """
    return np.array([*color_to_rgb(color), alpha])


def rgb_to_color(rgb):
    """
    rgb数组到颜色
    """
    try:
        return Color(rgb=rgb)
    except ValueError:
        return Color(WHITE)


def rgba_to_color(rgba):
    """
    rgba数组到颜色
    """
    return rgb_to_color(rgba[:3])


def rgb_to_hex(rgb):
    return "#" + "".join(
        hex(int_x // 16)[2] + hex(int_x % 16)[2]
        for x in rgb
        for int_x in [int(255 * x)]
    )


def hex_to_rgb(hex_code):
    hex_part = hex_code[1:]
    if len(hex_part) == 3:
        hex_part = "".join([2 * c for c in hex_part])
    return np.array([
        int(hex_part[i:i + 2], 16) / 255
        for i in range(0, 6, 2)
    ])


def invert_color(color):
    """
    反转色
    """
    return rgb_to_color(1.0 - color_to_rgb(color))


def color_to_int_rgb(color):
    return (255 * color_to_rgb(color)).astype('uint8')


def color_to_int_rgba(color, opacity=1.0):
    alpha = int(255 * opacity)
    return np.array([*color_to_int_rgb(color), alpha])


def color_gradient(reference_colors, length_of_output):
    """
    给定颜色数组reference_colors
    输出length_of_output中颜色

    可以简单理解为在原颜色数组中插值得到另一个颜色数组
    """
    if length_of_output == 0:
        return reference_colors[0]
    rgbs = list(map(color_to_rgb, reference_colors))
    alphas = np.linspace(0, (len(rgbs) - 1), length_of_output)
    floors = alphas.astype('int')
    alphas_mod1 = alphas % 1
    # End edge case
    alphas_mod1[-1] = 1
    floors[-1] = len(rgbs) - 2
    return [
        rgb_to_color(interpolate(rgbs[i], rgbs[i + 1], alpha))
        for i, alpha in zip(floors, alphas_mod1)
    ]


def interpolate_color(color1, color2, alpha):
    """
    颜色的插值

    渐变色
    颜色梯度
    """
    rgb = interpolate(color_to_rgb(color1), color_to_rgb(color2), alpha)
    return rgb_to_color(rgb)


def average_color(*colors):
    """
    平均色
    """
    rgbs = np.array(list(map(color_to_rgb, colors)))
    return rgb_to_color(rgbs.mean(0))


def random_bright_color():
    """
    随机明亮的颜色
    """
    color = random_color()
    curr_rgb = color_to_rgb(color)
    new_rgb = interpolate(
        curr_rgb, np.ones(len(curr_rgb)), 0.5
    )
    return Color(rgb=new_rgb)


def random_color():
    """
    随机颜色
    """
    return Color(rgb=(random.random() for i in range(3)))


def get_colormap_list(map_name="viridis", n_colors=9):
    """
    Options for map_name:
    3b1b_colormap
    magma
    inferno
    plasma
    viridis
    cividis
    twilight
    twilight_shifted
    turbo
    """
    from matplotlib.cm import get_cmap

    if map_name == "3b1b_colormap":
        rgbs = [color_to_rgb(color) for color in COLORMAP_3B1B]
    else:
        rgbs = get_cmap(map_name).colors  # Make more general?
    return resize_with_interpolation(np.array(rgbs), n_colors)
