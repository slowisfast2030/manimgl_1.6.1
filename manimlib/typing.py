from typing import TYPE_CHECKING

"""
整份文件都是添加的, 并做了很多修改
因为很多写法都是基于python3.10+版本
"""

if TYPE_CHECKING:
    from typing import Union, Tuple, Literal, Iterable, Dict
    from typing_extensions import Annotated

    from colour import Color
    import numpy as np
    import re
    
    try:
        from typing import Self
    except ImportError:
        from typing_extensions import Self

    # Abbreviations for a common types
    ManimColor = Union[str, Color, None]
    RangeSpecifier = Union[Tuple[float, float, float], Tuple[float, float]]


    Span = Tuple[int, int]
    SingleSelector = Union[
        str,
        re.Pattern,
        Tuple[Union[int, None], Union[int, None]],
    ]
    Selector = Union[SingleSelector, Iterable[SingleSelector]]

    UniformDict = Dict[str, Union[float, bool, np.ndarray, tuple]]


    # These are various alternate names for np.ndarray meant to specify
    # certain shapes.
    # 
    # In theory, these annotations could be used to check arrays sizes
    # at runtime, but at the moment nothing actually uses them, and
    # the names are here primarily to enhance readibility and allow
    # for some stronger type checking if numpy has stronger typing
    # in the future
    FloatArray = np.ndarray[int, np.dtype[np.float64]]
    Vect2 = Annotated[FloatArray, Literal[2]]
    Vect3 = Annotated[FloatArray, Literal[3]]
    Vect4 = Annotated[FloatArray, Literal[4]]
    VectN = Annotated[FloatArray, Literal["N"]]
    Matrix3x3 = Annotated[FloatArray, Literal[3, 3]]
    Vect2Array = Annotated[FloatArray, Literal["N", 2]]
    Vect3Array = Annotated[FloatArray, Literal["N", 3]]
    Vect4Array = Annotated[FloatArray, Literal["N", 4]]
    VectNArray = Annotated[FloatArray, Literal["N", "M"]]
