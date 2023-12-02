# Minimal Class Multidispatch example.
# Type safe: if types not included in overload set exception is raised
# Author: Ugo Varetto
# License SPDX: UPL-1.0 (Permissive license)

import sys
def dyndisp(*types): 
    def decorator(f):
        C = types[0]
        type_names = "_".join([t.__name__ for t in types[1:] ])
        t = type_names
        fn = f.__name__ + '_' + t
        f.__name__ = fn
        f.__qualname__ = C.__name__ + '.' + f.__name__
        setattr(C,fn,f)
        def wrapper(*args, **kwargs):
            return f(*args, **kwargs)
        wrapper.__name__ = f.__qualname__
        return wrapper
    return decorator

def dynmethod(f):
    def wrapper(*args):
        self = args[0]
        types = [type(t).__name__ for t in args[1:] ]
        type_names = "_".join(types)
        method_name = f.__name__ + '_' + type_names
        method = getattr(self, method_name, None)
        if not method:
            raise TypeError(f"No '{f.__qualname__}' overload for type(s)' {types}'")
        else:
            return method(*args[1:])
    wrapper.__name__ = f.__name__
    return wrapper

class AClass:
    # in-class overload <method name>_<type names>
    def set_int(self, i: int) -> None:
        print(f"{self.set_int.__qualname__} called")
        self.i = i
    def set_str(self, i: str) -> None:
        print(f"{self.set_str.__qualname__} called")
        self.i = int(i)
    def __init__(self, i: int, j: int = 0):
        self.i = i
        self.j = j
    # automatically invokes method by appending a _<type 1 name>_<type 2 name>... string to 
    # current method name
    @dynmethod
    def set(self, *_, **__) -> None:
        del (_,__) # avoid unused variable warning
        pass

# Overloaded method <method name>_<type names> added to class
# specified as first decorator parameter
@dyndisp(AClass, float)
def set(self: AClass, f: float):
    print(f"{set.__name__} called")
    self.set(int(f))

@dyndisp(AClass, int, int)
def set(self: AClass, i: int, j: int):
    print(f"{set.__name__} called")
    self.i = i
    self.j = j

if __name__ == "__main__":
    print([ x for x in dir(AClass) if x[0] != '_'])
    try:
        a = AClass(2)
        print(a.i)
        print()
        a.set(1.0)
        print(a.i)
        a.set("10")
        print(a.i)
        a.set(4)
        print(a.i)
        a.set(6,7)
        print(a.i, a.j)
        a.set(6.6, 6.9) #trigger exception
        #a.set(True) #trigger exception
    except TypeError as e:
        print(e, file=sys.stderr)

