"""
ГОСТ Р 34.10-2012 - ИНТЕРАКТИВНЫЙ РЕЖИМ
Полная работа с файлами: подпись, проверка, генерация ключей
"""

import os
import sys
import random
from verify_gost_compliance import GOSTSignature, HasseTheorem
from verify_gost_compliance import Point


def print_header():
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    ГОСТ Р 34.10-2012 - ЭЛЕКТРОННАЯ ПОДПИСЬ                    ║
║                                                                              ║
║  Полная реализация:                                                         ║
║    - Хэш-функция Streebog (ГОСТ Р 34.11-2012) с выбором 256/512 бит        ║
║    - Эллиптическая кривая с теоремой Хассе                                   ║
║    - Алгоритмы подписи и проверки (ГОСТ Р 34.10-2012)                       ║
║    - Работа с файлами (подпись, проверка)                                   ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)


def select_hash_length() -> int:
    """Выбор длины хэша"""
    print("\nВыберите длину хэша (ГОСТ Р 34.11-2012):")
    print("  1. 256 бит (стандартный)")
    print("  2. 512 бит (повышенная стойкость)")
    choice = input("\nВаш выбор (1-2): ")
    return 512 if choice == '2' else 256


def select_curve_params():
    """Выбор параметров кривой"""
    print("\n" + "=" * 60)
    print("ВЫБОР ПАРАМЕТРОВ ЭЛЛИПТИЧЕСКОЙ КРИВОЙ")
    print("=" * 60)
    print("  1. Учебный пример (p=97, a=9, b=3) - для тестов")
    print("  2. Случайные параметры (в заданном диапазоне)")
    print("  3. Ввести свои параметры")
    print("  4. Вернуться к предыдущему меню (оставить текущие)")

    choice = input("\nВаш выбор (1-4): ")

    if choice == '1':
        return 97, 9, 3, "Учебный пример (p=97, a=9, b=3)"

    elif choice == '2':
        print("\nГенерация случайных параметров...")
        primes = [97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193,
                  197, 199]
        p = random.choice(primes)
        a = random.randint(0, p - 1)
        b = random.randint(0, p - 1)

        disc = (4 * a ** 3 + 27 * b ** 2) % p
        while disc == 0:
            a = random.randint(0, p - 1)
            b = random.randint(0, p - 1)
            disc = (4 * a ** 3 + 27 * b ** 2) % p

        print(f"\nСгенерированы параметры:")
        print(f"  p = {p}")
        print(f"  a = {a}")
        print(f"  b = {b}")
        return p, a, b, f"Случайные параметры (p={p}, a={a}, b={b})"

    elif choice == '3':
        print("\nВведите параметры кривой:")
        p = int(input("  p (простое число): "))
        a = int(input("  a: "))
        b = int(input("  b: "))
        return p, a, b, f"Пользовательские параметры (p={p}, a={a}, b={b})"

    else:
        return None, None, None, None


def print_menu(gost):
    """Выводит главное меню"""
    print("\n" + "─" * 60)
    print(f"ТЕКУЩИЕ ПАРАМЕТРЫ: p={gost.p}, a={gost.a}, b={gost.b}, q={gost.q}")
    print("─" * 60)
    print("ДОСТУПНЫЕ ОПЕРАЦИИ:")
    print("  1. Сгенерировать ключевую пару")
    print("  2. Подписать файл")
    print("  3. Проверить подпись файла")
    print("  4. Показать параметры (с теоремой Хассе)")
    print("  5. Сменить параметры эллиптической кривой")
    print("  0. Выход")
    print("─" * 60)


def show_params(gost):
    """Показывает параметры кривой"""
    print("\n" + "=" * 60)
    print("ПАРАМЕТРЫ ЭЛЛИПТИЧЕСКОЙ КРИВОЙ")
    print("=" * 60)
    print(f"  Уравнение: y² = x³ + {gost.a}x + {gost.b} (mod {gost.p})")
    print(f"  Порядок подгруппы q = {gost.q}")
    print(f"  Базовая точка P = {gost.P}")
    print(f"  Длина хэша: {gost.hash_len} бит")
    print(f"  Длина подписи: {gost.component_bits * 2} бит")

    # Теорема Хассе
    if hasattr(gost, 'm') and gost.m:
        hasse = HasseTheorem.verify_curve(gost.p, gost.m)
        print(f"\n  ТЕОРЕМА ХАССЕ:")
        print(f"    {hasse['formula']}")
        print(f"    √{gost.p} ≈ {hasse['sqrt_p']:.4f}")
        print(f"    2√p ≈ {hasse['2_sqrt_p']:.4f}")
        print(f"    Диапазон: {hasse['range']}")
        print(f"    m = {gost.m} → {'✅' if hasse['is_valid'] else '❌'}")
    print("=" * 60)


