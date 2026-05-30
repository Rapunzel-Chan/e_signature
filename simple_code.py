"""
ГОСТ Р 34.10-2012 - МАТЕМАТИЧЕСКИЕ ОСНОВЫ
Содержит: расширенный алгоритм Евклида, обратный элемент,
          теорему Хассе, проверку простоты
"""

import math
import random
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional, Tuple

# ============================================================================
# МЕТАДАННЫЕ ПОДПИСИ (автор, дата, срок действия)
# ============================================================================


@dataclass
class SignatureMetadata:
    """Метаданные подписи"""

    author: str  # автор подписи
    created_at: str  # дата и время создания
    expires_at: str  # срок действия (опционально)
    purpose: str  # назначение подписи (опционально)

    @classmethod
    def create(cls, author: str, validity_days: int = 365) -> "SignatureMetadata":
        """Создает метаданные с текущей датой и сроком действия"""
        now = datetime.now()
        expires = now + timedelta(days=validity_days)

        return cls(
            author=author,
            created_at=now.strftime("%Y-%m-%d %H:%M:%S"),
            expires_at=expires.strftime("%Y-%m-%d %H:%M:%S"),
            purpose="Электронная цифровая подпись по ГОСТ Р 34.10-2012",
        )

    def to_bytes(self) -> bytes:
        """Преобразует метаданные в байты для подписи"""
        data = f"AUTHOR:{self.author}\n"
        data += f"CREATED:{self.created_at}\n"
        data += f"EXPIRES:{self.expires_at}\n"
        data += f"PURPOSE:{self.purpose}\n"
        data += f"END_METADATA\n"
        return data.encode("utf-8")

    def to_readable(self) -> str:
        """Возвращает читаемый вид метаданных (без псевдографики для совместимости)"""
        return f"""
    {'=' * 60}
    ИНФОРМАЦИЯ О ПОДПИСИ
    {'=' * 60}
      Автор: {self.author}
      Создана: {self.created_at}
      Действительна до: {self.expires_at}
      Назначение: {self.purpose}
    {'=' * 60}
    """

    def is_valid(self) -> bool:
        """Проверяет, не истёк ли срок действия подписи"""
        now = datetime.now()
        try:
            expires = datetime.strptime(self.expires_at, "%Y-%m-%d %H:%M:%S")
            return now <= expires
        except:
            return True


