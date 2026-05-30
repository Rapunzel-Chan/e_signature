"""
Тесты для ГОСТ Р 34.10-2012 - Электронная цифровая подпись

Тестирование:
1. Модульная арифметика (расширенный алгоритм Евклида, обратный элемент)
2. Эллиптическая кривая (сложение, удвоение, умножение)
3. Теорема Хассе
4. Формирование и проверка подписи
5. Интеграционные тесты
"""

import unittest
import random
import os
import tempfile
import sys

# Добавляем путь к модулям
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from simple_code import (
    ModularArithmetic, HasseTheorem, BinaryVector,
    Point, EllipticCurve, Streebog, GOSTSignature
)


# ============================================================================
# ТЕСТ 1: МОДУЛЬНАЯ АРИФМЕТИКА
# ============================================================================

class TestModularArithmetic(unittest.TestCase):
    """Тесты для класса ModularArithmetic"""

    def test_egcd(self):
        """Тест расширенного алгоритма Евклида"""
        d, x, y = ModularArithmetic.egcd(47, 17)
        self.assertEqual(d, 1)
        self.assertEqual(47 * x + 17 * y, d)

        d, x, y = ModularArithmetic.egcd(100, 35)
        self.assertEqual(d, 5)

    def test_modinv(self):
        """Тест обратного элемента по модулю"""
        inv = ModularArithmetic.modinv(17, 47)
        self.assertEqual((17 * inv) % 47, 1)

        inv = ModularArithmetic.modinv(42, 47)
        self.assertEqual((42 * inv) % 47, 1)
        self.assertEqual(inv, 28)

        with self.assertRaises(ValueError):
            ModularArithmetic.modinv(2, 4)

    def test_mod_pow(self):
        """Тест быстрого возведения в степень"""
        result = ModularArithmetic.mod_pow(2, 10, 100)
        self.assertEqual(result, 24)

        result = ModularArithmetic.mod_pow(3, 4, 100)
        self.assertEqual(result, 81)

        result = ModularArithmetic.mod_pow(5, 0, 100)
        self.assertEqual(result, 1)

    def test_is_prime(self):
        """Тест простоты чисел"""
        self.assertTrue(ModularArithmetic.is_prime(2))
        self.assertTrue(ModularArithmetic.is_prime(3))
        self.assertTrue(ModularArithmetic.is_prime(97))
        self.assertTrue(ModularArithmetic.is_prime(101))

        self.assertFalse(ModularArithmetic.is_prime(1))
        self.assertFalse(ModularArithmetic.is_prime(4))
        self.assertFalse(ModularArithmetic.is_prime(100))
        self.assertFalse(ModularArithmetic.is_prime(30049))


# ============================================================================
# ТЕСТ 2: ТЕОРЕМА ХАССЕ
# ============================================================================

class TestHasseTheorem(unittest.TestCase):
    """Тесты для теоремы Хассе"""

    def test_bounds(self):
        """Тест вычисления границ"""
        min_m, max_m = HasseTheorem.bounds(97)
        self.assertLessEqual(min_m, 78)
        self.assertGreaterEqual(max_m, 118)

        min_m, max_m = HasseTheorem.bounds(101)
        self.assertLessEqual(min_m, 81)
        self.assertGreaterEqual(max_m, 123)

    def test_check(self):
        """Тест проверки порядка"""
        self.assertTrue(HasseTheorem.check(94, 97))
        self.assertTrue(HasseTheorem.check(100, 97))

    def test_verify_curve(self):
        """Тест проверки кривой"""
        result = HasseTheorem.verify_curve(97, 94)
        self.assertEqual(result['p'], 97)
        self.assertEqual(result['actual_m'], 94)
        self.assertTrue(result['is_valid'])


# ============================================================================
# ТЕСТ 3: ДВОИЧНЫЕ ВЕКТОРЫ
# ============================================================================