"""
ГОСТ Р 34.10-2012 - ИНТЕРАКТИВНЫЙ РЕЖИМ
Полная работа с файлами: подпись, проверка, генерация ключей

ВАЖНО: Для p > 2000 автоматический перебор точек НЕ производится.
       В таком случае пользователь должен указать параметры q, Px, Py вручную.
"""

import os
import random
from simple_code import GOSTSignature
from simple_code import Point

# Порог для автоматического вычисления параметров
# Для p > AUTO_THRESHOLD требуется ручной ввод q, Px, Py
AUTO_THRESHOLD = 2000


def print_header():
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    ГОСТ Р 34.10-2012 - ЭЛЕКТРОННАЯ ПОДПИСЬ                    ║
║                                                                              ║
║  Полная реализация:                                                         ║
║    - Хэш-функция Streebog (ГОСТ Р 34.11-2012) с выбором 256/512 бит        ║
║    - Эллиптическая кривая с теоремой Хассе                                   ║
║    - Алгоритмы подписи и проверки (ГОСТ Р 34.10-2012)                       ║
║    - Работа с файлами (подпись, проверка)                                   ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)


def select_hash_length() -> int:
    """Выбор длины хэша"""
    print("\nВыберите длину хэша (ГОСТ Р 34.11-2012):")
    print("  1. 256 бит (стандартный)")
    print("  2. 512 бит (повышенная стойкость)")
    choice = input("\nВаш выбор (1-2): ")
    return 512 if choice == '2' else 256


def select_curve_params():
    """
    Выбор параметров кривой

    Возвращает кортеж из 8 элементов:
    (p, a, b, auto_params, q, Px, Py, params_name)

    auto_params = True  → программа вычисляет m, q, P автоматически
    auto_params = False → используются ручные значения q, Px, Py
    """
    print("\n" + "=" * 60)
    print("ВЫБОР ПАРАМЕТРОВ ЭЛЛИПТИЧЕСКОЙ КРИВОЙ")
    print("=" * 60)
    print("  1. Учебный пример (p=97, a=9, b=3) - для тестов")
    print("  2. Случайные параметры (в заданном диапазоне)")
    print("  3. Ввести свои параметры")
    print("  4. Вернуться к предыдущему меню (оставить текущие)")

    choice = input("\nВаш выбор (1-4): ")

    # Учебный пример
    if choice == '1':
        p, a, b = 97, 9, 3
        # Для учебного примера p < AUTO_THRESHOLD → авто-вычисление
        return (p, a, b, True, None, None, None,
                f"Учебный пример (p={p}, a={a}, b={b})")

    # Случайные параметры (только маленькие p)
    elif choice == '2':
        print("\nГенерация случайных параметров...")
        # Используем только маленькие p для учебных целей
        primes = [97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193,
                  197, 199]
        p = random.choice(primes)
        a = random.randint(0, p - 1)
        b = random.randint(0, p - 1)

        # Проверка дискриминанта
        disc = (4 * a ** 3 + 27 * b ** 2) % p
        while disc == 0:
            a = random.randint(0, p - 1)
            b = random.randint(0, p - 1)
            disc = (4 * a ** 3 + 27 * b ** 2) % p

        print(f"\nСгенерированы параметры:")
        print(f"  p = {p}")
        print(f"  a = {a}")
        print(f"  b = {b}")
        print(f"\n(p = {p} < {AUTO_THRESHOLD} → автоматическое вычисление)")
        return (p, a, b, True, None, None, None,
                f"Случайные параметры (p={p}, a={a}, b={b})")

    # Ввести свои параметры
    elif choice == '3':
        print("\nВведите параметры кривой:")
        p = int(input("  p (простое число): "))
        a = int(input("  a: "))
        b = int(input("  b: "))

        # Проверка: если p большое, нужно ввести q, Px, Py вручную
        if p > AUTO_THRESHOLD:
            print(f"\n⚠️  p = {p} > {AUTO_THRESHOLD}")
            print("   Для больших p автоматическое вычисление НЕ производится.")
            print("   Необходимо ввести параметры вручную:")
            q = int(input("  q (порядок подгруппы, простое число): "))
            Px = int(input("  Px (x-координата базовой точки): "))
            Py = int(input("  Py (y-координата базовой точки): "))
            return (p, a, b, False, q, Px, Py,
                    f"Пользовательские параметры (p={p}, a={a}, b={b})")
        else:
            # Для маленьких p можно авто-вычисление
            print(f"\n(p = {p} < {AUTO_THRESHOLD} → автоматическое вычисление)")
            return (p, a, b, True, None, None, None,
                    f"Пользовательские параметры (p={p}, a={a}, b={b})")

    else:
        return (None, None, None, None, None, None, None, None)