class ModularArithmetic:
    """Модульная арифметика по ГОСТ Р 34.10-2012 (раздел 2.4)"""

    @staticmethod
    def egcd(a: int, b: int) -> tuple:
        """
        Расширенный алгоритм Евклида
        Вход: a, b (a ≥ b > 0)
        Выход: (d, x, y) где d = НОД(a,b), a·x + b·y = d

        - Подаем на вход (n, a) для нахождения a⁻¹ mod n
        - Возвращаем y₂ как обратный элемент
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

        ПО ФОРМУЛЕ ИЗ МЕТОДИЧКИ (стр. 8):
        Чтобы найти a⁻¹ mod n, подаем на вход пару (n, a)
        и возвращаем значение y₂
        """
        # Подаем (m, a) в правильном порядке
        gcd, _, y = ModularArithmetic.egcd(m, a)
        if gcd != 1:
            raise ValueError(f"Нет обратного элемента для {a} mod {m}")
        # Возвращаем y (который соответствует y₂ в алгоритме)
        return y % m

    @staticmethod
    def mod_pow(base: int, exp: int, mod: int) -> int:
        """
        Быстрое возведение в степень по модулю (бинарный метод).

        Вход: a = base, k = exp, n = mod
        Выход: a^k mod n

        Математическая формула:
            a^k = a^{k_0·2^0 + k_1·2^1 + ... + k_t·2^t} = ∏_{i=0}^{t} (a^{2^i})^{k_i}

        Алгоритм (пошагово):
            1. b = 1
            2. A = a mod n
            3. Если младший бит k равен 1, то b = A
            4. Для каждого следующего бита k (i = 1..t):
               4.1. A = A² mod n      # вычисляем a^(2^i) mod n
               4.2. Если i-й бит k равен 1, то b = (b · A) mod n
            5. Возвращаем b
        """
        # Шаг 1: b ← 1
        # b — накопитель результата, изначально равен 1
        result = 1

        # Шаг 2: A ← a
        # Приводим основание к модулю n для уменьшения чисел
        A = base % mod

        # Сохраняем исходную степень для вывода (только для демонстрации)
        k = exp

        print(f"\n  Вычисление: {base}^{exp} mod {mod}")
        print(f"  Двоичное представление exp = {exp} = {bin(exp)[2:]}")
        print(f"  A₀ = {base} mod {mod} = {A}")

        i = 0  # номер текущего бита
        step = 1

        # Шаг 3: Если k₀ = 1, то b ← A
        # Проверяем младший бит (k₀)
        if exp & 1:
            result = A
            print(f"\n  Шаг {step}: бит {i} = 1 → result = {result}")
        else:
            print(f"\n  Шаг {step}: бит {i} = 0 → пропускаем")
        step += 1

        # Сдвигаем exp вправо, чтобы обработать следующий бит
        exp >>= 1
        i += 1

        # Шаг 4: Для i = 1..t
        while exp > 0:
            # Шаг 4.1: A ← A² mod n
            # Формула: a^(2^i) = (a^(2^{i-1}))² mod n
            A = (A * A) % mod
            print(f"\n  Шаг {step}.1: A = A² mod n = {A}")

            # Шаг 4.2: Если kᵢ = 1, то b ← (A · b) mod n
            if exp & 1:
                result = (result * A) % mod
                print(f"  Шаг {step}.2: бит {i} = 1 → result = result × A = {result}")
            else:
                print(f"  Шаг {step}.2: бит {i} = 0 → пропускаем")

            exp >>= 1
            i += 1
            step += 1

        print(f"\n  Результат: {base}^{k} mod {mod} = {result}")
        return result

    @staticmethod
    def is_prime(n: int, k: int = 40) -> bool:
        """
        Тест Миллера-Рабина на простоту.

        Математическая основа (малая теорема Ферма):
        Если n простое, то для любого a: a^(n-1) ≡ 1 (mod n)

        Алгоритм (по ГОСТ Р 34.10-2012, раздел 2.4.3):
        1. Если n < 2 → составное
        2. Если n = 2 или 3 → простое
        3. Если n чётное → составное
        4. Представляем n-1 = 2^s * d, где d нечётное
        5. Для k раундов:
           a = случайное (2 ≤ a ≤ n-2)
           x = a^d mod n
           Если x = 1 или x = n-1 → следующий раунд
           Для j = 1..s-1:
               x = x² mod n
               Если x = n-1 → следующий раунд
           Если ни разу не получили n-1 → n составное
        6. n вероятно простое

        Вероятность ошибки: 2^(-k), для k=40 → 2^(-80) ≈ 0
        """
        if n <= 1:
            return False
        if n <= 3:
            return True
        if n % 2 == 0:
            return False

        # Шаг 4: представляем n-1 = 2^s * d
        s = 0
        d = n - 1
        while d % 2 == 0:
            d //= 2
            s += 1

        # Шаг 5: k раундов
        for _ in range(k):
            # secrets.randbelow безопасен для криптографии
            a = secrets.randbelow(n - 3) + 2
            x = pow(a, d, n)

            if x == 1 or x == n - 1:
                continue

            for _ in range(s - 1):
                x = pow(x, 2, n)
                if x == n - 1:
                    break
            else:
                return False  # n составное

        return True  # n вероятно простое


class HasseTheorem:
    """Теорема Хассе для эллиптических кривых"""

    @staticmethod
    def bounds(p: int) -> tuple:
        """
        Возвращает (min_m, max_m) - границы порядка группы
        По теореме Хассе: |p+1-2√p| ≤ m ≤ p+1+2√p

        ВАЖНО: Используем floor и ceil от вещественного корня
        для точного определения границ
        """
        sqrt_p_float = math.sqrt(p)
        sqrt_p_int = math.floor(sqrt_p_float)  # нижняя граница

        # Для точности используем вещественное значение
        min_m = int(math.floor(p + 1 - 2 * sqrt_p_float))
        max_m = int(math.ceil(p + 1 + 2 * sqrt_p_float))
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
            "p": p,
            "sqrt_p": sqrt_p,
            "2_sqrt_p": 2 * sqrt_p,
            "min_m": min_m,
            "max_m": max_m,
            "actual_m": m,
            "is_valid": min_m <= m <= max_m,
            "formula": f"{p}+1-2√{p} ≤ m ≤ {p}+1+2√{p}",
            "range": f"[{min_m}, {max_m}]",
        }


