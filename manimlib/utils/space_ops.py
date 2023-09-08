from __future__ import annotations

import math
import operator as op
from functools import reduce
from typing import Callable, Iterable, Sequence
import platform

import numpy as np
import numpy.typing as npt
from mapbox_earcut import triangulate_float32 as earcut
from scipy.spatial.transform import Rotation
from tqdm import tqdm as ProgressDisplay

from manimlib.constants import RIGHT
from manimlib.constants import DOWN
from manimlib.constants import OUT
from manimlib.constants import PI
from manimlib.constants import TAU
from manimlib.utils.iterables import adjacent_pairs
from manimlib.utils.simple_functions import clip


def cross(v1: np.ndarray, v2: np.ndarray) -> list[np.ndarray]:
    """
    |   i     j     k   |
    | v1[0] v1[1] v1[2] |
    | v2[0] v2[1] v2[2] |

    计算v1和v2的叉乘
    """
    return [
        v1[1] * v2[2] - v1[2] * v2[1],
        v1[2] * v2[0] - v1[0] * v2[2],
        v1[0] * v2[1] - v1[1] * v2[0]
    ]


def get_norm(vect: Iterable) -> float:
    return sum((x**2 for x in vect))**0.5


def normalize(vect: np.ndarray, fall_back: np.ndarray | None = None) -> np.ndarray:
    norm = get_norm(vect)
    if norm > 0:
        return np.array(vect) / norm
    elif fall_back is not None:
        return fall_back
    else:
        return np.zeros(len(vect))


# Operations related to rotation


def quaternion_mult(*quats: Sequence[float]) -> list[float]:
    # Real part is last entry, which is bizzare, but fits scipy Rotation convention
    """
    多个四元数相乘
    """
    if len(quats) == 0:
        return [0, 0, 0, 1]
    result = quats[0]
    for next_quat in quats[1:]:
        x1, y1, z1, w1 = result
        x2, y2, z2, w2 = next_quat
        result = [
            w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2,
            w1 * y2 + y1 * w2 + z1 * x2 - x1 * z2,
            w1 * z2 + z1 * w2 + x1 * y2 - y1 * x2,
            w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2,
        ]
    return result


def quaternion_from_angle_axis(
    angle: float,
    axis: np.ndarray,
) -> list[float]:
    """
    给定angle和axis, 返回四元数
    sin(angle/2)axis[0]
    sin(angle/2)axis[1]
    sin(angle/2)axis[2]
    cos(angle/2)

    最后一个数是实部

    举例:
    angle = np.pi / 4 
    axis = np.array([0, 0, 1]) 
    quaternion = quaternion_from_angle_axis(angle, axis) 
    返回结果[0, 0, 0.38268343, 0.92387953]

    math.sin(np.pi/8) --> 0.3826834323650898
    math.cos(np.pi/8) --> 0.9238795325112867
    """
    return Rotation.from_rotvec(angle * normalize(axis)).as_quat()


def angle_axis_from_quaternion(quat: Sequence[float]) -> tuple[float, np.ndarray]:
    """
    给定四元数，返回angle和axis

    quat = [0, 0, 0.3826834323650898, 0.9238795325112867]
    angle, axis = angle_axis_from_quaternion(quat)
    print(angle, axis)

    0.7853981633974484 [0. 0. 1.]
    """
    rot_vec = Rotation.from_quat(quat).as_rotvec()
    norm = get_norm(rot_vec)
    return norm, rot_vec / norm


def quaternion_conjugate(quaternion: Iterable) -> list:
    result = list(quaternion)
    for i in range(3):
        result[i] *= -1
    return result


def rotate_vector(
    vector: Iterable,
    angle: float,
    axis: np.ndarray = OUT
) -> np.ndarray | list[float]:
    """
    这里默认axis过原点
    """
    rot = Rotation.from_rotvec(angle * normalize(axis))
    return np.dot(vector, rot.as_matrix().T)


"""
complex is a built-in function that comes with Python. It is used to create 
a complex number by specifying a real part and an imaginary part. For example, 
complex(3, 5) returns (3+5j), which is a complex number with real part 3 and 
imaginary part 5. You can also use a string as the first argument of the complex 
function, as long as it represents a valid complex number. For example, 
complex('3+5j') also returns (3+5j)
"""
def rotate_vector_2d(vector: Iterable, angle: float):
    # Use complex numbers...because why not
    """
    使用复数完成2d vector的旋转
    令vector为(x,y)
    z = (x+i*y)*e^(i*angle)
    完美的使用了复数的两种表达形式
    """
    z = complex(*vector) * np.exp(complex(0, angle))
    return np.array([z.real, z.imag])


