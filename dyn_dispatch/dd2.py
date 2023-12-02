# Minimal Multidispatch example.
# Type safe: if types not included in overload set exception is raised
# Author: Ugo Varetto
# License SPDX: UPL-1.0 (Permissive license)

import sys


def __create_overload_table(obj):
    if getattr(obj, '__overload_table', None):
        return
    else:
        setattr(obj, '__overload_table', dict())


__create_overload_table_fun = __create_overload_table

def set_create_overload_table_fun(f):
    global __create_overload_table_fun
    __create_overload_table_fun = f



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
        if not getattr(self, '__overload_table', None):
            raise AttributeError(f"No overloaded methods found for '{f.__name__}'")
        if key not in self.__overload_table:
            raise TypeError(f"No overload found for method '{f.__name__}' with parameter type(s) '{key[1]}'")
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
        if not getattr(module, '__overload_table', None):
            raise AttributeError(f"No overloaded methods found for '{f.__name__}'")
        if key not in module.__overload_table:
            raise TypeError(f"No overload found for method '{f.__name__}' with parameter type(s) '{key[1]}'")
        return module.__overload_table[key](*args)

    wrapper.__name__ = f.__name__
    return wrapper


### Class
class AClass:
    def __init__(self, i: int, j: int = 0):
        self.i = i
        self.j = j

    @dyn_method
    def set(self, *_):
        ...


@dyn_dispatch(AClass, 'set', int)
def set_int(self, i: int):
    print("set_int called")
    self.i = i


@dyn_dispatch(AClass, 'set', float)
def set_float(self, f: float):
    print("set_float called")
    self.set(int(f))


@dyn_dispatch(AClass, 'set', str)
def set_str(self, s: str):
    print("set_str called")
    self.set(int(s))


@dyn_dispatch(AClass, 'set', int, int)
def set_int_int(self, i: int, j: int):
    print("set_int_int called")
    self.i, self.j = i, j


### Function

@dyn_fun
def double(*_):
    pass


@dyn_dispatch_f('double', float)
def double_float(f: float) -> float:
    print("double_float called")
    return 2 * f


@dyn_dispatch_f('double', int)
def double_int(i: int) -> int:
    print("double_int called")
    return 2 * i


@dyn_dispatch_f('double', str)
def double_str(s: str) -> str:
    print("double_str called")
    return s + s


if __name__ == "__main__":
    print("-" * 10)
    print("Class")
    print(AClass.__overload_table)
    try:
        a = AClass(2)
        print(a.i)
        print()
        a.set(1.0)
        print(a.i)
        a.set("10")
        print(a.i)
        a.set(6, 7)
        print(a.i, a.j)
        a.set(6.6, 6.9)  # trigger exception no (float, float) overload for set
        # a.set(True) #trigger exception no (bool) overload for set
    except TypeError as e:
        print(e, file=sys.stderr)
    print()
    print("-" * 10)
    print("\nFunction")
    print(__overload_table)
    try:
        print(double(1.4))
        print(double(3))
        print(double('string'))
        print(double(1, 2))
    except TypeError as e:
        print(e, file=sys.stderr)
