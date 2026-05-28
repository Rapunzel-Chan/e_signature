"""
ГОСТ Р 34.10-2012 - МАТЕМАТИЧЕСКИЕ ОСНОВЫ
Содержит: расширенный алгоритм Евклида, обратный элемент,
          теорему Хассе, проверку простоты
"""

import math
import random


class ModularArithmetic:
    """Модульная арифметика по ГОСТ Р 34.10-2012 (раздел 2.4)"""

    @staticmethod
    def egcd(a: int, b: int) -> tuple:
        """
        Расширенный алгоритм Евклида
        Вход: a, b (a ≥ b > 0)
        Выход: (d, x, y) где d = НОД(a,b), a·x + b·y = d
        """
        x2, x1 = 1, 0
        y2, y1 = 0, 1

        while b > 0:
            q = a // b
            r = a - q * b
            x = x2 - q * x1
            y = y2 - q * y1
            a, b = b, r
            x2, x1 = x1, x
            y2, y1 = y1, y

        return a, x2, y2

    @staticmethod
    def modinv(a: int, m: int) -> int:
        """
        Обратный элемент: a·a⁻¹ ≡ 1 (mod m)
        a⁻¹ mod m = y₂ из расширенного алгоритма Евклида
        """
        gcd, x, _ = ModularArithmetic.egcd(a, m)
        if gcd != 1:
            raise ValueError(f"Нет обратного элемента для {a} mod {m}")
        return x % m

    @staticmethod
    def mod_pow(base: int, exp: int, mod: int) -> int:
        """Быстрое возведение в степень по модулю"""
        result = 1
        base = base % mod
        while exp > 0:
            if exp & 1:
                result = (result * base) % mod
            base = (base * base) % mod
            exp >>= 1
        return result

    @staticmethod
    def is_prime(n: int, k: int = 10) -> bool:
        """Тест Ферма на простоту (раздел 2.4.3)"""
        if n <= 1:
            return False
        if n <= 3:
            return True
        if n % 2 == 0:
            return False

        for _ in range(k):
            a = random.randint(2, n - 2)
            if pow(a, n - 1, n) != 1:
                return False
        return True


class HasseTheorem:
    """Теорема Хассе для эллиптических кривых"""

    @staticmethod
    def bounds(p: int) -> tuple:
        """
        Возвращает (min_m, max_m) - границы порядка группы
        По теореме Хассе: |p+1-2√p| ≤ m ≤ p+1+2√p
        """
        sqrt_p = math.isqrt(p)
        min_m = p + 1 - 2 * sqrt_p
        max_m = p + 1 + 2 * sqrt_p
        return min_m, max_m

    @staticmethod
    def check(m: int, p: int) -> bool:
        """Проверяет, удовлетворяет ли порядок m теореме Хассе"""
        min_m, max_m = HasseTheorem.bounds(p)
        return min_m <= m <= max_m

    @staticmethod
    def verify_curve(p: int, m: int) -> dict:
        """Проверяет кривую и возвращает детали"""
        min_m, max_m = HasseTheorem.bounds(p)
        sqrt_p = math.sqrt(p)

        return {
            'p': p,
            'sqrt_p': sqrt_p,
            '2_sqrt_p': 2 * sqrt_p,
            'min_m': min_m,
            'max_m': max_m,
            'actual_m': m,
            'is_valid': min_m <= m <= max_m,
            'formula': f"{p}+1-2√{p} ≤ m ≤ {p}+1+2√{p}",
            'range': f"[{min_m}, {max_m}]"
        }


