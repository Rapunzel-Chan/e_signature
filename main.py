"""
ГОСТ Р 34.10-2012 - ИНТЕРАКТИВНЫЙ РЕЖИМ
Полная работа с файлами: подпись, проверка, генерация ключей
"""

import os
import random
from simple_code import GOSTSignature, HasseTheorem, Point, SignatureMetadata, BinaryVector

# Порог для автоматического вычисления параметров
AUTO_THRESHOLD = 2000


def print_header():
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    ГОСТ Р 34.10-2012 - ЭЛЕКТРОННАЯ ПОДПИСЬ                   ║
║                                                                              ║
║  Полная реализация:                                                          ║
║    - Хэш-функция Streebog (ГОСТ Р 34.11-2012) с выбором 256/512 бит          ║
║    - Эллиптическая кривая с теоремой Хассе                                   ║
║    - Алгоритмы подписи и проверки (ГОСТ Р 34.10-2012)                        ║
║    - Работа с файлами (подпись, проверка)                                    ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)


def select_hash_length() -> int:
    """Выбор длины хэша"""
    print("\nВыберите длину хэша (ГОСТ Р 34.11-2012):")
    print("  1. 256 бит (стандартный)")
    print("  2. 512 бит (повышенная стойкость)")
    choice = input("\nВаш выбор (1-2): ")
    return 512 if choice == '2' else 256


def setup_lecture_example(hash_len: int) -> GOSTSignature:
    """
    НАСТРОЙКА УЧЕБНОГО ПРИМЕРА ИЗ ЛЕКЦИИ

    Все параметры жестко заданы как в лекции 18:
        p = 97, a = 9, b = 3
        q = 47
        P = (89, 1)  # (-8, 1) mod 97
        d = 5
        Q = 5·P = (50, 56)
    """
    print("\n🔧 ИНИЦИАЛИЗАЦИЯ УЧЕБНОГО ПРИМЕРА (ЛЕКЦИЯ 18)")
    print("   Параметры: p=97, a=9, b=3, q=47, P=(89,1)")

    # Создаём кривую с фиксированными параметрами
    gost = GOSTSignature(97, 9, 3, hash_len, auto_params=False, q=47, Px=89, Py=1)

    # Устанавливаем лекционные ключи d=5
    print("\n📚 Установка лекционных ключей (d=5)...")
    d, Q = gost.set_lecture_keys()

    # Сохраняем ключи в файлы
    with open("private.key", "w") as f:
        f.write(str(d))
    with open("public.key", "w") as f:
        f.write(f"{Q.x}\n{Q.y}")

    print(f"\n✅ Лекционные ключи сохранены:")
    print(f"   private.key (d = {d})")
    print(f"   public.key (Q = {Q})")

    return gost, d, Q


def setup_random_params(hash_len: int):
    """Генерация случайных параметров (маленькие p)"""
    print("\n🔧 ГЕНЕРАЦИЯ СЛУЧАЙНЫХ ПАРАМЕТРОВ")

    primes = [97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151,
              157, 163, 167, 173, 179, 181, 191, 193, 197, 199]
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

    gost = GOSTSignature(p, a, b, hash_len, auto_params=True)
    return gost, None, None


def setup_custom_params(hash_len: int):
    """Ввод своих параметров"""
    print("\n🔧 ВВОД СВОИХ ПАРАМЕТРОВ")

    p = int(input("  p (простое число): "))
    a = int(input("  a: "))
    b = int(input("  b: "))

    if p > AUTO_THRESHOLD:
        print(f"\n⚠️  p = {p} > {AUTO_THRESHOLD}")
        print("   Для больших p необходимо ввести параметры вручную:")
        q = int(input("  q (порядок подгруппы, простое число): "))
        Px = int(input("  Px (x-координата базовой точки): "))
        Py = int(input("  Py (y-координата базовой точки): "))
        gost = GOSTSignature(p, a, b, hash_len, auto_params=False, q=q, Px=Px, Py=Py)
    else:
        gost = GOSTSignature(p, a, b, hash_len, auto_params=True)

    return gost, None, None