def print_menu(gost):
    """Выводит главное меню"""
    print("\n" + "─" * 60)
    print(f"ТЕКУЩИЕ ПАРАМЕТРЫ: p={gost.p}, a={gost.a}, b={gost.b}, q={gost.q}")
    print("─" * 60)
    print("ДОСТУПНЫЕ ОПЕРАЦИИ:")
    print("  1. Сгенерировать ключевую пару")
    print("  2. Подписать файл")
    print("  3. Проверить подпись файла")
    print("  4. Показать параметры (с теоремой Хассе)")
    print("  5. Сменить параметры эллиптической кривой")
    print("  0. Выход")
    print("─" * 60)


def show_params(gost):
    """Показывает параметры кривой"""
    print("\n" + "=" * 60)
    print("ПАРАМЕТРЫ ЭЛЛИПТИЧЕСКОЙ КРИВОЙ")
    print("=" * 60)
    print(f"  Уравнение: y² = x³ + {gost.a}x + {gost.b} (mod {gost.p})")
    print(f"  Порядок подгруппы q = {gost.q}")
    print(f"  Базовая точка P = {gost.P}")
    print(f"  Длина хэша: {gost.hash_len} бит")
    print(f"  Длина подписи: {gost.component_bits * 2} бит")

    # Используем уже вычисленные данные из gost
    if hasattr(gost, 'm') and gost.m:
        from simple_code import HasseTheorem
        hasse = HasseTheorem.verify_curve(gost.p, gost.m)
        print(f"\n  ТЕОРЕМА ХАССЕ:")
        print(f"    {hasse['formula']}")
        print(f"    √{gost.p} ≈ {hasse['sqrt_p']:.4f}")
        print(f"    2√p ≈ {hasse['2_sqrt_p']:.4f}")
        print(f"    Диапазон: {hasse['range']}")
        print(f"    m = {gost.m} → {'✅' if hasse['is_valid'] else '❌'}")
    print("=" * 60)


