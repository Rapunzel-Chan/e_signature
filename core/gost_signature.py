"""
ГОСТ Р 34.10-2012 - Электронная цифровая подпись
SOLID: Single Responsibility - только подпись и проверка
"""

import random
from typing import Tuple, Optional
from core.elliptic import Point
from core.arithmetic import ModularArithmetic
from core.gost_hash import gost_hash
from models.curve_params import CurveParams
from models.key_pair import KeyPair
from models.signature import Signature


class GOST3410_2012:
    """
    Реализация ГОСТ Р 34.10-2012
    """

    def __init__(self, params: CurveParams):
        self.params = params
        self._base_point = Point(
            params.Px, params.Py,
            params.a, params.b, params.p
        )

    @property
    def base_point(self) -> Point:
        """Базовая точка P"""
        return self._base_point

    def _hash_to_int(self, message: bytes) -> int:
        """Вычисляет хэш и приводит к модулю q"""
        h = gost_hash(message, self.params.hash_len)
        e = h % self.params.q
        return 1 if e == 0 else e

    def generate_key_pair(self, seed: Optional[int] = None) -> KeyPair:
        """
        Генерирует ключевую пару (d, Q)

        Returns:
            KeyPair: пара ключей
        """
        if seed is not None:
            random.seed(seed)

        # Секретный ключ: 0 < d < q
        d = random.randint(1, self.params.q - 1)

        # Открытый ключ: Q = d * P
        Q = d * self._base_point

        return KeyPair(d, Q)

    def sign(self, message: bytes, private_key: int) -> Signature:
        """
        Формирует электронную подпись

        Args:
            message: подписываемое сообщение
            private_key: секретный ключ d

        Returns:
            Signature: подпись (r, s)
        """
        e = self._hash_to_int(message)

        while True:
            # Генерируем случайное k (1 < k < q)
            k = random.randint(1, self.params.q - 1)

            # Вычисляем C = k * P
            C = k * self._base_point

            # r = x_C mod q
            r = C.x % self.params.q
            if r == 0:
                continue

            # s = (r*d + k*e) mod q
            s = (r * private_key + k * e) % self.params.q
            if s == 0:
                continue

            return Signature(r, s)

    def verify(self, message: bytes, signature: Signature, public_key: Point) -> bool:
        """
        Проверяет электронную подпись

        Args:
            message: сообщение
            signature: подпись (r, s)
            public_key: открытый ключ Q

        Returns:
            bool: True если подпись верна
        """
        r, s = signature.r, signature.s

        # Проверяем 0 < r < q и 0 < s < q
        if not (0 < r < self.params.q and 0 < s < self.params.q):
            return False

        e = self._hash_to_int(message)

        # v = e^(-1) mod q
        try:
            v = ModularArithmetic.modinv(e, self.params.q)
        except ValueError:
            return False

        # z1 = s*v mod q, z2 = -r*v mod q
        z1 = (s * v) % self.params.q
        z2 = (-r * v) % self.params.q

        # C = z1*P + z2*Q
        C = (z1 * self._base_point) + (z2 * public_key)

        # R = x_C mod q
        R = C.x % self.params.q

        return R == r