class BinaryVector:
    """Работа с двоичными векторами (раздел 5.3)"""

    @staticmethod
    def to_int(bits: str) -> int:
        """
        Преобразует двоичный вектор в целое число
        Пример: "101010" → 42
        """
        return int(bits, 2)

    @staticmethod
    def to_bits(n: int, length: int) -> str:
        """
        Преобразует целое число в двоичный вектор фиксированной длины
        Пример: 42 → "101010" (при length=6)
        """
        return bin(n)[2:].zfill(length)

    @staticmethod
    def bytes_to_int(data: bytes) -> int:
        """Преобразует байтовый хэш в целое число"""
        return int.from_bytes(data, 'big')

    @staticmethod
    def int_to_bytes(n: int, length: int) -> bytes:
        """Преобразует целое число в байты"""
        return n.to_bytes(length, 'big')

    @staticmethod
    def concat(r_bits: str, s_bits: str) -> str:
        """Конкатенация двоичных векторов: ζ = r̄ || s̄"""
        return r_bits + s_bits


"""
ГОСТ Р 34.10-2012 - ЭЛЛИПТИЧЕСКАЯ КРИВАЯ
Содержит: точку на кривой, сложение, удвоение, умножение,
          вычисление порядка группы, поиск базовой точки
"""




class Point:
    """
    Точка на эллиптической кривой E: y² = x³ + a·x + b (mod p)
    Формулы из ГОСТ Р 34.10-2012, раздел 5.1
    """

    def __init__(self, x, y, a, b, p, is_inf=False):
        self.x = x
        self.y = y
        self.a = a
        self.b = b
        self.p = p
        self.inf = is_inf

    def __str__(self):
        if self.inf:
            return "O"
        return f"({self.x}, {self.y})"

    def is_infinity(self):
        return self.inf

    @staticmethod
    def infinity(a, b, p):
        return Point(None, None, a, b, p, is_inf=True)

    def __eq__(self, other):
        if not isinstance(other, Point):
            return False
        if self.inf and other.inf:
            return True
        if self.inf or other.inf:
            return False
        return self.x == other.x and self.y == other.y

    def on_curve(self) -> bool:
        """Проверка: y² ≡ x³ + a·x + b (mod p)"""
        if self.inf:
            return True
        left = (self.y * self.y) % self.p
        right = (self.x ** 3 + self.a * self.x + self.b) % self.p
        return left == right

    def __add__(self, other):
        """
        Сложение точек по формулам (3) и (4)
        Случай 1: P + O = P
        Случай 2: P + (-P) = O
        Случай 3: P ≠ Q, x₁ ≠ x₂ → λ = (y₂ - y₁)/(x₂ - x₁)
        Случай 4: P = Q (удвоение) → λ = (3x₁² + a)/(2y₁)
        """
        if self.inf:
            return other
        if other.inf:
            return self

        # P + (-P) = O
        if self.x == other.x and (self.y + other.y) % self.p == 0:
            return Point.infinity(self.a, self.b, self.p)

        # Вычисление λ
        if self == other:
            # Формула (4) - удвоение
            if self.y == 0:
                raise ValueError("Невозможно удвоить точку с y=0")
            lam_num = (3 * self.x * self.x + self.a) % self.p
            lam_den = (2 * self.y) % self.p
        else:
            # Формула (3) - разные точки
            lam_num = (other.y - self.y) % self.p
            lam_den = (other.x - self.x) % self.p

        lam = lam_num * ModularArithmetic.modinv(lam_den, self.p) % self.p

        # Координаты суммы
        x3 = (lam * lam - self.x - other.x) % self.p
        y3 = (lam * (self.x - x3) - self.y) % self.p

        return Point(x3, y3, self.a, self.b, self.p)

    def __mul__(self, scalar: int):
        """Умножение точки на скаляр (double-and-add)"""
        result = Point.infinity(self.a, self.b, self.p)
        base = self
        k = scalar

        while k > 0:
            if k & 1:
                result = result + base
            base = base + base
            k >>= 1

        return result

    def __rmul__(self, scalar):
        return self.__mul__(scalar)

    def __neg__(self):
        """Отрицание точки: -P = (x, -y mod p)"""
        if self.inf:
            return self
        return Point(self.x, (-self.y) % self.p, self.a, self.b, self.p)

    def order(self, max_iter=10000) -> int:
        """Находит порядок точки (минимальное n: n·P = O)"""
        result = Point.infinity(self.a, self.b, self.p)
        for i in range(1, max_iter):
            result = result + self
            if result.is_infinity():
                return i
        raise ValueError(f"Порядок не найден за {max_iter} итераций")