class TestBinaryVector(unittest.TestCase):
    """Тесты для работы с двоичными векторами"""

    def test_to_int(self):
        """Преобразование двоичного вектора → целое число"""
        self.assertEqual(BinaryVector.to_int("101010"), 42)
        self.assertEqual(BinaryVector.to_int("001100"), 12)
        self.assertEqual(BinaryVector.to_int("010001"), 17)
        self.assertEqual(BinaryVector.to_int("0"), 0)

    def test_to_bits(self):
        """Преобразование целого числа → двоичный вектор"""
        self.assertEqual(BinaryVector.to_bits(42, 6), "101010")
        self.assertEqual(BinaryVector.to_bits(12, 6), "001100")
        self.assertEqual(BinaryVector.to_bits(17, 6), "010001")
        self.assertEqual(BinaryVector.to_bits(5, 8), "00000101")

    def test_concat(self):
        """Конкатенация двоичных векторов"""
        r_bits = "001100"
        s_bits = "010001"
        result = BinaryVector.concat(r_bits, s_bits)
        self.assertEqual(result, "001100010001")


# ============================================================================
# ТЕСТ 4: ТОЧКА НА ЭЛЛИПТИЧЕСКОЙ КРИВОЙ
# ============================================================================

class TestPoint(unittest.TestCase):
    """Тесты для точки на эллиптической кривой"""

    def setUp(self):
        self.p = 97
        self.a = 9
        self.b = 3
        self.P = Point(89, 1, self.a, self.b, self.p)

    def test_on_curve(self):
        """Проверка, что точка лежит на кривой"""
        self.assertTrue(self.P.on_curve())

        fake_point = Point(10, 20, self.a, self.b, self.p)
        self.assertFalse(fake_point.on_curve())

    def test_point_addition(self):
        """Тест сложения точек"""
        P2 = self.P + self.P
        self.assertEqual(P2.x, 4)
        self.assertEqual(P2.y, 54)

        P4 = P2 + P2
        self.assertEqual(P4.x, 91)
        self.assertEqual(P4.y, 86)

        P5 = P4 + self.P
        self.assertEqual(P5.x, 50)
        self.assertEqual(P5.y, 56)

    def test_point_multiplication(self):
        """Тест умножения точки на скаляр"""
        P5 = self.P * 5
        self.assertEqual(P5.x, 50)
        self.assertEqual(P5.y, 56)

        P18 = self.P * 18
        self.assertEqual(P18.x, 12)
        self.assertEqual(P18.y, 44)

        P47 = self.P * 47
        self.assertTrue(P47.is_infinity())

    def test_point_negation(self):
        """Тест отрицания точки"""
        neg_P = -self.P
        result = self.P + neg_P
        self.assertTrue(result.is_infinity())


# ============================================================================
# ТЕСТ 5: ЭЛЛИПТИЧЕСКАЯ КРИВАЯ
# ============================================================================

class TestEllipticCurve(unittest.TestCase):
    """Тесты для эллиптической кривой"""

    def setUp(self):
        self.p = 97
        self.a = 9
        self.b = 3
        self.curve = EllipticCurve(self.p, self.a, self.b)

    def test_discriminant(self):
        """Проверка дискриминанта (должен быть ≠ 0)"""
        discriminant = (4 * self.a**3 + 27 * self.b**2) % self.p
        self.assertNotEqual(discriminant, 0)

    def test_find_all_points(self):
        """Поиск всех точек на кривой"""
        points = self.curve.find_all_points()
        self.assertEqual(len(points), 94)

    def test_get_order(self):
        """Вычисление порядка группы"""
        m = self.curve.get_order(verbose=False)
        self.assertEqual(m, 94)

    def test_find_subgroup_order(self):
        """Поиск порядка подгруппы"""
        q = self.curve.find_subgroup_order(94)
        self.assertEqual(q, 47)

    def test_find_base_point(self):
        """Поиск базовой точки порядка q"""
        q = 47
        P = self.curve.find_base_point(q)
        qP = q * P
        self.assertTrue(qP.is_infinity())


# ============================================================================
# ТЕСТ 6: ХЭШ-ФУНКЦИЯ STREEBOG
# ============================================================================

