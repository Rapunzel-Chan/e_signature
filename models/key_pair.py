"""
Модель ключевой пары
SOLID: Single Responsibility - только хранение данных
"""

from dataclasses import dataclass
from core.elliptic import Point


@dataclass
class KeyPair:
    """Ключевая пара для ЭЦП"""
    private_key: int  # секретный ключ d
    public_key: Point  # открытый ключ Q = d * P

    def __str__(self) -> str:
        return f"KeyPair(private={self.private_key}, public={self.public_key})"

    def to_files(self, private_path: str, public_path: str) -> None:
        """Сохраняет ключи в файлы"""
        # Сохраняем секретный ключ
        with open(private_path, 'w') as f:
            f.write(str(self.private_key))

        # Сохраняем открытый ключ (x и y на отдельных строках)
        with open(public_path, 'w') as f:
            f.write(f"{self.public_key.x}\n{self.public_key.y}")

    @classmethod
    def from_files(cls, private_path: str, public_path: str, params) -> 'KeyPair':
        """Загружает ключи из файлов"""
        with open(private_path, 'r') as f:
            private_key = int(f.read().strip())

        with open(public_path, 'r') as f:
            x = int(f.readline().strip())
            y = int(f.readline().strip())

        from core.elliptic import Point
        public_key = Point(x, y, params.a, params.b, params.p)

        return cls(private_key, public_key)