class EllipticCurve:
    """Эллиптическая кривая с методами для порядка и базовой точки"""

    def __init__(self, p: int, a: int, b: int):
        self.p = p
        self.a = a
        self.b = b

        # Проверка дискриминанта
        discriminant = (4 * a ** 3 + 27 * b ** 2) % p
        if discriminant == 0:
            raise ValueError(f"Кривая вырождена: Δ = {discriminant} = 0")

        print(f"\n{'=' * 60}")
        print(f"ЭЛЛИПТИЧЕСКАЯ КРИВАЯ: y² = x³ + {a}x + {b} (mod {p})")
        print(f"Дискриминант: Δ = {discriminant} ≠ 0 ✅")

    def find_all_points(self) -> list:
        """Находит все точки на кривой (для малых p)"""
        points = [Point.infinity(self.a, self.b, self.p)]
        for x in range(self.p):
            right = (x ** 3 + self.a * x + self.b) % self.p
            for y in range(self.p):
                if (y * y) % self.p == right:
                    points.append(Point(x, y, self.a, self.b, self.p))
        return points

    def get_order(self, verbose=True) -> int:
        """Вычисляет порядок группы m = |E(Fp)|"""
        points = self.find_all_points()
        m = len(points)

        if verbose:
            print(f"\n--- ПОРЯДОК ГРУППЫ m = |E(Fp)| ---")
            print(f"Всего точек на кривой: {m}")

            # Теорема Хассе
            hasse = HasseTheorem.verify_curve(self.p, m)
            print(f"\nТеорема Хассе: {hasse['formula']}")
            print(f"  √{self.p} ≈ {hasse['sqrt_p']:.4f}")
            print(f"  2√p ≈ {hasse['2_sqrt_p']:.4f}")
            print(f"  Диапазон: {hasse['range']}")
            print(f"  m = {m} → {'✅' if hasse['is_valid'] else '❌'}")

        return m

    def find_subgroup_order(self, m: int) -> int:
        """Находит порядок q циклической подгруппы (простой делитель m)"""
        print(f"\n--- ПОИСК ПОРЯДКА ПОДГРУППЫ q ---")

        # Разложение m на множители
        factors = self._factorize(m)
        print(f"Делители m = {m}: {factors}")

        # Ищем простой делитель
        for q in sorted(set(factors), reverse=True):
            if ModularArithmetic.is_prime(q):
                # Проверка по ГОСТ (только для больших чисел)
                if 2 ** 254 < q < 2 ** 256:
                    print(f"q = {q} (256-битный диапазон) ✅")
                elif 2 ** 508 < q < 2 ** 512:
                    print(f"q = {q} (512-битный диапазон) ✅")
                else:
                    print(f"q = {q} (вне ГОСТ-диапазона, учебный пример)")
                return q

        # Если не нашли, берем наибольший делитель
        q = max([f for f in factors if ModularArithmetic.is_prime(f)])
        print(f"Найден q = {q} (учебный пример)")
        return q

    def _factorize(self, n: int) -> list:
        """Разложение на множители"""
        factors = []
        d = 2
        while d * d <= n:
            while n % d == 0:
                factors.append(d)
                n //= d
            d += 1
        if n > 1:
            factors.append(n)
        return factors

    def find_base_point(self, q: int) -> Point:
        """Находит базовую точку P порядка q (q·P = O)"""
        print(f"\n--- ПОИСК БАЗОВОЙ ТОЧКИ ПОРЯДКА q = {q} ---")

        points = self.find_all_points()
        print(f"Всего точек на кривой: {len(points)}")

        for point in points:
            if point.is_infinity():
                continue

            # Проверяем, что q·P = O
            qP = q * point
            if qP.is_infinity():
                # Проверяем, что порядок точно q
                point_order = point.order()
                if point_order == q:
                    print(f"Найдена точка: P = {point}")
                    print(f"Проверка: {q}·P = {qP}")
                    return point

        raise ValueError(f"Не найдена точка порядка {q}")


