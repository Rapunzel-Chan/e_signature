# GOST-R-34.10-2012 — Реализация электронной цифровой подписи на эллиптических кривых по ГОСТ Р 34.10-2012

## Описание

**GOST-R-34.10-2012** — это программная реализация электронной цифровой подписи (ЭЦП) на эллиптических кривых в соответствии с российским государственным стандартом:

- **ГОСТ Р 34.10-2012** — процессы формирования и проверки электронной цифровой подписи;
- **ГОСТ Р 34.11-2012** — хэш-функция Streebog.

Проект предназначен для учебных целей и демонстрирует полный цикл работы ЭЦП: генерацию ключей, формирование подписи, проверку подписи, а также работу с файлами и метаданными.

## Возможности

- **Модульная арифметика**:
  - Расширенный алгоритм Евклида для нахождения НОД;
  - Вычисление обратного элемента по модулю;
  - Бинарное возведение в степень по модулю (square-and-multiply);
  - Тест Миллера-Рабина для проверки простоты чисел.

- **Эллиптическая кривая**:
  - Сложение и удвоение точек по формулам (3) и (4) из ГОСТ Р 34.10-2012;
  - Умножение точки на скаляр (double-and-add);
  - Вычисление порядка группы m;
  - Поиск порядка подгруппы q (простой делитель m);
  - Поиск базовой точки P порядка q.

- **Теорема Хассе**:
  - Проверка границ порядка группы: `p+1-2√p ≤ m ≤ p+1+2√p`.

- **Хэш-функция Streebog**:
  - Реализация ГОСТ Р 34.11-2012 через библиотеку `gostcrypto`;
  - Поддержка длины хэша 256 и 512 бит.

- **Формирование и проверка подписи**:
  - Алгоритм I: формирование подписи (раздел 6.1);
  - Алгоритм II: проверка подписи (раздел 6.2);
  - Преобразование подписи в двоичные векторы (r̄, s̄);
  - Конкатенация в итоговую подпись ζ = r̄ || s̄.

- **Метаданные подписи**:
  - Добавление информации об авторе;
  - Фиксация даты и времени создания;
  - Установка срока действия подписи;
  - Защита метаданных электронной подписью.

- **Интерактивная оболочка**:
  - Три режима настройки параметров кривой: учебный пример (лекция 18), случайные параметры, ручной ввод;
  - Выбор длины хэша (256 или 512 бит);
  - Генерация ключевой пары;
  - Подпись файла (с возможностью добавления метаданных);
  - Проверка подписи файла;
  - Загрузка/сохранение ключей из файлов;
  - Ручной ввод ключей;
  - Просмотр параметров кривой с теоремой Хассе;
  - Смена параметров кривой в процессе работы.

- **Автоматическое тестирование**:
  - 43 теста на основе unittest;
  - Контрольные примеры из ГОСТ Р 34.10-2012 (Приложение А, Пример 1 с 256-битной кривой);
  - Проверка всех ключевых компонентов.

## Структура проекта

GOST-R-34.10-2012/
├── simple_code.py # Основная реализация
├── main.py # Интерактивная оболочка
├── test_simple_code.py # Автоматические тесты (43 теста)
├── pyproject.toml # Конфигурация Poetry
└── README.md # Документация

## Установка

### 1. Клонирование репозитория

```
git clone -b develop https://github.com/Rapunzel-Chan/e_signature.git
cd EP_GOST
```
### 2. Создание и активация виртуального окружения
Windows:

```
python -m venv venv
.\venv\Scripts\activate
```

Linux/macOS:

```
python3 -m venv venv
source venv/bin/activate
```

### 3. Установка зависимостей
```
pip install -r requirements.txt
```
Или 
```
poetry install
```

## Использование
Запустите интерактивную оболочку:

```
python main.py
```

Программа предложит:

- Выбрать длину хэша (256 или 512 бит);

- Выбрать режим настройки параметров кривой:

-- Учебный пример (p=97, a=9, b=3, q=47, P=(89,1), d=5);

-- Случайные параметры (маленькие числа для тестирования);

-- Ручной ввод (для больших ГОСТ-совместимых параметров).

- Работать с ключами: генерация, загрузка, ручной ввод;

- Подписывать файлы (с возможностью добавления метаданных);

- Проверять подпись файлов.

### 3. Автоматическое тестирование
Запуск всех тестов:

``` 
python test_simple_code.py 
``` 
Или с использованием unittest:

``` 
python -m unittest test_simple_code.py
``` 

## Требования
- Python: 3.10 или выше

## Зависимости
- gostcrypto — реализация хэш-функции Streebog (ГОСТ Р 34.11-2012)

