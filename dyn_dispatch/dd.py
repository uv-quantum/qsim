# Minimal Multidispatch example.
# Type safe: if types not included in overload set exception is raised
# Author: Ugo Varetto
# License SPDX: UPL-1.0 (Permissive license)

import sys


def __create_overload_table(obj):
    if getattr(obj, "__overload_table", None):
        return
    else:
        setattr(obj, "__overload_table", dict())


def dyn_dispatch(class_type, method_name, *types):
    # types: types used to specify the overload keys, no need to match signature
    # if signature too long or accepting a variable number of parameters just
    # use as few as needed to make the key unique
    def decorator(f):
        __create_overload_table(class_type)
        class_type.__overload_table[(method_name, tuple(t for t in types))] = f

        def wrapper(*args):
            return f(*args)

        wrapper.__name__ = method_name
        return wrapper

    return decorator


def dyn_method(f):
    def wrapper(self, *args):
        key = (f.__name__, tuple(type(t) for t in args))
        # error checking, remove for faster execution
        if not getattr(self, "__overload_table", None):
            raise AttributeError(f"No overloaded methods found for '{f.__name__}'")
        if key not in self.__overload_table:
            raise TypeError(
                f"No overload found for method '{f.__name__}' with parameter type(s) '{key[1]}'"
            )
        return self.__overload_table[key](self, *args)

    wrapper.__name__ = f.__name__
    return wrapper


def dyn_dispatch_f(fun_name, *types):
    # types: types used to specify the overload keys, no need to match signature
    # if signature too long or accepting a variable number of parameters just
    # use as few as needed to make the key unique
    def decorator(f):
        module = sys.modules[__name__]
        __create_overload_table(module)
        module.__overload_table[(fun_name, tuple(t for t in types))] = f

        def wrapper(*args):
            return f(*args)

        wrapper.__name__ = fun_name
        return wrapper

    return decorator


def dyn_fun(f):
    def wrapper(*args):
        module = sys.modules[__name__]
        key = (f.__name__, tuple(type(t) for t in args))
        # error checking, remove for faster execution
        if not getattr(module, "__overload_table", None):
            raise AttributeError(f"No overloaded methods found for '{f.__name__}'")
        if key not in module.__overload_table:
            raise TypeError(
                f"No overload found for method '{f.__name__}' with parameter type(s) '{key[1]}'"
            )
        return module.__overload_table[key](*args)

    wrapper.__name__ = f.__name__
    return wrapper


################################################################################