"""
ГОСТ Р 34.11-2012 - ФУНКЦИЯ ХЭШИРОВАНИЯ STREEBOG
Полная реализация с поддержкой 256 и 512 бит
"""
"""
ГОСТ Р 34.11-2012 - ФУНКЦИЯ ХЭШИРОВАНИЯ STREEBOG
Использует официальную реализацию из библиотеки 
"""

import gostcrypto

"""
ГОСТ Р 34.11-2012 - ФУНКЦИЯ ХЭШИРОВАНИЯ STREEBOG
Использует библиотеку gostcrypto
"""

import gostcrypto


"""
ГОСТ Р 34.11-2012 - ФУНКЦИЯ ХЭШИРОВАНИЯ STREEBOG
Использует библиотеку gostcrypto
"""

import gostcrypto


class Streebog:
    """
    Функция хэширования Streebog (ГОСТ Р 34.11-2012)
    """

    def __init__(self, digest_size: int = 256):
        if digest_size not in (256, 512):
            raise ValueError("digest_size должен быть 256 или 512")
        self.digest_size = digest_size
        # gostcrypto требует строго имена 'streebog256' или 'streebog512'
        self.algo_name = f"streebog{digest_size}"

    def hash(self, message: bytes) -> bytes:
        """
        Вычисляет хэш-код сообщения
        """
        try:
            # Теперь self.algo_name передает корректную строку 'streebog256'
            hasher = gostcrypto.gosthash.new(self.algo_name, data=message)
            return hasher.digest()
        except Exception as e:
            raise ImportError(
                "Ошибка вызова gostcrypto. Убедитесь, что библиотека установлена корректно.\n"
                f"Детали ошибки: {e}"
            )

    def hash_to_int(self, message: bytes) -> int:
        return int.from_bytes(self.hash(message), 'big')

    def hash_to_bits(self, message: bytes) -> str:
        return bin(self.hash_to_int(message))[2:].zfill(self.digest_size)


def get_hasher(digest_size: int = 256) -> Streebog:
    return Streebog(digest_size)