class TestStreebog(unittest.TestCase):
    """Тесты для хэш-функции Streebog"""

    def test_hash_length(self):
        """Проверка длины хэша"""
        hasher256 = Streebog(256)
        hash256 = hasher256.hash(b"test")
        self.assertEqual(len(hash256) * 8, 256)

        hasher512 = Streebog(512)
        hash512 = hasher512.hash(b"test")
        self.assertEqual(len(hash512) * 8, 512)

    def test_hash_consistency(self):
        """Проверка детерминированности хэш-функции"""
        hasher = Streebog(256)
        hash1 = hasher.hash(b"Hello, world!")
        hash2 = hasher.hash(b"Hello, world!")
        self.assertEqual(hash1, hash2)

        hash3 = hasher.hash(b"Different message")
        self.assertNotEqual(hash1, hash3)

    def test_hash_to_int(self):
        """Преобразование хэша в целое число"""
        hasher = Streebog(256)
        h_int = hasher.hash_to_int(b"test")
        self.assertIsInstance(h_int, int)
        self.assertGreater(h_int, 0)


# ============================================================================
# ТЕСТ 7: ФОРМИРОВАНИЕ И ПРОВЕРКА ПОДПИСИ
# ============================================================================

class TestGOSTSignature(unittest.TestCase):
    """Тесты для основной реализации подписи с auto_params=True"""

    @classmethod
    def setUpClass(cls):
        cls.gost = GOSTSignature(97, 9, 3, 256, auto_params=True)

    def test_generate_key_pair(self):
        """Тест генерации ключевой пары (БЕЗ seed)"""
        # Устанавливаем seed для воспроизводимости в тесте
        random.seed(42)
        d, Q = self.gost.generate_key_pair()
        self.assertIsInstance(d, int)
        self.assertTrue(0 < d < self.gost.q)
        self.assertFalse(Q.is_infinity())

    def test_sign_and_verify(self):
        """Полный цикл: подпись → проверка"""
        random.seed(42)
        d, Q = self.gost.generate_key_pair()
        message = b"Test message for GOST signature"

        r, s, _, _, _ = self.gost.sign(message, d, verbose=False)
        result = self.gost.verify(message, r, s, Q, verbose=False)
        self.assertTrue(result)

    def test_verify_wrong_message(self):
        """Проверка подписи с изменённым сообщением"""
        random.seed(42)
        d, Q = self.gost.generate_key_pair()
        original_message = b"Original message for GOST signature verification test"
        modified_message = b"Modified message with significant changes"

        r, s, _, _, _ = self.gost.sign(original_message, d, verbose=False)
        result = self.gost.verify(modified_message, r, s, Q, verbose=False)

        e1 = self.gost._hash_to_e(original_message)[0]
        e2 = self.gost._hash_to_e(modified_message)[0]

        if e1 == e2:
            self.skipTest(f"Коллизия хэша: e1=e2={e1}")
        else:
            self.assertFalse(result)

    def test_verify_wrong_key(self):
        """Проверка подписи с чужим открытым ключом"""
        random.seed(42)
        d1, Q1 = self.gost.generate_key_pair()
        random.seed(43)
        d2, Q2 = self.gost.generate_key_pair()
        message = b"Secret message"

        r, s, _, _, _ = self.gost.sign(message, d1, verbose=False)
        result = self.gost.verify(message, r, s, Q2, verbose=False)
        self.assertFalse(result)

    def test_signature_serialization(self):
        """Тест сериализации подписи в байты и обратно"""
        random.seed(42)
        d, Q = self.gost.generate_key_pair()
        message = b"Test message"

        r, s, _, _, _ = self.gost.sign(message, d, verbose=False)

        bytes_data = self.gost.signature_to_bytes(r, s)
        r2, s2 = self.gost.signature_from_bytes(bytes_data)

        self.assertEqual(r, r2)
        self.assertEqual(s, s2)


# ============================================================================
# ТЕСТ 8: ПРОВЕРКА ПРИМЕРА ИЗ ЛЕКЦИИ (фиксированные параметры)
# ============================================================================

