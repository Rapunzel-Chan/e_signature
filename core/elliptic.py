"""
Эллиптическая кривая над конечным полем
SOLID: Single Responsibility - только математика кривой
"""

from dataclasses import dataclass
from typing import Optional
from core.arithmetic import ModularArithmetic


@dataclass(frozen=True)
class Point:
    """
    Точка на эллиптической кривой
    Неизменяемый объект (immutable) для безопасности
    """
    x: Optional[int]
    y: Optional[int]
    a: int
    b: int
    p: int
    is_infinity: bool = False

    def __post_init__(self):
        """Валидация точки"""
        if self.is_infinity:
            return
        if self.x is None or self.y is None:
            raise ValueError("Координаты точки не могут быть None")

        # Проверка, что точка лежит на кривой: y^2 = x^3 + a*x + b (mod p)
        left = (self.y * self.y) % self.p
        right = (self.x * self.x * self.x + self.a * self.x + self.b) % self.p
        if left != right:
            raise ValueError(f"Точка ({self.x}, {self.y}) не лежит на кривой")

    @staticmethod
    def infinity(a: int, b: int, p: int) -> 'Point':
        """Создает бесконечно удаленную точку (нейтральный элемент)"""
        return Point(None, None, a, b, p, is_infinity=True)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Point):
            return False
        if self.is_infinity and other.is_infinity:
            return True
        if self.is_infinity or other.is_infinity:
            return False
        return self.x == other.x and self.y == other.y

    def __neg__(self) -> 'Point':
        """Обратная точка: -P = (x, -y mod p)"""
        if self.is_infinity:
            return self
        return Point(self.x, (-self.y) % self.p, self.a, self.b, self.p)

    def __add__(self, other: 'Point') -> 'Point':
        """Сложение двух точек на кривой"""
        # P + O = P
        if self.is_infinity:
            return other
        if other.is_infinity:
            return self

        # P + (-P) = O
        if self.x == other.x and (self.y + other.y) % self.p == 0:
            return Point.infinity(self.a, self.b, self.p)

        # Вычисление наклона (лямбды)
        if self == other:
            # Удвоение точки
            if self.y == 0:
                raise ValueError("Невозможно удвоить точку с y=0")
            numerator = (3 * self.x * self.x + self.a) % self.p
            denominator = (2 * self.y) % self.p
        else:
            # Сложение разных точек
            numerator = (other.y - self.y) % self.p
            denominator = (other.x - self.x) % self.p

        lam = numerator * ModularArithmetic.modinv(denominator, self.p) % self.p

        # Вычисление координат
        x3 = (lam * lam - self.x - other.x) % self.p
        y3 = (lam * (self.x - x3) - self.y) % self.p

        return Point(x3, y3, self.a, self.b, self.p)

    def __mul__(self, scalar: int) -> 'Point':
        """Умножение точки на скаляр (double-and-add алгоритм)"""
        if scalar < 0:
            raise ValueError("Скаляр должен быть неотрицательным")

        result = Point.infinity(self.a, self.b, self.p)
        base = self

        while scalar > 0:
            if scalar & 1:
                result = result + base
            base = base + base
            scalar >>= 1

        return result

    def __rmul__(self, scalar: int) -> 'Point':
        return self.__mul__(scalar)

    def __str__(self) -> str:
        if self.is_infinity:
            return "∞"
        return f"({self.x}, {self.y})"