def rotation_matrix_transpose_from_quaternion(quat: Iterable) -> np.ndarray:
    return Rotation.from_quat(quat).as_matrix()


def rotation_matrix_from_quaternion(quat: Iterable) -> np.ndarray:
    return np.transpose(rotation_matrix_transpose_from_quaternion(quat))


"""
获取旋转矩阵
"""
def rotation_matrix(angle: float, axis: np.ndarray) -> np.ndarray:
    """
    Rotation in R^3 about a specified axis of rotation.

    特别注意: 这里默认axis过原点

    表达旋转的三种方法:
    1.angle, axis
    2.quaternion
    3.matrix
    4.欧拉角

    Rotation.from_quat(quat).as_rotvec()
    Rotation.from_rotvec(angle * normalize(axis)).as_quat()
    Rotation.from_rotvec(angle * normalize(axis)).as_matrix()
    Rotation.from_euler("zxz", eulers[::-1]) 
    """
    return Rotation.from_rotvec(angle * normalize(axis)).as_matrix()


"""
获取旋转矩阵的转置
"""
def rotation_matrix_transpose(angle: float, axis: np.ndarray) -> np.ndarray:
    return rotation_matrix(angle, axis).T


"""
s = Square().set_color(WHITE).shift(RIGHT*2)
s.apply_points_function(
    lambda points: np.dot(points, rotation_about_z(PI/8))
)
"""
def rotation_about_z(angle: float) -> list[list[float]]:
    """
    可用rotation_matrix函数代替
    """
    return [
        [math.cos(angle), -math.sin(angle), 0],
        [math.sin(angle), math.cos(angle), 0],
        [0, 0, 1]
    ]

"""
单位阵 identity(unit) matrix
This code creates a 3x3 identity matrix using the identity function 
from the NumPy library. An identity matrix is a square matrix where 
all elements on the main diagonal are 1, and all other elements are 0. 
"""
def rotation_between_vectors(v1, v2) -> np.ndarray:
    """
    从v1到v2的旋转矩阵
    """
    if np.all(np.isclose(v1, v2)):
        return np.identity(3)
    return rotation_matrix(
        angle=angle_between_vectors(v1, v2),
        axis=np.cross(v1, v2)
    )


def z_to_vector(vector: np.ndarray) -> np.ndarray:
    return rotation_between_vectors(OUT, vector)


def angle_of_vector(vector: Sequence[float]) -> float:
    """
    Returns polar coordinate theta when vector is project on xy plane
    """
    return np.angle(complex(*vector[:2]))


def angle_between_vectors(v1: np.ndarray, v2: np.ndarray) -> float:
    """
    Returns the angle between two 3D vectors.
    This angle will always be btw 0 and pi
    """
    """
    向量之间的夹角
    """
    n1 = get_norm(v1)
    n2 = get_norm(v2)
    cos_angle = np.dot(v1, v2) / np.float64(n1 * n2)
    return math.acos(clip(cos_angle, -1, 1))


def project_along_vector(point: np.ndarray, vector: np.ndarray) -> np.ndarray:
    matrix = np.identity(3) - np.outer(vector, vector)
    return np.dot(point, matrix.T)


def normalize_along_axis(
    array: np.ndarray,
    axis: np.ndarray,
) -> np.ndarray:
    norms = np.sqrt((array * array).sum(axis))
    norms[norms == 0] = 1
    buffed_norms = np.repeat(norms, array.shape[axis]).reshape(array.shape)
    array /= buffed_norms
    return array


def get_unit_normal(
    v1: np.ndarray,
    v2: np.ndarray,
    tol: float = 1e-6
) -> np.ndarray:
    v1 = normalize(v1)
    v2 = normalize(v2)
    cp = cross(v1, v2)
    cp_norm = get_norm(cp)
    if cp_norm < tol:
        # Vectors align, so find a normal to them in the plane shared with the z-axis
        new_cp = cross(cross(v1, OUT), v1)
        new_cp_norm = get_norm(new_cp)
        if new_cp_norm < tol:
            return DOWN
        return new_cp / new_cp_norm
    return cp / cp_norm


###


def thick_diagonal(dim: int, thickness: int = 2) -> np.ndarray:
    row_indices = np.arange(dim).repeat(dim).reshape((dim, dim))
    col_indices = np.transpose(row_indices)
    return (np.abs(row_indices - col_indices) < thickness).astype('uint8')


def compass_directions(n: int = 4, start_vect: np.ndarray = RIGHT) -> np.ndarray:
    angle = TAU / n
    return np.array([
        rotate_vector(start_vect, k * angle)
        for k in range(n)
    ])


def complex_to_R3(complex_num: complex) -> np.ndarray:
    return np.array((complex_num.real, complex_num.imag, 0))


