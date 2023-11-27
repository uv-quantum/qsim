from __future__ import annotations
from dataclasses import dataclass
from functools import reduce
from typing import List
from multimethod import multimethod
import math

@dataclass
class Qbits:
    vector : List[float] #column vector
    # tensor product: multiply each element of another array by
    # all the elements of this array
    @multimethod
    def __mul__(self, q: Qbits) -> Qbits:
        v = []
        for x in q.vector:
            for y in self.vector:
                v.append(x * y)
        return Qbits(v)
    @multimethod
    def __mul__(self, s: float) -> Qbits:
        return Qbits([s * x for x in self.vector])
    def __rmul__(self, s: float) -> Qbits:
        return self.__mul__(s)
    
@dataclass
class Qbit:
    vector : List[float] #column vector
    def __mul_qbit(self, q: Qbit) -> Qbits:
        v = [0.] * 4
        v[0] = self.vector[0] * q.vector[0]
        v[1] = self.vector[1] * q.vector[0]
        v[2] = self.vector[0] * q.vector[1]
        v[3] = self.vector[1] * q.vector[1]
        return Qbits(v)
    def __mulfloat(self, s: float) -> Qbit:
        return Qbit([s * self.vector[0], s * self.vector[1]])
    def __rmul__(self, s: float) -> Qbit:
        return self.__mulfloat(s)
    def __mul__(self, d):
        if type(d) == type(float):
            return self.__mulfloat(d)
        else:
            return self.__mul_qbit(d)

@dataclass
class Gate:
    matrix : List[List[float]]
    # 2x2 Matrix x  2 d column vector
    def __mul_qbit(self, q: Qbit) -> Qbit:
        return Qbit([self.matrix[0][0] * q.vector[0] + self.matrix[0][1] * q.vector[1], 
                    self.matrix[1][0] * q.vector[0] + self.matrix[1][1] * q.vector[1]])
    # n x n matrix * 1 x n column vector
    def __mul_qbits(self, q: Qbits) -> Qbits:
        v = [0.] * len(self.matrix)
        for r in range(len(self.matrix)):
            for c in range(len(self.matrix[0])):
                v[r] += self.matrix[r][c] * q.vector[c]
        return Qbits(v)

    def __mul__(self, d):
        if type(d) == type(Qbit):
            return self.__mul_qbit(d)
        else:
            return self.__mul_qbit(d)