class BinaryVector:
    """Работа с двоичными векторами (раздел 5.3)"""

    @staticmethod
    def to_int(bits: str) -> int:
        """Преобразует двоичный вектор в целое число"""
        if not bits:
            return 0
        return int(bits, 2)

    @staticmethod
    def to_bits(n: int, length: int) -> str:
        """Преобразует целое число в двоичный вектор фиксированной длины"""
        return bin(n)[2:].zfill(length)

    @staticmethod
    def bytes_to_int(data: bytes) -> int:
        """Преобразует байтовый хэш в целое число"""
        return int.from_bytes(data, "little")

    @staticmethod
    def int_to_bytes(n: int, length: int) -> bytes:
        """Преобразует целое число в байты"""
        return n.to_bytes(length, "little")

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
        right = (self.x**3 + self.a * self.x + self.b) % self.p
        return left == right

    def __add__(self, other):
        """
        Сложение точек по формулам (3) и (4) из ГОСТ Р 34.10-2012

        ЛОГИКА ПО МЕТОДИЧКЕ (стр. 7):
        1. Если x₁ ≠ x₂ → секущая (разные точки)
        2. Если x₁ = x₂ и y₁ = -y₂ → O (противоположные)
        3. Если x₁ = x₂ и y₁ = y₂ → касательная (удвоение)
        """
        # P + O = P
        if self.inf:
            return other
        if other.inf:
            return self

        # Проверка на противоположные точки: P + (-P) = O
        # Это должно быть до проверки на равенство!
        if self.x == other.x and (self.y + other.y) % self.p == 0:
            return Point.infinity(self.a, self.b, self.p)

        # Проверка на удвоение: P = Q
        if self.x == other.x and self.y == other.y:
            # Если y = 0, то точка является обратной самой себе
            # 2P = P + P = O (так как P = -P)
            if self.y == 0:
                return Point.infinity(self.a, self.b, self.p)

            # Формула (4) - удвоение
            lam_num = (3 * self.x * self.x + self.a) % self.p
            lam_den = (2 * self.y) % self.p
            lam = lam_num * ModularArithmetic.modinv(lam_den, self.p) % self.p

            x3 = (lam * lam - 2 * self.x) % self.p
            y3 = (lam * (self.x - x3) - self.y) % self.p
            return Point(x3, y3, self.a, self.b, self.p)

        # Разные точки: x₁ ≠ x₂
        # Формула (3) - секущая
        lam_num = (other.y - self.y) % self.p
        lam_den = (other.x - self.x) % self.p
        lam = lam_num * ModularArithmetic.modinv(lam_den, self.p) % self.p

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
        self.a = a % p
        self.b = b % p

        # Проверка дискриминанта
        discriminant = (4 * a**3 + 27 * b**2) % p
        if discriminant == 0:
            raise ValueError(f"Кривая вырождена: Δ = {discriminant} = 0")

        print(f"\n{'=' * 60}")
        print(f"ЭЛЛИПТИЧЕСКАЯ КРИВАЯ: y² = x³ + {a}x + {b} (mod {p})")
        print(f"Дискриминант: Δ = {discriminant} ≠ 0 ✅")

    def find_all_points(self) -> list:
        """
        Находит все точки на кривой (ТОЛЬКО ДЛЯ МАЛЫХ p)
        Для больших p (реальных ГОСТ) этот метод НЕ вызывается
        """
        points = [Point.infinity(self.a, self.b, self.p)]
        for x in range(self.p):
            right = (x**3 + self.a * x + self.b) % self.p
            for y in range(self.p):
                if (y * y) % self.p == right:
                    points.append(Point(x, y, self.a, self.b, self.p))
        return points

    def get_order(self, verbose=True) -> int:
        """
        Вычисляет порядок группы m = |E(Fp)|

        ВНИМАНИЕ: Для больших p (реальных ГОСТ) этот метод
        использует упрощенную оценку по теореме Хассе.
        В реальных системах параметры берутся из стандарта.
        """
        # Для учебных и небольших p вычисляем точно
        if self.p < 10000:
            points = self.find_all_points()
            m = len(points)
        else:
            # Для больших p используем теорему Хассе
            min_m, max_m = HasseTheorem.bounds(self.p)
            m = (min_m + max_m) // 2  # среднее значение для оценки
            if verbose:
                print(f"\n--- ПОРЯДОК ГРУППЫ m = |E(Fp)| (оценка) ---")
                print(f"p = {self.p} > 10000, используется оценка по Хассе")

        if verbose:
            print(f"\n--- ПОРЯДОК ГРУППЫ m = |E(Fp)| ---")
            print(f"Порядок группы m = {m}")

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
                if 2**254 < q < 2**256:
                    print(f"q = {q} (256-битный диапазон) ✅")
                elif 2**508 < q < 2**512:
                    print(f"q = {q} (512-битный диапазон) ✅")
                else:
                    print(f"q = {q} (вне ГОСТ-диапазона, учебный пример)")
                return q

        # Если не нашли, берем наибольший делитель
        prime_factors = [f for f in factors if ModularArithmetic.is_prime(f)]
        q = max(prime_factors) if prime_factors else m
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
        """
        Находит базовую точку P порядка q (q·P = O)

        ВНИМАНИЕ: Если q простое (а это гарантирует find_subgroup_order),
        то любое q·P = O автоматически означает, что порядок точки = q
        """
        print(f"\n--- ПОИСК БАЗОВОЙ ТОЧКИ ПОРЯДКА q = {q} ---")

        points = self.find_all_points()
        print(f"Всего точек на кривой: {len(points)}")

        for point in points:
            if point.is_infinity():
                continue

            # Проверяем, что q·P = O
            qP = q * point
            if qP.is_infinity():
                # Если q простое, то порядок точки = q
                # Дополнительная проверка не нужна
                print(f"Найдена точка: P = {point}")
                print(f"Проверка: {q}·P = {qP}")
                return point

        raise ValueError(f"Не найдена точка порядка {q}")


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
        # gostcrypto требует имена 'streebog256' или 'streebog512'
        self.algo_name = f"streebog{digest_size}"

    def hash(self, message: bytes) -> bytes:
        """
        Вычисляет хэш-код сообщения
        """
        try:
            hasher = gostcrypto.gosthash.new(self.algo_name, data=message)
            return hasher.digest()
        except Exception as e:
            raise ImportError(
                "Ошибка вызова gostcrypto. Убедитесь, что библиотека установлена корректно.\n"
                f"Детали ошибки: {e}"
            )

    def hash_to_int(self, message: bytes) -> int:
        return int.from_bytes(self.hash(message), "little")

    def hash_to_bits(self, message: bytes) -> str:
        return bin(self.hash_to_int(message))[2:].zfill(self.digest_size)