def R3_to_complex(point: Sequence[float]) -> complex:
    return complex(*point[:2])


def complex_func_to_R3_func(
    complex_func: Callable[[complex], complex]
) -> Callable[[np.ndarray], np.ndarray]:
    return lambda p: complex_to_R3(complex_func(R3_to_complex(p)))


def center_of_mass(points: Iterable[npt.ArrayLike]) -> np.ndarray:
    points = [np.array(point).astype("float") for point in points]
    return sum(points) / len(points)


def midpoint(
    point1: Sequence[float],
    point2: Sequence[float]
) -> np.ndarray:
    return center_of_mass([point1, point2])


def line_intersection(
    line1: Sequence[Sequence[float]],
    line2: Sequence[Sequence[float]]
) -> np.ndarray:
    """
    return intersection point of two lines,
    each defined with a pair of vectors determining
    the end points
    """
    x_diff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
    y_diff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])

    def det(a, b):
        return a[0] * b[1] - a[1] * b[0]

    div = det(x_diff, y_diff)
    if div == 0:
        raise Exception("Lines do not intersect")
    d = (det(*line1), det(*line2))
    x = det(d, x_diff) / div
    y = det(d, y_diff) / div
    return np.array([x, y, 0])


def find_intersection(
    p0: npt.ArrayLike,
    v0: npt.ArrayLike,
    p1: npt.ArrayLike,
    v1: npt.ArrayLike,
    threshold: float = 1e-5
) -> np.ndarray:
    """
    Return the intersection of a line passing through p0 in direction v0
    with one passing through p1 in direction v1.  (Or array of intersections
    from arrays of such points/directions).
    For 3d values, it returns the point on the ray p0 + v0 * t closest to the
    ray p1 + v1 * t

    对于2d or 3d空间的直线, 计算交点
    对于3d空间的直线, 可能是异面直线, 那么返回line1上距离line2最近的点
    (交换下line1和line2的顺序, 就可以返回line2上距离line1最近的点)
    """
    p0 = np.array(p0, ndmin=2)
    v0 = np.array(v0, ndmin=2)
    p1 = np.array(p1, ndmin=2)
    v1 = np.array(v1, ndmin=2)
    m, n = np.shape(p0)
    assert(n in [2, 3])

    numer = np.cross(v1, p1 - p0)
    denom = np.cross(v1, v0)
    if n == 3:
        d = len(np.shape(numer))
        new_numer = np.multiply(numer, numer).sum(d - 1)
        new_denom = np.multiply(denom, numer).sum(d - 1)
        numer, denom = new_numer, new_denom

    denom[abs(denom) < threshold] = np.inf  # So that ratio goes to 0 there
    ratio = numer / denom
    ratio = np.repeat(ratio, n).reshape((m, n))
    return p0 + ratio * v0


def get_closest_point_on_line(
    a: np.ndarray,
    b: np.ndarray,
    p: np.ndarray
) -> np.ndarray:
    """
        It returns point x such that
        x is on line ab and xp is perpendicular to ab.
        If x lies beyond ab line, then it returns nearest edge(a or b).
    
        p是线段ab外一点
        求p到线段ab的最短距离
    """
    # x = b + t*(a-b) = t*a + (1-t)*b
    t = np.dot(p - b, a - b) / np.dot(a - b, a - b)
    if t < 0:
        t = 0
    if t > 1:
        t = 1
    return ((t * a) + ((1 - t) * b))


def get_winding_number(points: Iterable[float]) -> float:
    total_angle = 0
    for p1, p2 in adjacent_pairs(points):
        d_angle = angle_of_vector(p2) - angle_of_vector(p1)
        d_angle = ((d_angle + PI) % TAU) - PI
        total_angle += d_angle
    return total_angle / TAU


##