def print_menu(gost):
    """Выводит главное меню"""
    print("\n" + "─" * 60)
    print(f"ТЕКУЩИЕ ПАРАМЕТРЫ: p={gost.p}, a={gost.a}, b={gost.b}, q={gost.q}")
    print("─" * 60)
    print("ДОСТУПНЫЕ ОПЕРАЦИИ:")
    print("  1. Сгенерировать новую ключевую пару")
    print("  2. Подписать файл")
    print("  3. Проверить подпись файла")
    print("  4. Показать параметры (с теоремой Хассе)")
    print("  5. Сменить параметры эллиптической кривой")
    print("  6. Загрузить ключи из файлов")
    print("  7. Ввести ключи вручную")
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

    if hasattr(gost, 'm') and gost.m:
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

    # НАЧАЛЬНАЯ НАСТРОЙКА: выбор типа параметров
    print("\n" + "=" * 60)
    print("НАЧАЛЬНАЯ НАСТРОЙКА")
    print("=" * 60)
    print("  1. Учебный пример (p=97, a=9, b=3, P=(89,1), d=5) - КАК В ЛЕКЦИИ")
    print("  2. Случайные параметры (маленькие числа)")
    print("  3. Ввести свои параметры")

    setup_choice = input("\nВаш выбор (1-3): ")

    if setup_choice == '1':
        gost, current_private, current_public = setup_lecture_example(hash_len)
    elif setup_choice == '2':
        gost, current_private, current_public = setup_random_params(hash_len)
    elif setup_choice == '3':
        gost, current_private, current_public = setup_custom_params(hash_len)
    else:
        print("❌ Неверный выбор, используем учебный пример")
        gost, current_private, current_public = setup_lecture_example(hash_len)

    while True:
        print_menu(gost)
        choice = input("Выберите операцию: ")

        # 1. ГЕНЕРАЦИЯ НОВОЙ КЛЮЧЕВОЙ ПАРЫ (СЛУЧАЙНАЯ)
        if choice == '1':
            print("\n--- ГЕНЕРАЦИЯ НОВОЙ КЛЮЧЕВОЙ ПАРЫ ---")
            d, Q = gost.generate_key_pair()
            current_private = d
            current_public = Q

            with open("private.key", "w") as f:
                f.write(str(d))
            with open("public.key", "w") as f:
                f.write(f"{Q.x}\n{Q.y}")

            print(f"\n✅ Новые ключи сохранены:")
            print(f"   private.key (d = {d})")
            print(f"   public.key (Q = {Q})")

        # 2. ПОДПИСАНИЕ ФАЙЛА
        elif choice == '2':
            print("\n--- ПОДПИСАНИЕ ФАЙЛА ---")
            file_path = input("Путь к файлу: ").strip()

            if not os.path.exists(file_path):
                print("❌ Файл не найден")
                continue

            # Запрос метаданных
            add_metadata = input("Добавить информацию об авторе и дате? (y/n): ").lower()

            author = None
            validity_days = 365

            if add_metadata == 'y':
                author = input("  Введите имя автора: ").strip()
                if not author:
                    author = "Unknown"
                days = input("  Срок действия в днях (Enter = 365): ").strip()
                if days:
                    validity_days = int(days)

            # Выбор ключа
            if current_private is None:
                if not os.path.exists("private.key"):
                    print("❌ Нет секретного ключа. Сначала операция 1 или загрузите ключи")
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

            if add_metadata == 'y' and author:
                r, s, metadata = gost.sign_with_metadata(data, d, author, validity_days, verbose=True)
                metadata_bytes = metadata.to_bytes()
                separator = b"\n---SIGNED_DATA---\n"
                signed_data = metadata_bytes + separator + data
                signed_path = file_path + ".signed"
                with open(signed_path, 'wb') as f:
                    f.write(signed_data)
                print(f"\n✅ Подписанный файл сохранён: {signed_path}")
                r_bits = BinaryVector.to_bits(r, gost.component_bits)
                s_bits = BinaryVector.to_bits(s, gost.component_bits)
                signature_bits = r_bits + s_bits
            else:
                r, s, r_bits, s_bits, signature_bits = gost.sign(data, d, verbose=True)

            sig_path = file_path + ".sig"
            with open(sig_path, 'wb') as f:
                f.write(gost.signature_to_bytes(r, s))

            print(f"\n✅ Подпись сохранена: {sig_path}")
            print(f"   r = {r}")
            print(f"   s = {s}")
            if r_bits and s_bits:
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
                    print("❌ Нет открытого ключа. Сначала операция 1 или загрузите ключи")
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
            else:
                print("❌ ПОДПИСЬ НЕВЕРНА")
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

            print("\nВыберите новые параметры:")
            print("  1. Учебный пример (лекция)")
            print("  2. Случайные параметры")
            print("  3. Ввести свои параметры")

            new_choice = input("\nВаш выбор (1-3): ")

            if new_choice == '1':
                gost, current_private, current_public = setup_lecture_example(hash_len)
            elif new_choice == '2':
                gost, current_private, current_public = setup_random_params(hash_len)
            elif new_choice == '3':
                gost, current_private, current_public = setup_custom_params(hash_len)
            else:
                print("❌ Неверный выбор, параметры не изменены")
                continue

            print(f"\n✅ Параметры кривой изменены!")

        # 6. ЗАГРУЗИТЬ КЛЮЧИ ИЗ ФАЙЛОВ
        elif choice == '6':
            print("\n--- ЗАГРУЗКА КЛЮЧЕЙ ИЗ ФАЙЛОВ ---")

            priv_file = input("Файл с секретным ключом (private.key): ").strip()
            if not priv_file:
                priv_file = "private.key"

            if os.path.exists(priv_file):
                with open(priv_file, "r") as f:
                    current_private = int(f.read().strip())
                print(f"✅ Загружен секретный ключ: d = {current_private}")
            else:
                print(f"❌ Файл {priv_file} не найден")

            pub_file = input("Файл с открытым ключом (public.key): ").strip()
            if not pub_file:
                pub_file = "public.key"

            if os.path.exists(pub_file):
                with open(pub_file, "r") as f:
                    x = int(f.readline().strip())
                    y = int(f.readline().strip())
                current_public = Point(x, y, gost.a, gost.b, gost.p)
                print(f"✅ Загружен открытый ключ: Q = {current_public}")
            else:
                print(f"❌ Файл {pub_file} не найден")

        # 7. Ввести ключи вручную
        elif choice == '7':
            print("\n--- ВВОД КЛЮЧЕЙ ВРУЧНУЮ ---")

            d_str = input("Введите секретный ключ d: ").strip()
            if d_str:
                current_private = int(d_str)
                print(f"✅ Установлен секретный ключ: d = {current_private}")

            x_str = input("Введите x-координату открытого ключа: ").strip()
            y_str = input("Введите y-координату открытого ключа: ").strip()
            if x_str and y_str:
                current_public = Point(int(x_str), int(y_str), gost.a, gost.b, gost.p)
                print(f"✅ Установлен открытый ключ: Q = {current_public}")

        # 0. ВЫХОД
        elif choice == '0':
            print("\nДо свидания!")
            break

        else:
            print("\n❌ Неверный выбор!")


