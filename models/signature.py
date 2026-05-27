"""
Модель цифровой подписи
SOLID: Single Responsibility
"""

from dataclasses import dataclass


@dataclass
class Signature:
    """Цифровая подпись (r, s)"""
    r: int
    s: int

    def __post_init__(self):
        if self.r < 0 or self.s < 0:
            raise ValueError("r и s должны быть неотрицательными")

    def to_bytes(self, byte_len: int) -> bytes:
        """Конвертирует подпись в байты"""
        return self.r.to_bytes(byte_len, 'big') + self.s.to_bytes(byte_len, 'big')

    @classmethod
    def from_bytes(cls, data: bytes, byte_len: int) -> 'Signature':
        """Создает подпись из байт"""
        if len(data) != 2 * byte_len:
            raise ValueError(f"Неверный размер данных: {len(data)}, ожидается {2 * byte_len}")

        r = int.from_bytes(data[:byte_len], 'big')
        s = int.from_bytes(data[byte_len:], 'big')
        return cls(r, s)

    @classmethod
    def from_components(cls, r: int, s: int) -> 'Signature':
        """Создает подпись из компонент"""
        return cls(r, s)

    def __str__(self) -> str:
        return f"Signature(r={self.r}, s={self.s})"