class TestLectureExample(unittest.TestCase):
    """Тест примера из лекции с фиксированными параметрами"""

    def setUp(self):
        self.gost = GOSTSignature(97, 9, 3, 256,
                                  auto_params=False, q=47, Px=89, Py=1)

    def test_lecture_example_sign(self):
        """Тест примера из лекции: d=5, k=18, e=42 → r=12, s=17"""
        d = 5
        k = 18
        e = 42

        C = k * self.gost.P
        r = C.x % self.gost.q
        s = (r * d + k * e) % self.gost.q

        self.assertEqual(r, 12)
        self.assertEqual(s, 17)

        r_bits = BinaryVector.to_bits(r, 6)
        s_bits = BinaryVector.to_bits(s, 6)
        signature_bits = r_bits + s_bits

        self.assertEqual(r_bits, "001100")
        self.assertEqual(s_bits, "010001")
        self.assertEqual(signature_bits, "001100010001")

    def test_lecture_key_generation(self):
        """Тест: 5·P = (50, 56) из лекции"""
        d = 5
        Q = d * self.gost.P

        self.assertEqual(d, 5)
        self.assertEqual(Q.x, 50)
        self.assertEqual(Q.y, 56)

        P5 = self.gost.P * 5
        self.assertEqual(P5.x, 50)
        self.assertEqual(P5.y, 56)


# ============================================================================
# ТЕСТ 9: РАЗНЫЕ КРИВЫЕ
# ============================================================================

class TestDifferentCurves(unittest.TestCase):
    """Тесты с разными параметрами кривых"""

    def test_curve_with_auto_params(self):
        """Тест кривой с автоматическим вычислением параметров"""
        curves = [
            (97, 9, 3, "Лекционная кривая"),
            (101, 0, 2, "Кривая a=0, b=2"),
            (103, 1, 1, "Кривая a=1, b=1"),
        ]

        message = b"Test message for different curves"

        for p, a, b, name in curves:
            with self.subTest(curve=name):
                gost = GOSTSignature(p, a, b, 256, auto_params=True)
                random.seed(42)
                d, Q = gost.generate_key_pair()
                r, s, _, _, _ = gost.sign(message, d, verbose=False)
                result = gost.verify(message, r, s, Q, verbose=False)
                self.assertTrue(result, f"Ошибка на кривой {name}")


# ============================================================================
# ТЕСТ 10: ИНТЕГРАЦИОННЫЕ ТЕСТЫ
# ============================================================================

class TestIntegration(unittest.TestCase):
    """Интеграционные тесты"""

    def setUp(self):
        self.gost = GOSTSignature(97, 9, 3, 256, auto_params=True)

    def test_full_cycle_with_file(self):
        """Полный цикл: создание файла → подпись → проверка"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("This is a test document for GOST signature.")
            temp_file = f.name

        random.seed(42)
        d, Q = self.gost.generate_key_pair()

        with open(temp_file, 'rb') as f:
            data = f.read()

        r, s, _, _, _ = self.gost.sign(data, d, verbose=False)

        with open(temp_file + ".sig", 'wb') as f:
            f.write(self.gost.signature_to_bytes(r, s))

        with open(temp_file, 'rb') as f:
            data = f.read()
        with open(temp_file + ".sig", 'rb') as f:
            sig_data = f.read()

        r_loaded, s_loaded = self.gost.signature_from_bytes(sig_data)
        result = self.gost.verify(data, r_loaded, s_loaded, Q, verbose=False)
        self.assertTrue(result)

        os.remove(temp_file)
        os.remove(temp_file + ".sig")

    def test_modified_file_fails(self):
        """Изменённый файл не проходит проверку"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("Original content")
            temp_file = f.name

        random.seed(42)
        d, Q = self.gost.generate_key_pair()

        with open(temp_file, 'rb') as f:
            data = f.read()

        r, s, _, _, _ = self.gost.sign(data, d, verbose=False)

        with open(temp_file, 'w') as f:
            f.write("Modified content!!!")

        with open(temp_file, 'rb') as f:
            modified_data = f.read()

        result = self.gost.verify(modified_data, r, s, Q, verbose=False)
        self.assertFalse(result)

        os.remove(temp_file)


# ============================================================================
# ТЕСТ 11: КРАЕВЫЕ СЛУЧАИ
# ============================================================================

