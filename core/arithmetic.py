"""
Модульная арифметика для криптографических операций
Принципы: DRY, Single Responsibility
"""

from typing import Tuple


class ModularArithmetic:
    """Класс для операций модульной арифметики"""

    @staticmethod
    def egcd(a: int, b: int) -> Tuple[int, int, int]:
        """
        Расширенный алгоритм Евклида
        Возвращает: (gcd, x, y) где a*x + b*y = gcd
        """
        if a == 0:
            return (b, 0, 1)
        gcd, x1, y1 = ModularArithmetic.egcd(b % a, a)
        return (gcd, y1 - (b // a) * x1, x1)

    @staticmethod
    def modinv(a: int, m: int) -> int:
        """
        Обратный элемент по модулю m
        a^(-1) mod m
        """
        gcd, x, _ = ModularArithmetic.egcd(a, m)
        if gcd != 1:
            raise ValueError(f"Число {a} не обратимо по модулю {m}")
        return x % m

    @staticmethod
    def mod_pow(base: int, exponent: int, modulus: int) -> int:
        """
        Быстрое возведение в степень по модулю
        base^exponent mod modulus
        """
        if modulus == 1:
            return 0

        result = 1
        base = base % modulus

        while exponent > 0:
            if exponent & 1:
                result = (result * base) % modulus
            base = (base * base) % modulus
            exponent >>= 1

        return result

    @staticmethod
    def is_prime(n: int, k: int = 10) -> bool:
        """
        Тест простоты Миллера-Рабина
        """
        if n <= 1:
            return False
        if n <= 3:
            return True
        if n % 2 == 0:
            return False

        # Представляем n-1 как d * 2^r
        r = 0
        d = n - 1
        while d % 2 == 0:
            r += 1
            d //= 2

        # Проверяем k раундов
        import random
        for _ in range(k):
            a = random.randint(2, n - 2)
            x = ModularArithmetic.mod_pow(a, d, n)
            if x == 1 or x == n - 1:
                continue
            for _ in range(r - 1):
                x = ModularArithmetic.mod_pow(x, 2, n)
                if x == n - 1:
                    break
            else:
                return False
        return True
