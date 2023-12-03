from __future__ import annotations
from dataclasses import dataclass

Elem = float  # complex


def is_zero(x: float):
    return x < 1e-9


@dataclass(frozen=True)
class Vector:
    v: list[Elem]

    def __mul__(self, x: Elem) -> Vector:
        return Vector([x * e for e in self.v])

    def __len__(self) -> int:
        return len(self.v)

    def __getitem__(self, i: int) -> Elem:
        return self.v[i]

    def __matmul__(self, w: Vector) -> Vector:
        N = len(self.v)
        v: Vector = Vector([])
        for other in range(N):
            for this in range(N):
                v.v.append(self.v[this] * w.v[other])
        return v

    def __rmul__(self, x: Elem) -> Vector:
        return self.__mul__(x)

    def __add__(self, v: Vector) -> Vector:
        return Vector([x + y for x in self.v for y in v.v])

    def __sub__(self, v: Vector) -> Vector:
        return Vector([x - y for x in self.v for y in v.v])


@dataclass
class Matrix:
    m: list[list[Elem]]

    def __getitem__(self, i: tuple[int, int]) -> Elem:
        return self.m[i[0]][i[1]]

    def __setitem__(self, i: tuple[int], e: Elem) -> None:
        self.m[i[0]][i[1]] = e

    def num_rows(self) -> int:
        return len(self.m)

    def num_cols(self) -> int:
        return len(self.m[0]) if self.num_rows() else 0

    def place(self, roff: int, coff: int, m: Matrix) -> None:
        for i in range(m.num_rows()):
            for j in range(m.num_cols()):
                self[roff + i, coff + j] = m[i, j]

    @classmethod
    def max_eps(cls, m1: Matrix | Vector, m2: Matrix | Vector) -> float:
        e = 0.
        if isinstance(m1, Matrix) and isinstance(m2, Matrix):
            for r in range(m1.num_rows()):
                for c in range(m1.num_cols()):
                    v = abs(m1[r, c] - m2[r, c])
                    e = v if v > e else e
        elif isinstance(m1, Vector) and isinstance(m2, Vector):
            for i in range(len(m1)):
                v = abs(m1[i] - m2[i])
                e = v if v > e else e
        else:
            raise Exception(f"Invalid data types {type(m1)} {type(m2)}")
        return e

    @classmethod
    def new(cls, rows: int, cols: int) -> Matrix:
        m: list[list[Elem]] = []
        for _ in range(rows):
            l: list[Elem] = []
            for _ in range(cols):
                l.append(Elem())
            m.append(l)
        return Matrix(m)

    @classmethod
    def identity(cls, rows: int, cols: int) -> Matrix:
        m = Matrix.new(rows, cols)
        for i in range(rows):
            m[i, i] = 1.
        return m

    def __matvec(self: Matrix, v: Vector) -> Vector:
        ret: list[float] = []
        for r in range(self.num_rows()):
            x = 0.
            for c in range(self.num_cols()):
                x += self[r, c] * v[c]
            ret.append(x)
        return Vector(ret)

    def __matmul(self: Matrix, m: Matrix) -> Matrix:
        num_rows = self.num_rows()
        num_cols = self.num_cols()
        mat = Matrix.new(num_rows, num_cols)
        for r in range(num_rows):
            for c in range(num_cols):
                x = 0.
                for i in range(num_cols):
                    x += self[r, i] * m[i, c]
                mat[r, c] = x
        return mat

    def __matmul__(self, mv: Matrix | Vector) -> Matrix | Vector:
        if isinstance(mv, Matrix):
            return self.__matmul(mv)
        else:
            return self.__matvec(mv)

    def __mul__(self, x: Elem) -> Matrix:
        num_rows = self.num_rows()
        num_cols = self.num_cols()
        m = Matrix.new(num_rows, num_cols)
        for r in range(num_rows):
            for c in range(num_cols):
                m.m[r][c] = self.m[r][c] * x
        return m

    def __rmul__(self: Matrix, x: Elem) -> Matrix:
        return self.__mul__(x)

    def __mod__(self, m: Matrix) -> Matrix:
        num_rows = self.num_rows()
        num_cols = self.num_cols()
        t = Matrix.new(2 * num_rows, 2 * num_cols)
        for i in range(num_rows):
            for j in range(num_cols):
                roff = 2 * i
                coff = 2 * j
                s = m * self.m[i][j]
                t.place(roff, coff, s)
        return t

    def transpose(self) -> Matrix:
        m = Matrix.new(self.num_rows(), self.num_cols())
        for i in range(self.num_rows()):
            for j in range(self.num_cols()):
                m.m[j][i] = self.m[i][j]
        return m

    def conj(self) -> Matrix:
        # conjugate, return self for now
        return self

    def dagger(self) -> Matrix:
        return self.transpose().conj()


@dataclass
class UnitaryMatrix(Matrix):
    def __post_init__(self):
        e = Matrix.max_eps(self.dagger() @ self,
                           Matrix.identity(self.num_rows(), self.num_cols()))
        if not is_zero(e):
            raise Exception("Non unitary matrix")