# import hashlib
# import struct
#
#
# class Streebog:
#     """
#     Функция хэширования Streebog (ГОСТ Р 34.11-2012)
#     Поддерживает длину хэша 256 и 512 бит
#     """
#
#     # Инициализационные векторы
#     IV256 = bytes(32)  # 000...0 для 256 бит
#     IV512 = bytes(64)  # 000...0 для 512 бит
#
#     # S-блок (нелинейное преобразование)
#     SBOX = bytes([
#         0xFC, 0xEE, 0xDB, 0x04, 0x09, 0x07, 0x03, 0x0C, 0x06, 0xC6, 0x24, 0x95, 0xB9, 0x9B, 0x02, 0x3F,
#         0x14, 0xD8, 0x0D, 0x00, 0x01, 0xFA, 0x7C, 0x8E, 0xE2, 0xC9, 0x5C, 0x75, 0x8F, 0xE5, 0x73, 0xE7,
#         0x5E, 0x5D, 0x8D, 0x45, 0x44, 0x63, 0x30, 0x19, 0x85, 0xFE, 0x52, 0xBA, 0x83, 0xE6, 0x2C, 0x80,
#         0x81, 0x0E, 0x3D, 0x93, 0x3E, 0x47, 0x4F, 0xB7, 0x8A, 0x26, 0x2B, 0xA6, 0xB0, 0xD1, 0x87, 0xF1
#     ])
#
#     def __init__(self, digest_size: int = 256):
#         """
#         digest_size: 256 или 512 бит
#         """
#         if digest_size not in (256, 512):
#             raise ValueError("digest_size должен быть 256 или 512")
#         self.digest_size = digest_size
#         self.block_size = 64  # 512 бит
#
#     def _add_mod_512(self, a: bytes, b: bytes) -> bytes:
#         """Сложение двух 512-битных чисел по модулю 2^512"""
#         a_int = int.from_bytes(a, 'little')
#         b_int = int.from_bytes(b, 'little')
#         result = (a_int + b_int) & ((1 << 512) - 1)
#         return result.to_bytes(64, 'little')
#
#     def _xor(self, a: bytes, b: bytes) -> bytes:
#         """Побитовое XOR"""
#         return bytes(x ^ y for x, y in zip(a, b))
#
#     def _s(self, data: bytes) -> bytes:
#         """Нелинейное преобразование S (подстановка)"""
#         return bytes(self.SBOX[b] for b in data)
#
#     def _p(self, data: bytes) -> bytes:
#         """Перестановка байт τ"""
#         result = bytearray(64)
#         for i in range(64):
#             # τ(i) = (i * 8) mod 63, с особым случаем
#             new_idx = (i * 8) % 63 if (i * 8) % 63 != 0 or i == 0 else 63
#             result[new_idx] = data[i]
#         return bytes(result)
#
#     def _l(self, data: bytes) -> bytes:
#         """Линейное преобразование L (упрощенное)"""
#         # В реальной реализации - умножение на матрицу 64x64
#         result = bytearray(64)
#         for i in range(64):
#             val = 0
#             for j in range(8):
#                 if (data[j] >> (7 - i)) & 1:
#                     val ^= 0xC1
#             result[i] = val
#         return bytes(result)
#
#     def _lps(self, data: bytes) -> bytes:
#         """Преобразование LPS: L∘P∘S"""
#         return self._l(self._p(self._s(data)))
#
#     def _g(self, h: bytes, m: bytes, n: bytes, sigma: bytes) -> bytes:
#         """Функция сжатия"""
#         # K = LPS(h ⊕ N)
#         k = self._lps(self._xor(h, n))
#         # Результат (упрощенно)
#         return self._xor(self._xor(self._xor(m, k), h), sigma)
#
#     def hash(self, message: bytes) -> bytes:
#         """
#         Вычисление хэш-кода по алгоритму из раздела 8
#         """
#         # Этап 1: Инициализация
#         h = self.IV512 if self.digest_size == 512 else self.IV256
#         n = bytes(64)
#         sigma = bytes(64)
#         data = message
#
#         # Этап 2: Обработка полных блоков
#         while len(data) >= 64:
#             m = data[:64]
#             h = self._g(h, m, n, sigma)
#             n = self._add_mod_512(n, bytes(64))
#             sigma = self._add_mod_512(sigma, m)
#             data = data[64:]
#
#         # Этап 3: Обработка последнего блока
#         m = data + b'\x01' + b'\x00' * (63 - len(data))
#         h = self._g(h, m, n, sigma)
#
#         n = self._add_mod_512(n, bytes([len(message) % 512]))
#         sigma = self._add_mod_512(sigma, m)
#
#         h = self._g(h, n, sigma)
#
#         if self.digest_size == 256:
#             return h[:32]
#         return h
#
#     def hash_to_int(self, message: bytes) -> int:
#         """Возвращает хэш как целое число α"""
#         hash_bytes = self.hash(message)
#         return int.from_bytes(hash_bytes, 'big')
#
#     def hash_to_bits(self, message: bytes) -> str:
#         """Возвращает хэш как двоичную строку"""
#         hash_int = self.hash_to_int(message)
#         return bin(hash_int)[2:].zfill(self.digest_size)
#
#
# def get_hasher(digest_size: int = 256) -> Streebog:
#     """Возвращает экземпляр хэш-функции"""
#     return Streebog(digest_size)