def main():
    print_header()

    # Выбор длины хэша
    hash_len = select_hash_length()
    print(f"\n✅ Используется хэш-функция Streebog-{hash_len}")

    # Выбор параметров кривой (возвращает 8 значений)
    p, a, b, auto_params, q, Px, Py, params_name = select_curve_params()

    if p is None:
        print("❌ Некорректный выбор, используем учебный пример")
        p, a, b = 97, 9, 3
        auto_params = True
        q = Px = Py = None
        params_name = "Учебный пример (p=97, a=9, b=3)"

    # Создание экземпляра подписи с правильными параметрами
    try:
        print(f"\n🔧 Инициализация с параметрами: {params_name}")

        # Передаем правильные параметры в конструктор
        if auto_params:
            gost = GOSTSignature(p, a, b, hash_len, auto_params=True)
        else:
            gost = GOSTSignature(p, a, b, hash_len, auto_params=False,
                                 q=q, Px=Px, Py=Py)
    except Exception as e:
        print(f"\n❌ Ошибка инициализации: {e}")
        print("Используем учебный пример")
        gost = GOSTSignature(97, 9, 3, hash_len, auto_params=True)

    current_private = None
    current_public = None

    while True:
        print_menu(gost)
        choice = input("Выберите операцию: ")

        # 1. ГЕНЕРАЦИЯ КЛЮЧЕЙ
        if choice == '1':
            print("\n--- ГЕНЕРАЦИЯ КЛЮЧЕВОЙ ПАРЫ ---")
            print("⚠️  Seed используется ТОЛЬКО для воспроизводимости результатов.")
            print("    Он НЕ связан с хэшем сообщения и НЕ влияет на безопасность.")
            use_seed = input("Использовать фиксированный seed 42 для отладки? (y/n): ").lower()
            seed = 42 if use_seed == 'y' else None

            d, Q = gost.generate_key_pair(seed)
            current_private = d
            current_public = Q

            with open("private.key", "w") as f:
                f.write(str(d))
            with open("public.key", "w") as f:
                f.write(f"{Q.x}\n{Q.y}")

            print(f"\n✅ Ключи сохранены:")
            print(f"   private.key (d = {d})")
            print(f"   public.key (Q = {Q})")

        # 2. ПОДПИСАНИЕ ФАЙЛА
        elif choice == '2':
            print("\n--- ПОДПИСАНИЕ ФАЙЛА ---")
            file_path = input("Путь к файлу: ").strip()

            if not os.path.exists(file_path):
                print("❌ Файл не найден")
                continue

            if current_private is None:
                if not os.path.exists("private.key"):
                    print("❌ Нет секретного ключа. Сначала операция 1")
                    continue
                with open("private.key", "r") as f:
                    d = int(f.read().strip())
                print(f"Загружен секретный ключ: d = {d}")
            else:
                d = current_private

            with open(file_path, 'rb') as f:
                data = f.read()

            print(f"\n📄 Файл: {file_path} ({len(data)} байт)")
            print(f"🔐 Хэширование по Streebog-{gost.hash_len}...")

            r, s, r_bits, s_bits, signature_bits = gost.sign(data, d, verbose=True)

            sig_path = file_path + ".sig"
            with open(sig_path, 'wb') as f:
                f.write(gost.signature_to_bytes(r, s))

            print(f"\n✅ Подпись сохранена: {sig_path}")
            print(f"   r = {r}")
            print(f"   s = {s}")
            print(f"   r̄ = {r_bits}")
            print(f"   s̄ = {s_bits}")
            print(f"   ζ = {signature_bits}")

        # 3. ПРОВЕРКА ПОДПИСИ
        elif choice == '3':
            print("\n--- ПРОВЕРКА ПОДПИСИ ---")
            file_path = input("Путь к файлу: ").strip()
            sig_path = input("Путь к подписи: ").strip()

            if not os.path.exists(file_path):
                print("❌ Файл не найден")
                continue
            if not os.path.exists(sig_path):
                print("❌ Подпись не найдена")
                continue

            if current_public is None:
                if not os.path.exists("public.key"):
                    print("❌ Нет открытого ключа. Сначала операция 1")
                    continue
                with open("public.key", "r") as f:
                    x = int(f.readline().strip())
                    y = int(f.readline().strip())
                Q = Point(x, y, gost.a, gost.b, gost.p)
                print(f"Загружен открытый ключ: Q = {Q}")
            else:
                Q = current_public

            with open(file_path, 'rb') as f:
                data = f.read()
            with open(sig_path, 'rb') as f:
                sig_data = f.read()

            r, s = gost.signature_from_bytes(sig_data)

            print(f"\n📄 Файл: {file_path} ({len(data)} байт)")
            print(f"📝 Подпись: r={r}, s={s}")
            print(f"🔑 Открытый ключ: Q={Q}")

            result = gost.verify(data, r, s, Q, verbose=True)

            print("\n" + "=" * 40)
            if result:
                print("✅ ПОДПИСЬ ВЕРНА")
                print("   Файл аутентичен, авторство подтверждено")
            else:
                print("❌ ПОДПИСЬ НЕВЕРНА")
                print("   Файл был изменен или подпись подделана")
            print("=" * 40)

        # 4. ПОКАЗАТЬ ПАРАМЕТРЫ
        elif choice == '4':
            show_params(gost)

        # 5. СМЕНИТЬ ПАРАМЕТРЫ КРИВОЙ
        elif choice == '5':
            print("\n" + "=" * 60)
            print("⚠️  ВНИМАНИЕ: При смене параметров старые ключи станут недействительными!")
            confirm = input("Продолжить? (y/n): ").lower()
            if confirm != 'y':
                continue

            # Получаем 8 значений
            p, a, b, auto_params, q, Px, Py, params_name = select_curve_params()

            if p is None:
                print("❌ Параметры не изменены")
                continue

            try:
                print(f"\n🔧 Инициализация с новыми параметрами: {params_name}")
                if auto_params:
                    gost = GOSTSignature(p, a, b, hash_len, auto_params=True)
                else:
                    gost = GOSTSignature(p, a, b, hash_len, auto_params=False,
                                         q=q, Px=Px, Py=Py)
                current_private = None
                current_public = None
                print(f"\n✅ Параметры кривой изменены!")
            except Exception as e:
                print(f"\n❌ Ошибка: {e}")

        # 0. ВЫХОД
        elif choice == '0':
            print("\nДо свидания!")
            break

        else:
            print("\n❌ Неверный выбор!")


if __name__ == "__main__":
    main()