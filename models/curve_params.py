"""
Параметры эллиптической кривой
DRY: единое место для всех параметров
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class CurveParams:
    """Параметры эллиптической кривой"""
    p: int  # модуль кривой (простое число)
    a: int  # коэффициент a
    b: int  # коэффициент b
    q: int  # порядок подгруппы (простое число)
    Px: int  # x-координата базовой точки
    Py: int  # y-координата базовой точки
    hash_len: int  # длина хэша в битах (256 или 512)
    name: Optional[str] = None  # имя параметров

    @classmethod
    def test_params(cls) -> 'CurveParams':
        """Тестовые параметры из лекции"""
        return cls(
            p=97,
            a=9,
            b=3,
            q=47,
            Px=-8 % 97,
            Py=1,
            hash_len=256,
            name="TestParams"
        )

    @classmethod
    def gost_256_params_a(cls) -> 'CurveParams':
        """Стандартные параметры ГОСТ id-tc26-gost-3410-2012-256-paramSetA"""
        return cls(
            p=int("FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFD97", 16),
            a=int("FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFD94", 16),
            b=int("A6", 16),
            q=int("FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF6C611070995AD10045841B09B761B893", 16),
            Px=int("1", 16),
            Py=int("8D91E471E0989CDA27DF505A453F2B7635294F2DDF23E3B122ACC99C9E9F1E14", 16),
            hash_len=256,
            name="id-tc26-gost-3410-2012-256-paramSetA"
        )

    @classmethod
    def gost_512_params_a(cls) -> 'CurveParams':
        """Стандартные параметры ГОСТ для 512 бит"""
        return cls(
            p=int(
                "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFDC7",
                16),
            a=int(
                "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFDC4",
                16),
            b=int(
                "E8C2505DEDFC86DDC1BD0B2B6667F1DA34B82574761CB0E879BD081CFD0B6265EE3CB090F30D27614CB4574010DA90DD862EF9D4EBEE4761503190785A71C760",
                16),
            q=int(
                "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF27E69532F48D89116FF22B8D4E0560609B4B38ABFAD2B85DCACDB1411F10B275",
                16),
            Px=int("3", 16),
            Py=int(
                "7503CFE87A836AE3A61B8816E25450E14CE5E5C5F2FEDBEC9A846A52B931979B0D284C90B72B0C405A767358D856D4F8F2F19F277EFC7CC4339B694BDEA19AA6",
                16),
            hash_len=512,
            name="id-tc26-gost-3410-2012-512-paramSetA"
        )