if __name__ == "__main__":
    main()

# """
# ГОСТ Р 34.10-2012 - ИНТЕРАКТИВНЫЙ РЕЖИМ
# Полная работа с файлами: подпись, проверка, генерация ключей
# """
# from simple_code import GOSTSignature, HasseTheorem, Point, SignatureMetadata, BinaryVector
# import os
# import sys
# import random
# from test_simple_code import GOSTSignature, HasseTheorem
# from test_simple_code import Point
#
#
# def print_header():
#     print("""
# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                    ГОСТ Р 34.10-2012 - ЭЛЕКТРОННАЯ ПОДПИСЬ                   ║
# ║                                                                              ║
# ║  Полная реализация:                                                          ║
# ║    - Хэш-функция Streebog (ГОСТ Р 34.11-2012) с выбором 256/512 бит          ║
# ║    - Эллиптическая кривая с теоремой Хассе                                   ║
# ║    - Алгоритмы подписи и проверки (ГОСТ Р 34.10-2012)                        ║
# ║    - Работа с файлами (подпись, проверка)                                    ║
# ╚══════════════════════════════════════════════════════════════════════════════╝
#     """)
#
#
# def select_hash_length() -> int:
#     """Выбор длины хэша"""
#     print("\nВыберите длину хэша (ГОСТ Р 34.11-2012):")
#     print("  1. 256 бит (стандартный)")
#     print("  2. 512 бит (повышенная стойкость)")
#     choice = input("\nВаш выбор (1-2): ")
#     return 512 if choice == '2' else 256
#
#
# def select_curve_params():
#     """Выбор параметров кривой"""
#     print("\n" + "=" * 60)
#     print("ВЫБОР ПАРАМЕТРОВ ЭЛЛИПТИЧЕСКОЙ КРИВОЙ")
#     print("=" * 60)
#     print("  1. Учебный пример (p=97, a=9, b=3) - для тестов")
#     print("  2. Случайные параметры (в заданном диапазоне)")
#     print("  3. Ввести свои параметры")
#     print("  4. Вернуться к предыдущему меню (оставить текущие)")
#
#     choice = input("\nВаш выбор (1-4): ")
#
#     # Учебный пример (с лекционными ключами d=5)
#     if choice == '1':
#         p, a, b = 97, 9, 3
#         # Для учебного примера используем авто-вычисление
#         # и устанавливаем флаг use_lecture_keys=True
#         return (p, a, b, True, None, None, None, True,
#                 f"Учебный пример (p={p}, a={a}, b={b})")
#
#     # Случайные параметры
#     elif choice == '2':
#         print("\nГенерация случайных параметров...")
#         primes = [97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151,
#                   157, 163, 167, 173, 179, 181, 191, 193, 197, 199]
#         p = random.choice(primes)
#         a = random.randint(0, p - 1)
#         b = random.randint(0, p - 1)
#
#         disc = (4 * a ** 3 + 27 * b ** 2) % p
#         while disc == 0:
#             a = random.randint(0, p - 1)
#             b = random.randint(0, p - 1)
#             disc = (4 * a ** 3 + 27 * b ** 2) % p
#
#         print(f"\nСгенерированы параметры:")
#         print(f"  p = {p}")
#         print(f"  a = {a}")
#         print(f"  b = {b}")
#         return (p, a, b, True, None, None, None, False,
#                 f"Случайные параметры (p={p}, a={a}, b={b})")
#
#     # Ввести свои параметры
#     elif choice == '3':
#         print("\nВведите параметры кривой:")
#         p = int(input("  p (простое число): "))
#         a = int(input("  a: "))
#         b = int(input("  b: "))
#
#         if p > AUTO_THRESHOLD:
#             print(f"\n⚠️  p = {p} > {AUTO_THRESHOLD}")
#             print("   Для больших p необходимо ввести параметры вручную:")
#             q = int(input("  q (порядок подгруппы, простое число): "))
#             Px = int(input("  Px (x-координата базовой точки): "))
#             Py = int(input("  Py (y-координата базовой точки): "))
#             return (p, a, b, False, q, Px, Py, False,
#                     f"Пользовательские параметры (p={p}, a={a}, b={b})")
#         else:
#             return (p, a, b, True, None, None, None, False,
#                     f"Пользовательские параметры (p={p}, a={a}, b={b})")
#
#     else:
#         return (None, None, None, None, None, None, None, None, None)
#
#
# def print_menu(gost):
#     """Выводит главное меню"""
#     print("\n" + "─" * 60)
#     print(f"ТЕКУЩИЕ ПАРАМЕТРЫ: p={gost.p}, a={gost.a}, b={gost.b}, q={gost.q}")
#     print("─" * 60)
#     print("ДОСТУПНЫЕ ОПЕРАЦИИ:")
#     print("  1. Сгенерировать ключевую пару")
#     print("  2. Подписать файл")
#     print("  3. Проверить подпись файла")
#     print("  4. Показать параметры (с теоремой Хассе)")
#     print("  5. Сменить параметры эллиптической кривой")
#     print("  6. Загрузить ключи из файлов")
#     print("  7. Ввести ключи вручную")
#     print("  0. Выход")
#     print("─" * 60)
#
#
# def show_params(gost):
#     """Показывает параметры кривой"""
#     print("\n" + "=" * 60)
#     print("ПАРАМЕТРЫ ЭЛЛИПТИЧЕСКОЙ КРИВОЙ")
#     print("=" * 60)
#     print(f"  Уравнение: y² = x³ + {gost.a}x + {gost.b} (mod {gost.p})")
#     print(f"  Порядок подгруппы q = {gost.q}")
#     print(f"  Базовая точка P = {gost.P}")
#     print(f"  Длина хэша: {gost.hash_len} бит")
#     print(f"  Длина подписи: {gost.component_bits * 2} бит")
#
#     # Теорема Хассе
#     if hasattr(gost, 'm') and gost.m:
#         hasse = HasseTheorem.verify_curve(gost.p, gost.m)
#         print(f"\n  ТЕОРЕМА ХАССЕ:")
#         print(f"    {hasse['formula']}")
#         print(f"    √{gost.p} ≈ {hasse['sqrt_p']:.4f}")
#         print(f"    2√p ≈ {hasse['2_sqrt_p']:.4f}")
#         print(f"    Диапазон: {hasse['range']}")
#         print(f"    m = {gost.m} → {'✅' if hasse['is_valid'] else '❌'}")
#     print("=" * 60)
#
#
#
# import os
# import random
# from simple_code import GOSTSignature
# from simple_code import Point
#
# # Порог для автоматического вычисления параметров
# # Для p > AUTO_THRESHOLD требуется ручной ввод q, Px, Py
# AUTO_THRESHOLD = 2000
#
#
# def main():
#     print_header()
#
#     # Выбор длины хэша
#     hash_len = select_hash_length()
#     print(f"\n✅ Используется хэш-функция Streebog-{hash_len}")
#
#     # Выбор параметров кривой (возвращает 9 значений)
#     p, a, b, auto_params, q, Px, Py, use_lecture_keys, params_name = select_curve_params()
#
#     if p is None:
#         print("❌ Некорректный выбор, используем учебный пример")
#         p, a, b = 97, 9, 3
#         auto_params = True
#         q = Px = Py = None
#         use_lecture_keys = True
#         params_name = "Учебный пример (p=97, a=9, b=3)"
#
#     # Создание экземпляра подписи с правильными параметрами
#     try:
#         print(f"\n🔧 Инициализация с параметрами: {params_name}")
#
#         if params_name == "Учебный пример (p=97, a=9, b=3)":
#             # Принудительно используем точку P = (89, 1) из лекции
#             gost = GOSTSignature(97, 9, 3, hash_len, auto_params=False, q=47, Px=89, Py=1)
#             use_lecture_keys = True
#         # Передаем правильные параметры в конструктор
#         elif auto_params:
#             gost = GOSTSignature(p, a, b, hash_len, auto_params=True)
#         else:
#             gost = GOSTSignature(p, a, b, hash_len, auto_params=False,
#                                  q=q, Px=Px, Py=Py)
#     except Exception as e:
#         print(f"\n❌ Ошибка инициализации: {e}")
#         print("Используем учебный пример")
#         gost = GOSTSignature(97, 9, 3, hash_len, auto_params=True)
#         use_lecture_keys = True
#
#     current_private = None
#     current_public = None
#
#     # ⭐ ЕСЛИ ВЫБРАН УЧЕБНЫЙ ПРИМЕР - УСТАНАВЛИВАЕМ ЛЕКЦИОННЫЕ КЛЮЧИ d=5 ⭐
#     if use_lecture_keys:
#         print("\n📚 Установка лекционных ключей (d=5)...")
#         d, Q = gost.set_lecture_keys()
#         current_private = d
#         current_public = Q
#
#         with open("private.key", "w") as f:
#             f.write(str(d))
#         with open("public.key", "w") as f:
#             f.write(f"{Q.x}\n{Q.y}")
#         print(f"\n✅ Лекционные ключи сохранены:")
#         print(f"   private.key (d = {d})")
#         print(f"   public.key (Q = {Q})")
#
#     while True:
#         print_menu(gost)
#         choice = input("Выберите операцию: ")
#
#         # 1. ГЕНЕРАЦИЯ КЛЮЧЕЙ
#         if choice == '1':
#             print("\n--- ГЕНЕРАЦИЯ КЛЮЧЕВОЙ ПАРЫ ---")
#             d, Q = gost.generate_key_pair()
#             current_private = d
#             current_public = Q
#
#             with open("private.key", "w") as f:
#                 f.write(str(d))
#             with open("public.key", "w") as f:
#                 f.write(f"{Q.x}\n{Q.y}")
#
#             print(f"\n✅ Ключи сохранены:")
#             print(f"   private.key (d = {d})")
#             print(f"   public.key (Q = {Q})")
#
#         # 2. ПОДПИСАНИЕ ФАЙЛА
#         elif choice == '2':
#             print("\n--- ПОДПИСАНИЕ ФАЙЛА ---")
#             file_path = input("Путь к файлу: ").strip()
#
#             if not os.path.exists(file_path):
#                 print("❌ Файл не найден")
#                 continue
#
#             # Запрос метаданных
#             add_metadata = input("Добавить информацию об авторе и дате? (y/n): ").lower()
#
#             author = None
#             validity_days = 365
#
#             if add_metadata == 'y':
#                 author = input("  Введите имя автора: ").strip()
#                 if not author:
#                     author = "Unknown"
#                 days = input("  Срок действия в днях (Enter = 365): ").strip()
#                 if days:
#                     validity_days = int(days)
#
#             # Выбор ключа
#             if current_private is None:
#                 if not os.path.exists("private.key"):
#                     print("❌ Нет секретного ключа. Сначала операция 1")
#                     continue
#                 with open("private.key", "r") as f:
#                     d = int(f.read().strip())
#                 print(f"Загружен секретный ключ: d = {d}")
#             else:
#                 d = current_private
#
#             with open(file_path, 'rb') as f:
#                 data = f.read()
#
#             print(f"\n📄 Файл: {file_path} ({len(data)} байт)")
#             print(f"🔐 Хэширование по Streebog-{gost.hash_len}...")
#
#             # Переменные для вывода
#             r = None
#             s = None
#             r_bits = None
#             s_bits = None
#             signature_bits = None
#             signed_path = None
#
#             if add_metadata == 'y' and author:
#                 # Подпись с метаданными
#                 r, s, metadata = gost.sign_with_metadata(data, d, author, validity_days, verbose=True)
#
#                 # Сохраняем подписанные данные с метаданными
#                 metadata_bytes = metadata.to_bytes()
#                 separator = b"\n---SIGNED_DATA---\n"
#                 signed_data = metadata_bytes + separator + data
#                 signed_path = file_path + ".signed"
#                 with open(signed_path, 'wb') as f:
#                     f.write(signed_data)
#
#                 print(f"\n✅ Подписанный файл (с метаданными) сохранён: {signed_path}")
#
#                 # Для метаданных получаем двоичные векторы отдельно
#                 r_bits = BinaryVector.to_bits(r, gost.component_bits)
#                 s_bits = BinaryVector.to_bits(s, gost.component_bits)
#                 signature_bits = r_bits + s_bits
#             else:
#                 # Обычная подпись
#                 r, s, r_bits, s_bits, signature_bits = gost.sign(data, d, verbose=True)
#
#             # Сохраняем подпись
#             sig_path = file_path + ".sig"
#             with open(sig_path, 'wb') as f:
#                 f.write(gost.signature_to_bytes(r, s))
#
#             print(f"\n✅ Подпись сохранена: {sig_path}")
#             print(f"   r = {r}")
#             print(f"   s = {s}")
#
#             if r_bits and s_bits and signature_bits:
#                 print(f"   r̄ = {r_bits}")
#                 print(f"   s̄ = {s_bits}")
#                 print(f"   ζ = {signature_bits}")
#         # elif choice == '2':
#         #     print("\n--- ПОДПИСАНИЕ ФАЙЛА ---")
#         #     file_path = input("Путь к файлу: ").strip()
#         #
#         #     if not os.path.exists(file_path):
#         #         print("❌ Файл не найден")
#         #         continue
#         #
#         #     if current_private is None:
#         #         if not os.path.exists("private.key"):
#         #             print("❌ Нет секретного ключа. Сначала операция 1")
#         #             continue
#         #         with open("private.key", "r") as f:
#         #             d = int(f.read().strip())
#         #         print(f"Загружен секретный ключ: d = {d}")
#         #     else:
#         #         d = current_private
#         #
#         #     with open(file_path, 'rb') as f:
#         #         data = f.read()
#         #
#         #     print(f"\n📄 Файл: {file_path} ({len(data)} байт)")
#         #     print(f"🔐 Хэширование по Streebog-{gost.hash_len}...")
#         #
#         #     r, s, r_bits, s_bits, signature_bits = gost.sign(data, d, verbose=True)
#         #
#         #     sig_path = file_path + ".sig"
#         #     with open(sig_path, 'wb') as f:
#         #         f.write(gost.signature_to_bytes(r, s))
#         #
#         #     print(f"\n✅ Подпись сохранена: {sig_path}")
#         #     print(f"   r = {r}")
#         #     print(f"   s = {s}")
#         #     print(f"   r̄ = {r_bits}")
#         #     print(f"   s̄ = {s_bits}")
#             print(f"   ζ = {signature_bits}")
#
#         # 3. ПРОВЕРКА ПОДПИСИ
#         elif choice == '3':
#             print("\n--- ПРОВЕРКА ПОДПИСИ ---")
#             file_path = input("Путь к файлу: ").strip()
#             sig_path = input("Путь к подписи: ").strip()
#
#             if not os.path.exists(file_path):
#                 print("❌ Файл не найден")
#                 continue
#             if not os.path.exists(sig_path):
#                 print("❌ Подпись не найдена")
#                 continue
#
#             if current_public is None:
#                 if not os.path.exists("public.key"):
#                     print("❌ Нет открытого ключа. Сначала операция 1")
#                     continue
#                 with open("public.key", "r") as f:
#                     x = int(f.readline().strip())
#                     y = int(f.readline().strip())
#                 Q = Point(x, y, gost.a, gost.b, gost.p)
#                 print(f"Загружен открытый ключ: Q = {Q}")
#             else:
#                 Q = current_public
#
#             with open(file_path, 'rb') as f:
#                 data = f.read()
#             with open(sig_path, 'rb') as f:
#                 sig_data = f.read()
#
#             r, s = gost.signature_from_bytes(sig_data)
#
#             print(f"\n📄 Файл: {file_path} ({len(data)} байт)")
#             print(f"📝 Подпись: r={r}, s={s}")
#             print(f"🔑 Открытый ключ: Q={Q}")
#
#             result = gost.verify(data, r, s, Q, verbose=True)
#
#             print("\n" + "=" * 40)
#             if result:
#                 print("✅ ПОДПИСЬ ВЕРНА")
#                 print("   Файл аутентичен, авторство подтверждено")
#             else:
#                 print("❌ ПОДПИСЬ НЕВЕРНА")
#                 print("   Файл был изменен или подпись подделана")
#             print("=" * 40)
#
#         # 4. ПОКАЗАТЬ ПАРАМЕТРЫ
#         elif choice == '4':
#             show_params(gost)
#
#         # 5. СМЕНИТЬ ПАРАМЕТРЫ КРИВОЙ
#         elif choice == '5':
#             print("\n" + "=" * 60)
#             print("⚠️  ВНИМАНИЕ: При смене параметров старые ключи станут недействительными!")
#             confirm = input("Продолжить? (y/n): ").lower()
#             if confirm != 'y':
#                 continue
#
#             # Получаем 9 значений
#             p, a, b, auto_params, q, Px, Py, use_lecture_keys, params_name = select_curve_params()
#
#             if p is None:
#                 print("❌ Параметры не изменены")
#                 continue
#
#             try:
#                 print(f"\n🔧 Инициализация с новыми параметрами: {params_name}")
#                 # ⭐ ДЛЯ УЧЕБНОГО ПРИМЕРА - ФИКСИРОВАННЫЕ ПАРАМЕТРЫ ⭐
#                 if params_name == "Учебный пример (p=97, a=9, b=3)":
#                     gost = GOSTSignature(97, 9, 3, hash_len, auto_params=False, q=47, Px=89, Py=1)
#                     use_lecture_keys = True
#
#                 elif auto_params:
#                     gost = GOSTSignature(p, a, b, hash_len, auto_params=True)
#                 else:
#                     gost = GOSTSignature(p, a, b, hash_len, auto_params=False,
#                                          q=q, Px=Px, Py=Py)
#                 current_private = None
#                 current_public = None
#
#                 # Если выбран учебный пример - устанавливаем лекционные ключи
#                 if use_lecture_keys:
#                     print("\n📚 Установка лекционных ключей (d=5)...")
#                     d, Q = gost.set_lecture_keys()
#                     current_private = d
#                     current_public = Q
#
#                     with open("private.key", "w") as f:
#                         f.write(str(d))
#                     with open("public.key", "w") as f:
#                         f.write(f"{Q.x}\n{Q.y}")
#                     print(f"\n✅ Лекционные ключи сохранены:")
#                     print(f"   private.key (d = {d})")
#                     print(f"   public.key (Q = {Q})")
#
#                 print(f"\n✅ Параметры кривой изменены!")
#             except Exception as e:
#                 print(f"\n❌ Ошибка: {e}")
#
#         # 6. ЗАГРУЗИТЬ КЛЮЧИ ИЗ ФАЙЛОВ
#         elif choice == '6':
#             print("\n--- ЗАГРУЗКА КЛЮЧЕЙ ИЗ ФАЙЛОВ ---")
#
#             # Загрузка секретного ключа
#             priv_file = input("Файл с секретным ключом (private.key): ").strip()
#             if not priv_file:
#                 priv_file = "private.key"
#
#             if os.path.exists(priv_file):
#                 with open(priv_file, "r") as f:
#                     current_private = int(f.read().strip())
#                 print(f"✅ Загружен секретный ключ: d = {current_private}")
#             else:
#                 print(f"❌ Файл {priv_file} не найден")
#
#             # Загрузка открытого ключа
#             pub_file = input("Файл с открытым ключом (public.key): ").strip()
#             if not pub_file:
#                 pub_file = "public.key"
#
#             if os.path.exists(pub_file):
#                 with open(pub_file, "r") as f:
#                     x = int(f.readline().strip())
#                     y = int(f.readline().strip())
#                 current_public = Point(x, y, gost.a, gost.b, gost.p)
#                 print(f"✅ Загружен открытый ключ: Q = {current_public}")
#             else:
#                 print(f"❌ Файл {pub_file} не найден")
#
#         # 7. Ввести ключи вручную
#         elif choice == '7':
#             print("\n--- ВВОД КЛЮЧЕЙ ВРУЧНУЮ ---")
#
#             print("\nВведите секретный ключ d:")
#             d_str = input("d (целое число): ").strip()
#             if d_str:
#                 current_private = int(d_str)
#                 print(f"✅ Установлен секретный ключ: d = {current_private}")
#
#             print("\nВведите открытый ключ Q (точка на кривой):")
#             x_str = input("x: ").strip()
#             y_str = input("y: ").strip()
#             if x_str and y_str:
#                 current_public = Point(int(x_str), int(y_str), gost.a, gost.b, gost.p)
#                 print(f"✅ Установлен открытый ключ: Q = {current_public}")
#
#         # 0. ВЫХОД
#         elif choice == '0':
#             print("\nДо свидания!")
#             break
#
#         else:
#             print("\n❌ Неверный выбор!")
#
#
# if __name__ == "__main__":
#     main()