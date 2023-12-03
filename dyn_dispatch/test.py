from __future__ import annotations
from dd import *


def test():
    # Declarations

    ### Class
    class AClass:
        def __init__(self, i: int, j: int = 0):
            self.i = i
            self.j = j

        @dyn_method
        def __add__(self, *_) -> AClass:
            ...

        @dyn_method
        def set(self, *_):
            ...

    @dyn_dispatch(AClass, "__add__", AClass)
    def add_obj(self, other: AClass) -> AClass:
        return AClass(self.i + other.i, self.j + other.j)

    @dyn_dispatch(AClass, "set", int)
    def set_int(self, i: int):
        # print("set_int called")
        self.i = i

    @dyn_dispatch(AClass, "set", float)
    def set_float(self, f: float):
        # print("set_float called")
        self.set(int(f))

    @dyn_dispatch(AClass, "set", str)
    def set_str(self, s: str):
        # print("set_str called")
        self.set(int(s))

    @dyn_dispatch(AClass, "set", int, int)
    def set_int_int(self, i: int, j: int):
        # print("set_int_int called")
        self.i, self.j = i, j

    ### Function

    @dyn_fun
    def double(*_):
        pass

    @dyn_dispatch_f("double", float)
    def double_float(f: float) -> float:
        # print("double_float called")
        return 2 * f

    @dyn_dispatch_f("double", int)
    def double_int(i: int) -> int:
        # print("double_int called")
        return 2 * i

    @dyn_dispatch_f("double", str)
    def double_str(s: str) -> str:
        # print("double_str called")
        return s + s

    # Tests
    a = AClass(1, 2)
    b = AClass(5, 6)
    c = a + b
    assert c.i == a.i + b.i
    assert c.j == a.j + b.j

    a.set(2)
    assert a.i == 2
    a.set(3.1)
    assert a.i == 3
    a.set("4")
    assert a.i == 4
    a.set(10, 20)
    assert a.i == 10 and a.j == 20
    try:
        a.set(10.1, 20.3)
        assert False
    except:
        assert True

    assert double(3) == double_int(3)
    assert double(3.2) == double_float(3.2)
    assert double("6") == double_str("6")

    try:
        _ = double(True)
        assert False
    except:
        assert True


if __name__ == "__main__":
    test()
    print("OK")