class TestEdgeCases(unittest.TestCase):
    """Тесты краевых случаев"""

    def setUp(self):
        self.gost = GOSTSignature(97, 9, 3, 256, auto_params=True)

    def test_empty_message(self):
        """Пустое сообщение"""
        random.seed(42)
        d, Q = self.gost.generate_key_pair()
        empty_message = b""

        r, s, _, _, _ = self.gost.sign(empty_message, d, verbose=False)
        result = self.gost.verify(empty_message, r, s, Q, verbose=False)
        self.assertTrue(result)

    def test_large_message(self):
        """Большое сообщение (1KB)"""
        random.seed(42)
        d, Q = self.gost.generate_key_pair()
        large_message = b"X" * 1024

        r, s, _, _, _ = self.gost.sign(large_message, d, verbose=False)
        result = self.gost.verify(large_message, r, s, Q, verbose=False)
        self.assertTrue(result)

    def test_invalid_signature_range(self):
        """Подпись с r или s вне диапазона"""
        random.seed(42)
        d, Q = self.gost.generate_key_pair()
        message = b"Test"

        result = self.gost.verify(message, 0, 1, Q, verbose=False)
        self.assertFalse(result)

        result = self.gost.verify(message, 1, self.gost.q, Q, verbose=False)
        self.assertFalse(result)


# ============================================================================
# ТЕСТ 12: ПРОВЕРКА ТЕОРЕМЫ ХАССЕ ДЛЯ РАЗНЫХ КРИВЫХ
# ============================================================================

class TestHasseForCurves(unittest.TestCase):
    """Проверка теоремы Хассе для разных кривых"""

    def test_hasse_for_lecture_curve(self):
        """Лекционная кривая: p=97, m=94"""
        p, a, b = 97, 9, 3
        curve = EllipticCurve(p, a, b)
        m = curve.get_order(verbose=False)
        min_m, max_m = HasseTheorem.bounds(p)
        self.assertGreaterEqual(m, min_m)
        self.assertLessEqual(m, max_m)

    def test_hasse_for_curve_a0(self):
        """Кривая a=0: p=101, b=2"""
        p, a, b = 101, 0, 2
        curve = EllipticCurve(p, a, b)
        m = curve.get_order(verbose=False)
        min_m, max_m = HasseTheorem.bounds(p)
        self.assertGreaterEqual(m, min_m)
        self.assertLessEqual(m, max_m)

    def test_hasse_for_curve_b1(self):
        """Кривая b=1: p=103, a=1, b=1"""
        p, a, b = 103, 1, 1
        curve = EllipticCurve(p, a, b)
        m = curve.get_order(verbose=False)
        min_m, max_m = HasseTheorem.bounds(p)
        self.assertGreaterEqual(m, min_m)
        self.assertLessEqual(m, max_m)


# ============================================================================
# ЗАПУСК ТЕСТОВ
# ============================================================================

def run_tests():
    print("\n" + "=" * 70)
    print("ЗАПУСК МОДУЛЬНЫХ ТЕСТОВ ДЛЯ ГОСТ Р 34.10-2012")
    print("=" * 70)

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestModularArithmetic))
    suite.addTests(loader.loadTestsFromTestCase(TestHasseTheorem))
    suite.addTests(loader.loadTestsFromTestCase(TestBinaryVector))
    suite.addTests(loader.loadTestsFromTestCase(TestPoint))
    suite.addTests(loader.loadTestsFromTestCase(TestEllipticCurve))
    suite.addTests(loader.loadTestsFromTestCase(TestStreebog))
    suite.addTests(loader.loadTestsFromTestCase(TestGOSTSignature))
    suite.addTests(loader.loadTestsFromTestCase(TestLectureExample))
    suite.addTests(loader.loadTestsFromTestCase(TestDifferentCurves))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    suite.addTests(loader.loadTestsFromTestCase(TestHasseForCurves))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "=" * 70)
    print("СВОДКА РЕЗУЛЬТАТОВ ТЕСТИРОВАНИЯ")
    print("=" * 70)
    print(f"  Тестов выполнено: {result.testsRun}")
    print(f"  Успешно: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"  Ошибок: {len(result.errors)}")
    print(f"  Провалов: {len(result.failures)}")

    if result.wasSuccessful():
        print("\n✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
    else:
        print("\n❌ НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОЙДЕНЫ")

    return result


if __name__ == "__main__":
    import sys
    from io import StringIO

    captured_output = StringIO()
    sys.stdout = captured_output

    try:
        result = run_tests()
    finally:
        sys.stdout = sys.__stdout__
        if not result.wasSuccessful():
            print(captured_output.getvalue())