def get_hasher(digest_size: int = 256) -> Streebog:
    return Streebog(digest_size)


"""
ГОСТ Р 34.10-2012 - ЭЛЕКТРОННАЯ ЦИФРОВАЯ ПОДПИСЬ
Полная реализация алгоритмов I и II
"""

import random
from typing import Tuple


class GOSTSignature:
    """
    Реализация ГОСТ Р 34.10-2012

    Алгоритм I: Формирование подписи (раздел 6.1)
    Алгоритм II: Проверка подписи (раздел 6.2)
    """

    def __init__(
        self,
        p: int,
        a: int,
        b: int,
        hash_len: int = 256,
        auto_params: bool = True,
        q: int = None,
        Px: int = None,
        Py: int = None,
    ):
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
        # Для учебных целей используем q.bit_length()
        # Для реальных ГОСТ компоненты имеют фиксированную длину 256/512 бит
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

    def sign_with_metadata(
        self,
        data: bytes,
        d: int,
        author: str,
        validity_days: int = 365,
        verbose: bool = True,
    ) -> Tuple[int, int, SignatureMetadata]:
        """
        Формирование подписи с метаданными (автор, дата, срок действия)

        Вход:
            data: исходные данные (файл/сообщение)
            d: секретный ключ
            author: имя автора подписи
            validity_days: срок действия в днях (по умолчанию 365)

        Выход:
            (r, s, metadata) - подпись и метаданные
        """
        # Создаём метаданные
        metadata = SignatureMetadata.create(author, validity_days)

        # Формируем сообщение: метаданные + разделитель + данные
        metadata_bytes = metadata.to_bytes()
        separator = b"\n---SIGNED_DATA---\n"

        full_message = metadata_bytes + separator + data

        if verbose:
            print(metadata.to_readable())
            print(f"Подписываем данные: {len(full_message)} байт (включая метаданные)")

        # Подписываем полное сообщение
        r, s, r_bits, s_bits, signature_bits = self.sign(full_message, d, verbose)

        return r, s, metadata

    def verify_with_metadata(
        self, data: bytes, r: int, s: int, Q: Point, verbose: bool = True
    ) -> Tuple[bool, Optional[SignatureMetadata]]:
        """
        Проверка подписи с извлечением метаданных

        Возвращает:
            (is_valid, metadata) - результат проверки и извлечённые метаданные
        """
        if verbose:
            print(f"\n{'=' * 60}")
            print(f"ПРОВЕРКА ПОДПИСИ С МЕТАДАННЫМИ")
            print(f"{'=' * 60}")

        # Пробуем извлечь метаданные из начала данных
        metadata = None
        separator = b"\n---SIGNED_DATA---\n"

        if separator in data:
            metadata_part, actual_data = data.split(separator, 1)

            # Парсим метаданные
            try:
                meta_str = metadata_part.decode("utf-8")
                meta_dict = {}
                for line in meta_str.strip().split("\n"):
                    if ":" in line:
                        key, value = line.split(":", 1)
                        meta_dict[key.strip()] = value.strip()

                if "AUTHOR" in meta_dict:
                    metadata = SignatureMetadata(
                        author=meta_dict.get("AUTHOR", "Unknown"),
                        created_at=meta_dict.get("CREATED", "Unknown"),
                        expires_at=meta_dict.get("EXPIRES", "Unknown"),
                        purpose=meta_dict.get("PURPOSE", "Не указано"),
                    )

                    if verbose:
                        print(metadata.to_readable())

                        # Проверяем срок действия
                        if not metadata.is_valid():
                            print("⚠️  ВНИМАНИЕ: Срок действия подписи ИСТЁК!")
                        else:
                            print("✅ Срок действия подписи актуален")

            except Exception as e:
                if verbose:
                    print(f"⚠️ Не удалось распарсить метаданные: {e}")
        else:
            actual_data = data
            if verbose:
                print("⚠️ Метаданные не найдены, проверяем только подпись")

        # Проверяем подпись
        result = self.verify(actual_data, r, s, Q, verbose)

        return result, metadata

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

    def generate_key_pair(self) -> Tuple[int, Point]:
        """Генерация ключевой пары (d, Q)"""
        d = random.randint(1, self.q - 1)
        Q = d * self.P

        print(f"\n{'=' * 50}")
        print(f"ГЕНЕРАЦИЯ КЛЮЧЕЙ")
        print(f"{'=' * 50}")
        print(f"  Секретный ключ d = {d}")
        print(f"  Открытый ключ Q = d·P = {Q}")

        return d, Q

    def set_lecture_keys(self) -> Tuple[int, Point]:
        """
        УСТАНОВКА КЛЮЧЕЙ ИЗ ЛЕКЦИИ (для проверки примера)

        В лекции: d = 5, Q = 5·P = (50, 56)
        """
        d = 5
        Q = d * self.P

        print(f"\n{'=' * 50}")
        print(f"ЛЕКЦИОННЫЕ КЛЮЧИ")
        print(f"{'=' * 50}")
        print(f"  Секретный ключ d = {d}")
        print(f"  Открытый ключ Q = d·P = {Q}")

        return d, Q

    def sign(
        self, message: bytes, d: int, verbose: bool = True
    ) -> Tuple[int, int, str, str, str]:
        """
        АЛГОРИТМ I: Формирование подписи (раздел 6.1)

        Возвращает: (r, s, r_bits, s_bits, signature_bits)
        """
        if verbose:
            print(f"\n{'=' * 60}")
            print(f"АЛГОРИТМ I: ФОРМИРОВАНИЕ ПОДПИСИ")
            print(f"{'=' * 60}")

        # Шаг 1-2
        e, h_bits, α = self._hash_to_e(message)

        while True:
            # Шаг 3: Случайное k (0 < k < q)
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
                print(
                    f"  s = (r·d + k·e) mod q = ({r}·{d} + {k}·{e}) mod {self.q} = {s}"
                )

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

    def verify(
        self, message: bytes, r: int, s: int, Q: Point, verbose: bool = True
    ) -> bool:
        """
        АЛГОРИТМ II: Проверка подписи (раздел 6.2)

        ПО СТАНДАРТУ: z₂ вычисляется как (q - r) * v mod q
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

        # Шаг 5: z₁ = s·v mod q
        z1 = (s * v) % self.q
        # ПО СТАНДАРТУ: z₂ = (- r) * v mod q
        z2 = (-r * v) % self.q
        if verbose:
            print(f"\n  ШАГ 5: z₁ = s·v mod q = {z1}")
            print(f"         z₂ = (- r)·v mod q = (- {r})·{v} mod {self.q} = {z2}")

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
        result = R == r
        if verbose:
            print(f"\n  ШАГ 7: R == r? {result}")

        return result

    def signature_to_bytes(self, r: int, s: int) -> bytes:
        """Конвертирует подпись в байты"""
        byte_len = (self.component_bits + 7) // 8
        return r.to_bytes(byte_len, "big") + s.to_bytes(byte_len, "big")

    def signature_from_bytes(self, data: bytes) -> Tuple[int, int]:
        """Загружает подпись из байт"""
        byte_len = (self.component_bits + 7) // 8
        r = int.from_bytes(data[:byte_len], "big")
        s = int.from_bytes(data[byte_len:], "big")
        return r, s
