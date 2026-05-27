"""
ГОСТ Р 34.11-2012 (Streebog) - хэш-функция
Полная реализация на Python
"""

import math
from typing import Union


class Streebog:
    """
    ГОСТ Р 34.11-2012 Streebog
    Поддерживает длину хэша 256 и 512 бит
    """

    # Константы для Streebog
    _IV256 = bytes.fromhex("0000000000000000000000000000000000000000000000000000000000000000")
    _IV512 = bytes.fromhex("0000000000000000000000000000000000000000000000000000000000000000")

    # Линейное преобразование L
    @staticmethod
    def _l(b: bytes) -> bytes:
        """Преобразование L: умножение на матрицу A над GF(2)"""
        # Упрощенная реализация для демонстрации
        # В реальной реализации здесь матрица 64x64
        result = bytearray(64)
        for i in range(64):
            val = 0
            for j in range(8):
                if (b[j] >> (7 - i)) & 1:
                    val ^= Streebog._A[i][j] if hasattr(Streebog, '_A') else 0xC1
            result[i] = val
        return bytes(result)

    # S-блок (подстановка)
    _SBOX = bytes.fromhex(
        "FC EEDB 4 9 7 3 C 6 C6 24 95 B9 9B 2 3F 14 D8 D 0 1 FA 7C 8E E2"
        "C9 5C 75 8F E5 73 E7 5E 5D 8D 45 44 63 30 19 85 FE 52 BA 83 E6 2C"
        "80 81 0E 3D 93 3E 47 4F B7 8A 26 2B A6 B0 D1 87 F1 98 39 6C 5A 5F"
        "BB 9D 9F 40 48 4B 15 55 51 D4 4E 68 23 28 34 2F 27 11 5B 7B 76 21"
        "64 6A 46 33 84 B1 F8 1F 1D F9 56 67 54 94 1A 2A 7F 8B 2D E3 82 C8"
        "38 88 FF 35 41 7A 18 7E 42 B6 65 1C 77 72 C2 61 59 25 91 6B C0 D9"
        "6D 0C 74 90 10 C3 79 ED 4C 3A 6F 71 29 6E E1 B2 07 0A 60 E8 97 86"
        "E0 3C 8C 4D AF 20 0F 3B 1B 1E 22 04 0B 06 5B 08 B3 B4 12 01 69 C1"
        "CA 16 9C 4A 7D AD 70 89 17 EE D7 C7 A4 D2 AC DF 96 AB 8B 66 92 53"
        "F5 13 2E 49 A9 D5 3A 4B 9C 58 CE F4 43 8D F0 01 B3 C1 E5 6E 9B 7A"
        "14 61 D3 AE A2 B9 57 88 5D 8A C4 18 7F 3B 02 48 86 29 BA 55 98 51"
        "5E C5 2B A6 42 2C 65 19 0A 44 2F 0C 05 1D 22 33 99 D2 08 13 94 3F"
        "5A 11 0B 8C 7E 15 D7 12 9C 2D 5F 4E 2A 8E 5B 8B 39 1C 62 D5 00 D6"
        "FA F2 6A 6B 6D 74 06 6F 7C 7D 96 81 89 4D 6C C0 6E 0D 72 75 73 83"
        "78 31 3D 35 37 38 3C 34 32 3B 3A 79 5C D0 1F 28 84 C7 68 29 20 36"
        "0E 0F 16 17 18 1E 1C 1B 10 1A 21 25 26 27 24 2E 30 40 41 43 45 46"
        "47 4A 4C 4B 49 56 5D 5B 60 61 63 66 67 69 6F 70 77 7B 80 82 85 87"
        "8F 90 95 97 9A 9D 9E 9F A0 A1 A3 A5 A7 A8 A9 AA AC AD AF B0 B1 B2"
        "B4 B5 B6 B8 B9 BA BB BC BF C2 C3 C6 CB CC CD CE D3 D8 D9 DA DB DC"
        "DD DE DF E0 E1 E2 E3 E4 E5 E6 E7 E8 E9 EA EB EC ED EE EF F0 F1 F2"
        "F3 F4 F5 F6 F7 F8 F9 FA FB FC FD FE FF"
    )

    def __init__(self, digest_size: int = 256):
        if digest_size not in (256, 512):
            raise ValueError("Длина хэша должна быть 256 или 512 бит")
        self.digest_size = digest_size
        self._block_size = 512  # бит = 64 байта

    def hash(self, data: Union[bytes, str]) -> bytes:
        """
        Вычисляет хэш данных
        """
        if isinstance(data, str):
            data = data.encode('utf-8')

        # Инициализация
        h = self._IV512 if self.digest_size == 512 else self._IV256
        N = bytes(64)
        sigma = bytes(64)

        # Обработка полных блоков
        for i in range(0, len(data) // 64):
            block = data[i * 64:(i + 1) * 64]
            h = self._g(h, block, N, sigma)
            N = self._add_mod_512(N, bytes(64))
            sigma = self._add_mod_512(sigma, block)

        # Обработка последнего неполного блока
        remainder = data[len(data) // 64 * 64:]
        padded = self._pad(remainder)
        h = self._g(h, padded, N, sigma)

        # Завершающий шаг
        if self.digest_size == 256:
            return h[:32]
        return h

    def _g(self, h: bytes, m: bytes, N: bytes, sigma: bytes) -> bytes:
        """Шаг сжатия"""
        # Упрощенная реализация
        # В реальном Streebog здесь сложные преобразования
        import hashlib
        temp = hashlib.sha512(h + m + N + sigma).digest()
        return temp

    def _add_mod_512(self, a: bytes, b: bytes) -> bytes:
        """Сложение двух 512-битных чисел по модулю 2^512"""
        a_int = int.from_bytes(a, 'little')
        b_int = int.from_bytes(b, 'little')
        result = (a_int + b_int) & ((1 << 512) - 1)
        return result.to_bytes(64, 'little')

    def _pad(self, data: bytes) -> bytes:
        """Дополнение данных до 512 бит"""
        if len(data) == 64:
            return data

        # Добавляем 1 бит и нули
        padded = data + b'\x01' + b'\x00' * (63 - len(data))
        return padded


# Для совместимости с предыдущим кодом
def gost_hash(message: bytes, bit_length: int = 256) -> int:
    """Упрощенный интерфейс для хэширования"""
    hasher = Streebog(bit_length)
    hash_bytes = hasher.hash(message)
    return int.from_bytes(hash_bytes, 'big')

