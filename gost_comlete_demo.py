"""
ГОСТ Р 34.10-2012 - ПОЛНАЯ ДЕМОНСТРАЦИЯ С ПОШАГОВЫМ ВЫВОДОМ
Можно запустить и проверить каждый шаг вычислений вручную
"""

import random
import hashlib
from typing import Tuple, Optional


# ==================== МОДУЛЬНАЯ АРИФМЕТИКА ====================

def egcd(a: int, b: int) -> Tuple[int, int, int]:
    """Расширенный алгоритм Евклида"""
    if a == 0:
        return (b, 0, 1)
    gcd, x1, y1 = egcd(b % a, a)
    return (gcd, y1 - (b // a) * x1, x1)


def modinv(a: int, m: int) -> int:
    """Обратный элемент по модулю m"""
    gcd, x, _ = egcd(a, m)
    if gcd != 1:
        raise ValueError(f"Число {a} не обратимо по модулю {m}")
    return x % m


# ==================== ТОЧКА НА ЭЛЛИПТИЧЕСКОЙ КРИВОЙ ====================

class Point:
    """Точка на эллиптической кривой с выводом шагов"""

    def __init__(self, x, y, a, b, p, is_inf=False):
        self.x = x
        self.y = y
        self.a = a
        self.b = b
        self.p = p
        self.is_inf = is_inf
        self.debug = True  # Включаем вывод шагов

    def __str__(self):
        if self.is_inf:
            return "∞ (бесконечно удаленная точка)"
        return f"({self.x}, {self.y})"

    def __eq__(self, other):
        if self.is_inf and other.is_inf:
            return True
        if self.is_inf or other.is_inf:
            return False
        return self.x == other.x and self.y == other.y

    def __add__(self, other):
        """Сложение точек с пошаговым выводом"""
        print(f"\n  --- Сложение точек: {self} + {other} ---")

        # P + O = P
        if self.is_inf:
            print(f"  Результат: {other}")
            return other
        if other.is_inf:
            print(f"  Результат: {self}")
            return self

        # P + (-P) = O
        if self.x == other.x and (self.y + other.y) % self.p == 0:
            print(f"  Точки противоположны -> результат: ∞")
            return Point(None, None, self.a, self.b, self.p, is_inf=True)

        # Вычисление лямбды
        if self == other:
            print(f"  Удвоение точки (P = Q)")
            if self.y == 0:
                raise ValueError("Невозможно удвоить точку с y=0")
            numerator = (3 * self.x * self.x + self.a) % self.p
            denominator = (2 * self.y) % self.p
            print(f"  λ = (3*x² + a) / (2*y) = ({3 * self.x * self.x}+{self.a}) / ({2 * self.y})")
        else:
            print(f"  Сложение разных точек (P ≠ Q)")
            numerator = (other.y - self.y) % self.p
            denominator = (other.x - self.x) % self.p
            print(f"  λ = (y₂ - y₁) / (x₂ - x₁) = ({other.y} - {self.y}) / ({other.x} - {self.x})")

        print(f"  numerator = {numerator}")
        print(f"  denominator = {denominator}")

        lam = numerator * modinv(denominator, self.p) % self.p
        print(f"  λ = {lam}")

        # Вычисление координат
        x3 = (lam * lam - self.x - other.x) % self.p
        y3 = (lam * (self.x - x3) - self.y) % self.p
        print(f"  x₃ = λ² - x₁ - x₂ = {lam}² - {self.x} - {other.x} = {x3}")
        print(f"  y₃ = λ*(x₁ - x₃) - y₁ = {lam}*({self.x} - {x3}) - {self.y} = {y3}")

        result = Point(x3, y3, self.a, self.b, self.p)
        print(f"  Результат: {result}")
        return result

    def __mul__(self, scalar: int):
        """Умножение точки на скаляр (double-and-add)"""
        print(f"\n{'=' * 50}")
        print(f"УМНОЖЕНИЕ ТОЧКИ НА СКАЛЯР: {scalar} * {self}")
        print(f"{'=' * 50}")

        result = Point(None, None, self.a, self.b, self.p, is_inf=True)
        base = self
        k = scalar

        step = 1
        while k > 0:
            if k & 1:
                print(f"\nШаг {step}: бит = 1 -> result = result + base")
                result = result + base
            else:
                print(f"\nШаг {step}: бит = 0 -> пропускаем сложение")
            print(f"  base = base + base")
            base = base + base
            k >>= 1
            step += 1

        print(f"\nРезультат умножения: {result}")
        return result

    def __rmul__(self, scalar):
        return self.__mul__(scalar)


# ==================== ХЭШ-ФУНКЦИЯ ====================

def hash_to_int(message: bytes, q: int) -> int:
    """Хэширует сообщение и приводит к модулю q"""
    h = int.from_bytes(hashlib.sha256(message).digest(), 'big')
    e = h % q
    if e == 0:
        e = 1
    return e


# ==================== ПАРАМЕТРЫ КРИВЫХ ====================

class CurveParams:
    """Параметры эллиптической кривой"""

    # РЕКОМЕНДУЕМЫЕ ПАРАМЕТРЫ ИЗ ЗАДАНИЯ
    VARIANT_1 = {
        'name': 'Вариант 1 (рекомендуемый)',
        'p': 10711,
        'a': 236,
        'b': 757,
        'q': 5441,
        'm': 10882,
        'Px': None,  # Найдем позже
        'Py': None,
    }

    VARIANT_2 = {
        'name': 'Вариант 2 (рекомендуемый)',
        'p': 10711,
        'a': 138,
        'b': 757,
        'q': 10837,
        'm': 10837,
        'Px': None,
        'Py': None,
    }

    VARIANT_3 = {
        'name': 'Вариант 3 (рекомендуемый)',
        'p': 11117,
        'a': 338,
        'b': 157,
        'q': 5479,
        'm': 10958,
        'Px': None,
        'Py': None,
    }

    # ТЕСТОВЫЕ ПАРАМЕТРЫ (из лекции)
    TEST_PARAMS = {
        'name': 'Тестовые параметры (из лекции)',
        'p': 97,
        'a': 9,
        'b': 3,
        'q': 47,
        'm': 94,
        'Px': -8 % 97,
        'Py': 1,
    }

    @staticmethod
    def find_base_point(p: int, a: int, b: int, q: int) -> Tuple[int, int]:
        """Находит базовую точку порядка q"""
        print(f"\n  Поиск базовой точки порядка {q} на кривой...")

        for x in range(p):
            right = (x ** 3 + a * x + b) % p
            # Проверяем, является ли right квадратичным вычетом
            legendre = pow(right, (p - 1) // 2, p)
            if legendre == 1:  # есть квадратный корень
                for y in range(p):
                    if (y * y) % p == right:
                        # Проверяем порядок
                        test_point = Point(x, y, a, b, p)
                        if (q * test_point).is_infinity:
                            print(f"  Найдена точка: ({x}, {y})")
                            return (x, y)

        raise ValueError("Базовая точка не найдена")


# ==================== ОСНОВНОЙ КЛАСС ПОДПИСИ ====================

class GOSTSignature:
    """ГОСТ Р 34.10-2012 с пошаговым выводом"""

    def __init__(self, params: dict):
        self.params = params
        # Проверяем или находим базовую точку
        if params['Px'] is None:
            Px, Py = CurveParams.find_base_point(
                params['p'], params['a'], params['b'], params['q']
            )
            params['Px'] = Px
            params['Py'] = Py

        self.P = Point(params['Px'], params['Py'], params['a'], params['b'], params['p'])

        print(f"\n{'=' * 60}")
        print(f"ИНИЦИАЛИЗАЦИЯ: {params['name']}")
        print(f"{'=' * 60}")
        print(f"  p (модуль) = {params['p']}")
        print(f"  a = {params['a']}")
        print(f"  b = {params['b']}")
        print(f"  q (порядок подгруппы) = {params['q']}")
        print(f"  m (порядок группы) = {params['m']}")
        print(f"  P (базовая точка) = ({params['Px']}, {params['Py']})")
        print(f"  Проверка: q * P = {params['q'] * self.P}")

        # Проверка соотношения m = n * q
        n = params['m'] // params['q']
        print(f"  m / q = {params['m']} / {params['q']} = {n} (целое)")

    def generate_key_pair(self, seed: int = None) -> Tuple[int, Point]:
        """Генерирует ключевую пару"""
        if seed:
            random.seed(seed)

        d = random.randint(1, self.params['q'] - 1)
        Q = d * self.P

        print(f"\n{'=' * 50}")
        print(f"ГЕНЕРАЦИЯ КЛЮЧЕВ")
        print(f"{'=' * 50}")
        print(f"  Секретный ключ d = {d}")
        print(f"  Открытый ключ Q = d * P = {Q}")

        return d, Q

    def sign(self, message: bytes, d: int, verbose: bool = True) -> Tuple[int, int]:
        """Формирует подпись с пошаговым выводом"""

        if verbose:
            print(f"\n{'=' * 60}")
            print(f"ФОРМИРОВАНИЕ ПОДПИСИ")
            print(f"{'=' * 60}")
            print(f"  Сообщение: {message}")

        # Шаг 1: Вычисляем хэш
        e = hash_to_int(message, self.params['q'])
        if verbose:
            print(f"\nШАГ 1: Вычисление хэша")
            print(f"  h = hash(message) = {hashlib.sha256(message).hexdigest()}")
            print(f"  e = h mod q = {e}")

        while True:
            # Шаг 2: Генерируем случайное k
            k = random.randint(1, self.params['q'] - 1)
            if verbose:
                print(f"\nШАГ 2: Генерация случайного числа")
                print(f"  k = {k}")

            # Шаг 3: Вычисляем C = k * P
            C = k * self.P
            r = C.x % self.params['q']
            if verbose:
                print(f"\nШАГ 3: Вычисление r = x_C mod q")
                print(f"  C = k * P = {C}")
                print(f"  r = {C.x} mod {self.params['q']} = {r}")

            if r == 0:
                if verbose:
                    print(f"  r = 0, повторяем с новым k")
                continue

            # Шаг 4: Вычисляем s = (r*d + k*e) mod q
            s = (r * d + k * e) % self.params['q']
            if verbose:
                print(f"\nШАГ 4: Вычисление s = (r*d + k*e) mod q")
                print(f"  r*d = {r} * {d} = {r * d}")
                print(f"  k*e = {k} * {e} = {k * e}")
                print(f"  r*d + k*e = {r * d + k * e}")
                print(f"  s = {s}")

            if s == 0:
                if verbose:
                    print(f"  s = 0, повторяем с новым k")
                continue

            break

        if verbose:
            print(f"\n{'=' * 50}")
            print(f"РЕЗУЛЬТАТ ПОДПИСИ:")
            print(f"  r = {r}")
            print(f"  s = {s}")
            print(f"{'=' * 50}")

        return r, s

    def verify(self, message: bytes, r: int, s: int, Q: Point, verbose: bool = True) -> bool:
        """Проверяет подпись с пошаговым выводом"""

        if verbose:
            print(f"\n{'=' * 60}")
            print(f"ПРОВЕРКА ПОДПИСИ")
            print(f"{'=' * 60}")
            print(f"  Сообщение: {message}")
            print(f"  r = {r}, s = {s}")
            print(f"  Q = {Q}")

        # Шаг 1: Проверяем 0 < r < q и 0 < s < q
        if verbose:
            print(f"\nШАГ 1: Проверка диапазона")
            print(f"  0 < r < q? {0 < r < self.params['q']}")
            print(f"  0 < s < q? {0 < s < self.params['q']}")

        if not (0 < r < self.params['q'] and 0 < s < self.params['q']):
            if verbose:
                print(f"  ❌ Неверный диапазон")
            return False

        # Шаг 2: Вычисляем хэш
        e = hash_to_int(message, self.params['q'])
        if verbose:
            print(f"\nШАГ 2: Вычисление хэша")
            print(f"  e = {e}")

        # Шаг 3: v = e^(-1) mod q
        v = modinv(e, self.params['q'])
        if verbose:
            print(f"\nШАГ 3: v = e⁻¹ mod q")
            print(f"  v = {v}")
            print(f"  Проверка: e * v mod q = {(e * v) % self.params['q']}")

        # Шаг 4: z1 = s*v mod q, z2 = -r*v mod q
        z1 = (s * v) % self.params['q']
        z2 = (-r * v) % self.params['q']
        if verbose:
            print(f"\nШАГ 4: Вычисление z1 и z2")
            print(f"  z1 = s*v mod q = {s} * {v} mod {self.params['q']} = {z1}")
            print(f"  z2 = -r*v mod q = -{r} * {v} mod {self.params['q']} = {z2}")

        # Шаг 5: C = z1*P + z2*Q
        C = (z1 * self.P) + (z2 * Q)
        if verbose:
            print(f"\nШАГ 5: Вычисление C = z1*P + z2*Q")
            print(f"  z1*P = {z1} * {self.P} = {z1 * self.P}")
            print(f"  z2*Q = {z2} * {Q} = {z2 * Q}")
            print(f"  C = {C}")

        # Шаг 6: R = x_C mod q
        R = C.x % self.params['q']
        if verbose:
            print(f"\nШАГ 6: R = x_C mod q")
            print(f"  x_C = {C.x}")
            print(f"  R = {C.x} mod {self.params['q']} = {R}")

        # Шаг 7: Сравнение
        result = (R == r)
        if verbose:
            print(f"\nШАГ 7: Сравнение R и r")
            print(f"  R = {R}, r = {r}")
            print(f"  {'✅ ПОДПИСЬ ВЕРНА' if result else '❌ ПОДПИСЬ НЕВЕРНА'}")

        return result


# ==================== ДЕМОНСТРАЦИОННЫЕ ТЕСТЫ ====================

def test_variant_with_numbers(variant_num: int, params: dict, message: bytes, fixed_seed: int = 42):
    """Тестирует конкретный вариант с фиксированными числами"""

    print(f"\n{'#' * 70}")
    print(f"# ТЕСТИРОВАНИЕ {params['name']}")
    print(f"#{'#' * 70}")

    # Инициализация
    gost = GOSTSignature(params)

    # Генерация ключей с фиксированным seed
    random.seed(fixed_seed)
    d = random.randint(1, params['q'] - 1)
    Q = d * gost.P

    print(f"\n{'=' * 50}")
    print(f"КЛЮЧЕВАЯ ПАРА (seed={fixed_seed})")
    print(f"{'=' * 50}")
    print(f"  d = {d}")
    print(f"  Q = {Q}")

    # Формирование подписи
    r, s = gost.sign(message, d, verbose=True)

    # Проверка подписи
    result = gost.verify(message, r, s, Q, verbose=True)

    print(f"\n{'=' * 70}")
    print(f"ИТОГ ДЛЯ {params['name']}: {'✅ ПРОЙДЕН' if result else '❌ НЕ ПРОЙДЕН'}")
    print(f"{'=' * 70}")

    return result, (r, s, d, Q)


def test_all_variants():
    """Тестирует все варианты параметров"""

    print("\n" + "=" * 70)
    print("ПОЛНОЕ ТЕСТИРОВАНИЕ ВСЕХ ВАРИАНТОВ ПАРАМЕТРОВ")
    print("=" * 70)

    # Тестовое сообщение
    message = b"Hello, GOST! This is a test message for digital signature."

    results = {}

    # Тест варианта 1
    print("\n" + "🔵" * 35)
    results['variant1'] = test_variant_with_numbers(1, CurveParams.VARIANT_1, message, fixed_seed=42)

    # Тест варианта 2
    print("\n" + "🟢" * 35)
    results['variant2'] = test_variant_with_numbers(2, CurveParams.VARIANT_2, message, fixed_seed=42)

    # Тест варианта 3
    print("\n" + "🟡" * 35)
    results['variant3'] = test_variant_with_numbers(3, CurveParams.VARIANT_3, message, fixed_seed=42)

    # Тест с параметрами из лекции
    print("\n" + "⚪" * 35)
    results['test'] = test_variant_with_numbers(0, CurveParams.TEST_PARAMS, b"Test", fixed_seed=42)

    # Итоговый вывод
    print("\n" + "=" * 70)
    print("ИНТЕРЕСНЫЕ МАТЕМАТИЧЕСКИЕ ФАКТЫ:")
    print("=" * 70)

    for var_name, (result, data) in results.items():
        if var_name == 'variant1':
            print(f"\n📌 Вариант 1 (p=10711, q=5441):")
            print(f"   • Простота p: {pow(2, 10710, 10711) == 2}")
            print(f"   • Простота q: {pow(2, 5440, 5441) == 2}")
            print(f"   • d = {data[2]}")
            print(f"   • r = {data[0]}, s = {data[1]}")
            print(f"   • Подпись: {result}")

        elif var_name == 'variant2':
            print(f"\n📌 Вариант 2 (p=10711, q=10837):")
            print(f"   • Обратите внимание: q > p! Это особый случай")
            print(f"   • d = {data[2]}")
            print(f"   • r = {data[0]}, s = {data[1]}")
            print(f"   • Подпись: {result}")

        elif var_name == 'variant3':
            print(f"\n📌 Вариант 3 (p=11117, q=5479):")
            print(f"   • p = 11117 (простое: {pow(2, 11116, 11117) == 2})")
            print(f"   • d = {data[2]}")
            print(f"   • r = {data[0]}, s = {data[1]}")
            print(f"   • Подпись: {result}")

        elif var_name == 'test':
            print(f"\n📌 Тестовые параметры (p=97, q=47):")
            print(f"   • r = {data[0]}, s = {data[1]}")
            print(f"   • Подпись: {result}")


# ==================== ИНТЕРАКТИВНЫЙ РЕЖИМ ====================

def interactive_mode():
    """Интерактивный режим для ручной проверки"""

    print("\n" + "=" * 70)
    print("ИНТЕРАКТИВНЫЙ РЕЖИМ - ВЫ МОЖЕТЕ ВВЕСТИ СВОИ ЧИСЛА")
    print("=" * 70)

    while True:
        print("\nВыберите действие:")
        print("  1. Использовать вариант 1 (p=10711, a=236, b=757, q=5441)")
        print("  2. Использовать вариант 2 (p=10711, a=138, b=757, q=10837)")
        print("  3. Использовать вариант 3 (p=11117, a=338, b=157, q=5479)")
        print("  4. Использовать тестовые параметры (p=97, q=47)")
        print("  5. Ввести свои параметры вручную")
        print("  0. Выход")

        choice = input("\nВаш выбор: ")

        if choice == '1':
            params = CurveParams.VARIANT_1.copy()
        elif choice == '2':
            params = CurveParams.VARIANT_2.copy()
        elif choice == '3':
            params = CurveParams.VARIANT_3.copy()
        elif choice == '4':
            params = CurveParams.TEST_PARAMS.copy()
        elif choice == '5':
            print("\nВведите параметры кривой:")
            params = {
                'name': 'Пользовательские параметры',
                'p': int(input("  p (простое число): ")),
                'a': int(input("  a: ")),
                'b': int(input("  b: ")),
                'q': int(input("  q (порядок подгруппы): ")),
                'm': int(input("  m (порядок группы): ")),
                'Px': None,
                'Py': None,
            }
        elif choice == '0':
            print("До свидания!")
            break
        else:
            print("Неверный выбор!")
            continue

        try:
            # Создаем экземпляр
            gost = GOSTSignature(params)

            # Генерируем ключи
            print("\nХотите сгенерировать ключи?")
            gen_keys = input("  Введите seed для генерации (или Enter для случайного): ")
            if gen_keys:
                d, Q = gost.generate_key_pair(seed=int(gen_keys))
            else:
                d, Q = gost.generate_key_pair()

            # Ввод сообщения
            message = input("\nВведите сообщение для подписи: ").encode()

            # Подпись
            print("\nФормируем подпись...")
            r, s = gost.sign(message, d, verbose=True)

            # Проверка
            print("\nПроверяем подпись...")
            result = gost.verify(message, r, s, Q, verbose=True)

            print(f"\n{'=' * 50}")
            print(f"РЕЗУЛЬТАТ: {'✅ ПОДПИСЬ ВЕРНА' if result else '❌ ПОДПИСЬ НЕВЕРНА'}")
            print(f"{'=' * 50}")

        except Exception as e:
            print(f"\n❌ Ошибка: {e}")
            print("Проверьте правильность введенных параметров")


# ==================== ТОЧКА ВХОДА ====================

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════════╗
║     ГОСТ Р 34.10-2012 - ЭЛЕКТРОННАЯ ЦИФРОВАЯ ПОДПИСЬ             ║
║     Демонстрация с пошаговым выводом всех вычислений            ║
╚══════════════════════════════════════════════════════════════════╝
    """)

    print("\nВыберите режим работы:")
    print("  1. Автоматическое тестирование всех вариантов (с выводом шагов)")
    print("  2. Интерактивный режим (ручной ввод чисел)")

    mode = input("\nВаш выбор (1 или 2): ")

    if mode == '1':
        test_all_variants()
    else:
        interactive_mode()