from __future__ import annotations

from typing import Callable, Iterable, Sequence, TypeVar

import numpy as np

T = TypeVar("T")
S = TypeVar("S")


def remove_list_redundancies(l: Iterable[T]) -> list[T]:
    """
    Used instead of list(set(l)) to maintain order
    Keeps the last occurrence of each element
    """
    reversed_result = []
    used = set()
    for x in reversed(l):
        if x not in used:
            reversed_result.append(x)
            used.add(x)
    reversed_result.reverse()
    return reversed_result


def list_update(l1: Iterable[T], l2: Iterable[T]) -> list[T]:
    """
    Used instead of list(set(l1).update(l2)) to maintain order,
    making sure duplicates are removed from l1, not l2.
    """
    return [e for e in l1 if e not in l2] + list(l2)


def list_difference_update(l1: Iterable[T], l2: Iterable[T]) -> list[T]:
    return [e for e in l1 if e not in l2]


def adjacent_n_tuples(objects: Iterable[T], n: int) -> zip[tuple[T, T]]:
    return zip(*[
        [*objects[k:], *objects[:k]]
        for k in range(n)
    ])


def adjacent_pairs(objects: Iterable[T]) -> zip[tuple[T, T]]:
    return adjacent_n_tuples(objects, 2)


def batch_by_property(
    items: Iterable[T],
    property_func: Callable[[T], S]
) -> list[tuple[T, S]]:
    """
    Takes in a list, and returns a list of tuples, (batch, prop)
    such that all items in a batch have the same output when
    put into property_func, and such that chaining all these
    batches together would give the original list (i.e. order is
    preserved)
    """
    batch_prop_pairs = []
    curr_batch = []
    curr_prop = None
    for item in items:
        prop = property_func(item)
        if prop != curr_prop:
            # Add current batch
            if len(curr_batch) > 0:
                batch_prop_pairs.append((curr_batch, curr_prop))
            # Redefine curr
            curr_prop = prop
            curr_batch = [item]
        else:
            curr_batch.append(item)
    if len(curr_batch) > 0:
        batch_prop_pairs.append((curr_batch, curr_prop))
    return batch_prop_pairs


def listify(obj) -> list:
    if isinstance(obj, str):
        return [obj]
    try:
        return list(obj)
    except TypeError:
        return [obj]


def resize_array(nparray: np.ndarray, length: int) -> np.ndarray:
    """
    np.resize函数会复制或者截断原数组, 使得新数组的长度为length

    points = np.array([[1,2,3], [4,5,6], [7,8,9]])

    np.resize(points, (2, 3))
    array([[1, 2, 3],
           [4, 5, 6]])

    np.resize(points, (5, 3))
    array([[1, 2, 3],
           [4, 5, 6],
           [7, 8, 9],
           [1, 2, 3],
           [4, 5, 6]])

    np.resize(points, (3, 5))
    array([[1, 2, 3, 4, 5],
           [6, 7, 8, 9, 1],
           [2, 3, 4, 5, 6]])
    """
    if len(nparray) == length:
        return nparray
    return np.resize(nparray, (length, *nparray.shape[1:]))


def resize_preserving_order(nparray: np.ndarray, length: int) -> np.ndarray:
    if len(nparray) == 0:
        return np.zeros((length, *nparray.shape[1:]))
    if len(nparray) == length:
        return nparray
    indices = np.arange(length) * len(nparray) // length
    return nparray[indices]


"""
points = np.array([[1,2,3], [4,5,6]])
resize_with_interpolation(points, 6)

array([[1. , 2. , 3. ],
       [1.6, 2.6, 3.6],
       [2.2, 3.2, 4.2],
       [2.8, 3.8, 4.8],
       [3.4, 4.4, 5.4],
       [4. , 5. , 6. ]])
"""
def resize_with_interpolation(nparray: np.ndarray, length: int) -> np.ndarray:
    """
    这是一个典型的黑箱
    有一些黑箱是可以跳过的
    """
    if len(nparray) == length:
        return nparray
    if length == 0:
        return np.zeros((0, *nparray.shape[1:]))
    cont_indices = np.linspace(0, len(nparray) - 1, length)
    return np.array([
        (1 - a) * nparray[lh] + a * nparray[rh]
        for ci in cont_indices
        for lh, rh, a in [(int(ci), int(np.ceil(ci)), ci % 1)]
    ])


def make_even(
    iterable_1: Sequence[T], 
    iterable_2: Sequence[S]
) -> tuple[list[T], list[S]]:
    len1 = len(iterable_1)
    len2 = len(iterable_2)
    if len1 == len2:
        return iterable_1, iterable_2
    new_len = max(len1, len2)
    return (
        [iterable_1[(n * len1) // new_len] for n in range(new_len)],
        [iterable_2[(n * len2) // new_len] for n in range(new_len)]
    )


def hash_obj(obj: object) -> int:
    if isinstance(obj, dict):
        new_obj = {k: hash_obj(v) for k, v in obj.items()}
        return hash(tuple(frozenset(sorted(new_obj.items()))))

    if isinstance(obj, (set, tuple, list)):
        return hash(tuple(hash_obj(e) for e in obj))

    return hash(obj)