def cross2d(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    if len(a.shape) == 2:
        return a[:, 0] * b[:, 1] - a[:, 1] * b[:, 0]
    else:
        return a[0] * b[1] - b[0] * a[1]


def tri_area(
    a: Sequence[float],
    b: Sequence[float],
    c: Sequence[float]
) -> float:
    return 0.5 * abs(
        a[0] * (b[1] - c[1]) +
        b[0] * (c[1] - a[1]) +
        c[0] * (a[1] - b[1])
    )


def is_inside_triangle(
    p: np.ndarray,
    a: np.ndarray,
    b: np.ndarray,
    c: np.ndarray
) -> bool:
    """
    Test if point p is inside triangle abc
    """
    crosses = np.array([
        cross2d(p - a, b - p),
        cross2d(p - b, c - p),
        cross2d(p - c, a - p),
    ])
    return np.all(crosses > 0) or np.all(crosses < 0)


def norm_squared(v: Sequence[float]) -> float:
    return v[0] * v[0] + v[1] * v[1] + v[2] * v[2]


# TODO, fails for polygons drawn over themselves
def earclip_triangulation(verts: np.ndarray, ring_ends: list[int]) -> list:
    """
    Returns a list of indices giving a triangulation
    of a polygon, potentially with holes

    - verts is a numpy array of points

    - ring_ends is a list of indices indicating where
    the ends of new paths are
    """
    """
    Earclipping is a technique used in polygon triangulation, which is the 
    process of decomposing a polygon into a set of non-overlapping triangles. 
    Triangulation is commonly used in computer graphics, computational geometry, 
    and various other applications. 
    """

    rings = [
        list(range(e0, e1))
        for e0, e1 in zip([0, *ring_ends], ring_ends)
    ]

    def is_in(point, ring_id):
        return abs(abs(get_winding_number([i - point for i in verts[rings[ring_id]]])) - 1) < 1e-5

    def ring_area(ring_id):
        ring = rings[ring_id]
        s = 0
        for i, j in zip(ring[1:], ring):
            s += cross2d(verts[i], verts[j])
        return abs(s) / 2

    # Points at the same position may cause problems
    """
    numpy.core._exceptions.UFuncTypeError: Cannot cast ufunc 'add' output from 
    dtype('float64') to dtype('int64') with casting rule 'same_kind'

    The error you are getting is caused by trying to add two arrays of different 
    data types using the numpy ufunc ‘add’. A ufunc is a function that operates 
    on ndarrays in an element-by-element fashion1. The ‘add’ ufunc is the implementation 
    of the arithmetic addition operator +.

    In your code, you are trying to add verts[i[0]] and (verts[i[1]] - verts[i[0]]) * 1e-6. 
    The first array is of dtype(‘int64’), which means it contains 64-bit integers. 
    The second array is of dtype(‘float64’), which means it contains 64-bit floating-point 
    numbers. These two data types are not compatible for the ‘add’ ufunc, which requires 
    the same kind of data type for both inputs and outputs.

    当传入的顶点是int型的时候会上面的错:
    points = [[0,0,0], [1,0,0], [2,1,0]] 
    vm.set_points(np.array(points))

    最简单的方法:将2改为2.0
    """
    for i in rings:
        # 修改前，有数据类型不匹配风险
        verts[i[0]] += (verts[i[1]] - verts[i[0]]) * 1e-6
        verts[i[-1]] += (verts[i[-2]] - verts[i[-1]]) * 1e-6

        # 修改后
        # verts[i[0]] = np.add(verts[i[0]], (verts[i[1]] - verts[i[0]]) * 1e-6, casting='unsafe')
        # verts[i[-1]] = np.add(verts[i[-1]], (verts[i[-2]] - verts[i[0-1]]) * 1e-6, casting='unsafe')

    # First, we should know which rings are directly contained in it for each ring

    right = [max(verts[rings[i], 0]) for i in range(len(rings))]
    left = [min(verts[rings[i], 0]) for i in range(len(rings))]
    top = [max(verts[rings[i], 1]) for i in range(len(rings))]
    bottom = [min(verts[rings[i], 1]) for i in range(len(rings))]
    area = [ring_area(i) for i in range(len(rings))]

    # The larger ring must be outside
    rings_sorted = list(range(len(rings)))
    rings_sorted.sort(key=lambda x: area[x], reverse=True)

    def is_in_fast(ring_a, ring_b):
        # Whether a is in b
        return reduce(op.and_, (
            left[ring_b] <= left[ring_a] <= right[ring_a] <= right[ring_b],
            bottom[ring_b] <= bottom[ring_a] <= top[ring_a] <= top[ring_b],
            is_in(verts[rings[ring_a][0]], ring_b)
        ))

    chilren = [[] for i in rings]
    ringenum = ProgressDisplay(
        enumerate(rings_sorted),
        total=len(rings),
        leave=False,
        ascii=True if platform.system() == 'Windows' else None,
        dynamic_ncols=True,
        desc="SVG Triangulation",
        delay=3,
    )
    for idx, i in ringenum:
        for j in rings_sorted[:idx][::-1]:
            if is_in_fast(i, j):
                chilren[j].append(i)
                break

    res = []

    # Then, we can use earcut for each part
    used = [False] * len(rings)
    for i in rings_sorted:
        if used[i]:
            continue
        v = rings[i]
        ring_ends = [len(v)]
        for j in chilren[i]:
            used[j] = True
            v += rings[j]
            ring_ends.append(len(v))
        res += [v[i] for i in earcut(verts[v, :2], ring_ends)]

    return res