"""
ГОСТ Р 34.10-2012 - ЭЛЕКТРОННАЯ ЦИФРОВАЯ ПОДПИСЬ
Полная реализация алгоритмов I и II
"""

import random
from typing import Tuple, Optional



class GOSTSignature:
    """
    Реализация ГОСТ Р 34.10-2012

    Алгоритм I: Формирование подписи (раздел 6.1)
    Алгоритм II: Проверка подписи (раздел 6.2)
    """

    def __init__(self, p: int, a: int, b: int, hash_len: int = 256,
                 auto_params: bool = True, q: int = None, Px: int = None, Py: int = None):
        """
        Инициализация схемы подписи

        Параметры:
            p: модуль кривой (простое число)
            a, b: коэффициенты кривой
            hash_len: длина хэша (256 или 512)
            auto_params: вычислять ли m, q, P автоматически
            q, Px, Py: ручные параметры (для тестов)
        """
        self.p = p
        self.a = a
        self.b = b
        self.hash_len = hash_len
        self.hasher = get_hasher(hash_len)

        # Создаем кривую
        self.curve = EllipticCurve(p, a, b)

        if auto_params:
            # Вычисляем параметры автоматически
            self.m = self.curve.get_order()
            self.q = self.curve.find_subgroup_order(self.m)
            self.P = self.curve.find_base_point(self.q)
        else:
            # Используем ручные параметры (для тестов)
            self.m = None
            self.q = q
            self.P = Point(Px, Py, a, b, p)

        # Длина компонент подписи в битах
        self.component_bits = self.q.bit_length()

        print(f"\n{'=' * 60}")
        print(f"ПАРАМЕТРЫ СХЕМЫ ПОДПИСИ")
        print(f"{'=' * 60}")
        print(f"  p = {p}")
        print(f"  a = {a}, b = {b}")
        print(f"  q = {self.q}")
        print(f"  P = {self.P}")
        print(f"  Длина хэша: {hash_len} бит")
        print(f"  Длина подписи: {self.component_bits * 2} бит")

    def _hash_to_e(self, message: bytes) -> Tuple[int, str, int]:
        """
        Шаги 1-2 по ГОСТ:
        Шаг 1: h = H(M) - двоичный вектор
        Шаг 2: α - десятичное представление h, e = α mod q (если 0, то 1)
        """
        # Шаг 1: Хэш-код как двоичный вектор и целое число
        h_bits = self.hasher.hash_to_bits(message)
        α = self.hasher.hash_to_int(message)

        print(f"\n  Хэш-код h(M) (двоичный): {h_bits[:32]}...")
        print(f"  α (десятичное представление) = {α}")

        # Шаг 2: e = α mod q
        e = α % self.q
        if e == 0:
            e = 1
            print(f"  e = α mod q = 0 → устанавливаем e = 1")
        else:
            print(f"  e = α mod q = {e}")

        return e, h_bits, α

    def generate_key_pair(self, seed: int = None) -> Tuple[int, Point]:
        """Генерация ключевой пары (d, Q)"""
        if seed is not None:
            random.seed(seed)

        d = random.randint(1, self.q - 1)
        Q = d * self.P

        print(f"\n{'=' * 50}")
        print(f"ГЕНЕРАЦИЯ КЛЮЧЕЙ")
        print(f"{'=' * 50}")
        print(f"  Секретный ключ d = {d}")
        print(f"  Открытый ключ Q = d·P = {Q}")

        return d, Q

    def sign(self, message: bytes, d: int, verbose: bool = True) -> Tuple[int, int, str, str, str]:
        """
        АЛГОРИТМ I: Формирование подписи

        Возвращает: (r, s, r_bits, s_bits, signature_bits)
        """
        if verbose:
            print(f"\n{'=' * 60}")
            print(f"АЛГОРИТМ I: ФОРМИРОВАНИЕ ПОДПИСИ")
            print(f"{'=' * 60}")

        # Шаг 1-2
        e, h_bits, α = self._hash_to_e(message)

        while True:
            # Шаг 3: Случайное k
            k = random.randint(1, self.q - 1)

            # Шаг 4: C = k·P, r = x_C mod q
            C = k * self.P
            r = C.x % self.q

            if r == 0:
                continue

            # Шаг 5: s = (r·d + k·e) mod q
            s = (r * d + k * e) % self.q

            if s == 0:
                continue

            if verbose:
                print(f"\n  k = {k}")
                print(f"  C = k·P = {C}")
                print(f"  r = {r}")
                print(f"  s = (r·d + k·e) mod q = ({r}·{d} + {k}·{e}) mod {self.q} = {s}")

            break

        # Шаг 6: Двоичные векторы
        r_bits = BinaryVector.to_bits(r, self.component_bits)
        s_bits = BinaryVector.to_bits(s, self.component_bits)
        signature_bits = BinaryVector.concat(r_bits, s_bits)

        if verbose:
            print(f"\n  r̄ (двоичный) = {r_bits}")
            print(f"  s̄ (двоичный) = {s_bits}")
            print(f"  ζ = r̄ || s̄ = {signature_bits}")

        return r, s, r_bits, s_bits, signature_bits

    def verify(self, message: bytes, r: int, s: int, Q: Point, verbose: bool = True) -> bool:
        """
        АЛГОРИТМ II: Проверка подписи
        """
        if verbose:
            print(f"\n{'=' * 60}")
            print(f"АЛГОРИТМ II: ПРОВЕРКА ПОДПИСИ")
            print(f"{'=' * 60}")
            print(f"  r = {r}, s = {s}")
            print(f"  Q = {Q}")

        # Шаг 1: Проверка диапазона
        if not (0 < r < self.q and 0 < s < self.q):
            if verbose:
                print(f"\n  ШАГ 1: ❌ r или s вне диапазона (0, {self.q})")
            return False

        if verbose:
            print(f"\n  ШАГ 1: ✅ 0 < r < {self.q} и 0 < s < {self.q}")

        # Шаг 2-3: e
        e, h_bits, α = self._hash_to_e(message)

        # Шаг 4: v = e⁻¹ mod q
        v = ModularArithmetic.modinv(e, self.q)
        if verbose:
            print(f"\n  ШАГ 4: v = e⁻¹ mod q = {v}")

        # Шаг 5: z₁ = s·v mod q, z₂ = -r·v mod q
        z1 = (s * v) % self.q
        z2 = (-r * v) % self.q
        if verbose:
            print(f"\n  ШАГ 5: z₁ = s·v mod q = {z1}")
            print(f"         z₂ = -r·v mod q = {z2}")

        # Шаг 6: C = z₁·P + z₂·Q, R = x_C mod q
        C = (z1 * self.P) + (z2 * Q)
        if verbose:
            print(f"\n  ШАГ 6: C = {C}")

        if C.is_infinity():
            if verbose:
                print(f"         C - нулевая точка → подпись неверна")
            return False

        R = C.x % self.q
        if verbose:
            print(f"         R = x_C mod q = {R}")

        # Шаг 7: Сравнение
        result = (R == r)
        if verbose:
            print(f"\n  ШАГ 7: R == r? {result}")

        return result

    def signature_to_bytes(self, r: int, s: int) -> bytes:
        """Конвертирует подпись в байты"""
        byte_len = (self.component_bits + 7) // 8
        return r.to_bytes(byte_len, 'big') + s.to_bytes(byte_len, 'big')

    def signature_from_bytes(self, data: bytes) -> Tuple[int, int]:
        """Загружает подпись из байт"""
        byte_len = (self.component_bits + 7) // 8
        r = int.from_bytes(data[:byte_len], 'big')
        s = int.from_bytes(data[byte_len:], 'big')
        return r, s