## Результаты тестирования
----------------------------------------------------------------------
test_egcd (__main__.TestModularArithmetic.test_egcd)
Тест расширенного алгоритма Евклида ... ok
test_is_prime (__main__.TestModularArithmetic.test_is_prime)
Тест простоты чисел ... ok
test_mod_pow (__main__.TestModularArithmetic.test_mod_pow)
Тест быстрого возведения в степень ... ok
test_modinv (__main__.TestModularArithmetic.test_modinv)
Тест обратного элемента по модулю ... ok
test_bounds (__main__.TestHasseTheorem.test_bounds)
Тест вычисления границ ... ok
test_check (__main__.TestHasseTheorem.test_check)
Тест проверки порядка ... ok
test_verify_curve (__main__.TestHasseTheorem.test_verify_curve)
Тест проверки кривой ... ok
test_concat (__main__.TestBinaryVector.test_concat)
Конкатенация двоичных векторов ... ok
test_to_bits (__main__.TestBinaryVector.test_to_bits)
Преобразование целого числа → двоичный вектор ... ok
test_to_int (__main__.TestBinaryVector.test_to_int)
Преобразование двоичного вектора → целое число ... ok
test_on_curve (__main__.TestPoint.test_on_curve)
Проверка, что точка лежит на кривой ... ok
test_point_addition (__main__.TestPoint.test_point_addition)
Тест сложения точек ... ok
test_point_multiplication (__main__.TestPoint.test_point_multiplication)
Тест умножения точки на скаляр ... ok
test_point_negation (__main__.TestPoint.test_point_negation)
Тест отрицания точки ... ok
test_discriminant (__main__.TestEllipticCurve.test_discriminant)
Проверка дискриминанта (должен быть ≠ 0) ... ok
test_find_all_points (__main__.TestEllipticCurve.test_find_all_points)
Поиск всех точек на кривой ... ok
test_find_base_point (__main__.TestEllipticCurve.test_find_base_point)
Поиск базовой точки порядка q ... ok
test_find_subgroup_order (__main__.TestEllipticCurve.test_find_subgroup_order)
Поиск порядка подгруппы ... ok
test_get_order (__main__.TestEllipticCurve.test_get_order)
Вычисление порядка группы ... ok
test_hash_consistency (__main__.TestStreebog.test_hash_consistency)
Проверка детерминированности хэш-функции ... ok
test_hash_length (__main__.TestStreebog.test_hash_length)
Проверка длины хэша ... ok
test_hash_to_int (__main__.TestStreebog.test_hash_to_int)
Преобразование хэша в целое число ... ok
test_generate_key_pair (__main__.TestGOSTSignature.test_generate_key_pair)
Тест генерации ключевой пары (БЕЗ seed) ... ok
test_sign_and_verify (__main__.TestGOSTSignature.test_sign_and_verify)
Полный цикл: подпись → проверка ... ok
test_signature_serialization (__main__.TestGOSTSignature.test_signature_serialization)
Тест сериализации подписи в байты и обратно ... ok
test_verify_wrong_key (__main__.TestGOSTSignature.test_verify_wrong_key)
Проверка подписи с чужим открытым ключом ... ok
test_verify_wrong_message (__main__.TestGOSTSignature.test_verify_wrong_message)
Проверка подписи с изменённым сообщением ... ok
test_lecture_example_sign (__main__.TestLectureExample.test_lecture_example_sign)
Тест примера из лекции: d=5, k=18, e=42 → r=12, s=17 ... ok
test_lecture_key_generation (__main__.TestLectureExample.test_lecture_key_generation)
Тест: 5·P = (50, 56) из лекции ... ok
test_curve_with_auto_params (__main__.TestDifferentCurves.test_curve_with_auto_params)
Тест кривой с автоматическим вычислением параметров ... ok
test_full_cycle_with_file (__main__.TestIntegration.test_full_cycle_with_file)
Полный цикл: создание файла → подпись → проверка ... ok
test_modified_file_fails (__main__.TestIntegration.test_modified_file_fails)
Изменённый файл не проходит проверку ... ok
test_empty_message (__main__.TestEdgeCases.test_empty_message)
Пустое сообщение ... ok
test_invalid_signature_range (__main__.TestEdgeCases.test_invalid_signature_range)
Подпись с r или s вне диапазона ... ok
test_large_message (__main__.TestEdgeCases.test_large_message)
Большое сообщение (1KB) ... ok
test_hasse_for_curve_a0 (__main__.TestHasseForCurves.test_hasse_for_curve_a0)
Кривая a=0: p=101, b=2 ... ok
test_hasse_for_curve_b1 (__main__.TestHasseForCurves.test_hasse_for_curve_b1)
Кривая b=1: p=103, a=1, b=1 ... ok
test_example1_curve_parameters (__main__.TestGostAppendixA.test_example1_curve_parameters)
Тест 1.1: Проверка параметров кривой из примера 1 ... ok
test_example1_keys (__main__.TestGostAppendixA.test_example1_keys)
Тест 1.2: Проверка ключей из примера 1 ... ok      
test_example1_signature (__main__.TestGostAppendixA.test_example1_signature)
Тест 1.3: Проверка формирования подписи из примера 1 ... ok
test_example1_verification (__main__.TestGostAppendixA.test_example1_verification)
Тест 1.4: Проверка проверки подписи из примера 1 ... ok    

----------------------------------------------------------------------
Ran 43 tests in 0.681s

OK
----------------------------------------------------------------------

## Лицензия

Проект разработан в учебных целях. Код может использоваться для изучения криптографических алгоритмов и стандартов.

## Создатель

В случае возникновения вопросов, нахождения багов или предложений по улучшению кода, можно обратиться к разработчику
по e-mail: rapuncel.chan24@gmail.com.
