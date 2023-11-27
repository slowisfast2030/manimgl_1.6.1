import inspect
import itertools as it


def get_all_descendent_classes(Class):
    awaiting_review = [Class]
    result = []
    while awaiting_review:
        Child = awaiting_review.pop()
        awaiting_review += Child.__subclasses__()
        result.append(Child)
    return result


def filtered_locals(caller_locals):
    result = caller_locals.copy()
    ignored_local_args = ["self", "kwargs"]
    for arg in ignored_local_args:
        result.pop(arg, caller_locals)
    return result

"""
class BaseClass:
    CONFIG = {'color': 'blue', 'size': 10}

class SubClass(BaseClass):
    CONFIG = {'size': 15, 'shape': 'circle'}

class SubSubClass(SubClass):
    CONFIG = {'color': 'red'}

# Assume the definitions of digest_config and merge_dicts_recursively are available

# Instantiate the object
obj = SubSubClass()

# Additional configuration provided at instantiation
kwargs = {'size': 20, 'opacity': 0.5}
caller_locals = {}  # In this example, there are no additional locals

# Apply the configuration
digest_config(obj, kwargs, caller_locals)

# Print the final configuration of obj
print(obj.__dict__)

# {'color': 'red', 'size': 20, 'shape': 'circle', 'opacity': 0.5}
"""
def digest_config(obj, kwargs, caller_locals={}):
    """
    Sets init args and CONFIG values as local variables

    The purpose of this function is to ensure that all
    configuration of any object is inheritable, able to
    be easily passed into instantiation, and is attached
    as an attribute of the object.
    """
    """
    将self类的CONFIG字典(当前类和所有父类)和参数(当前类的kwargs)初始化为self的属性
    """
    """
    3b1b对python语言底层机制的掌握程度远超一般人
    """

    # Assemble list of CONFIGs from all super classes
    classes_in_hierarchy = [obj.__class__]
    static_configs = []
    # 从当前类开始，将当前类和所有父类的CONFIG字典加入static_configs
    # 需要注意的是，所有类的CONFIG字典的排列顺序
    # 子类的CONFIG字典在前，父类的CONFIG字典在后
    while len(classes_in_hierarchy) > 0:
        Class = classes_in_hierarchy.pop()
        classes_in_hierarchy += Class.__bases__
        if hasattr(Class, "CONFIG"):
            static_configs.append(Class.CONFIG)

    # Order matters a lot here, first dicts have higher priority
    caller_locals = filtered_locals(caller_locals)
    # 将kwargs、caller_locals、obj.__dict__、static_configs中的字典合并
    # 顺序很重要，越靠前的字典优先级越高，即
    # kwargs > caller_locals > obj.__dict__ > static_configs
    all_dicts = [kwargs, caller_locals, obj.__dict__]
    all_dicts += static_configs
    obj.__dict__ = merge_dicts_recursively(*reversed(all_dicts))


def merge_dicts_recursively(*dicts):
    """
    Creates a dict whose keyset is the union of all the
    input dictionaries.  The value for each key is based
    on the first dict in the list with that key.

    dicts later in the list have higher priority

    When values are dictionaries, it is applied recursively
    """
    """
    需要注意, 传递给当前函数的dicts中的字典的排列顺序
    static_configs, obj.__dict__, caller_locals, kwargs
    """
    result = dict()
    all_items = it.chain(*[d.items() for d in dicts])
    # all_items中的字典的排列顺序
    # static_configs, obj.__dict__, caller_locals, kwargs
    # 如果不同的字典有相同的key，那么排列靠后的字典的key-value会覆盖排列靠前的字典的key-value
    # 所以，kwargs中的key-value优先级最高
    for key, value in all_items:
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts_recursively(result[key], value)
        else:
            result[key] = value
    return result


def soft_dict_update(d1, d2):
    """
    Adds key values pairs of d2 to d1 only when d1 doesn't
    already have that key
    """
    for key, value in list(d2.items()):
        if key not in d1:
            d1[key] = value


def digest_locals(obj, keys=None):
    caller_locals = filtered_locals(
        inspect.currentframe().f_back.f_locals
    )
    if keys is None:
        keys = list(caller_locals.keys())
    for key in keys:
        setattr(obj, key, caller_locals[key])

# Occasionally convenient in order to write dict.x instead of more laborious
# (and less in keeping with all other attr accesses) dict["x"]


class DictAsObject(object):
    def __init__(self, dict):
        self.__dict__ = dict
