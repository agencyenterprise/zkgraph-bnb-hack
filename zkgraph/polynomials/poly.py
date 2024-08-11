from zkgraph.polynomials.field import ModularInteger, FiniteField
from typing import Union


class LinearPoly:
    def __init__(self, domain: FiniteField, a=0, b=0):
        self.domain = domain

        if not isinstance(a, ModularInteger):
            a = self.domain(a)
        if not isinstance(b, ModularInteger):
            b = self.domain(b)
        self.a = a
        self.b = b

    def __add__(self, other):
        if isinstance(other, ModularInteger):
            other = LinearPoly(self.domain, b=other)
        if isinstance(other, int):
            other = LinearPoly(self.domain, b=other)
        if isinstance(other, LinearPoly):
            return LinearPoly(self.domain, self.a + other.a, self.b + other.b)
        raise ValueError("Cannot add LinearPoly with non-LinearPoly")

    def __mul__(self, other):
        if isinstance(other, int) or isinstance(other, ModularInteger):
            other = LinearPoly(self.domain, b=other)
        if isinstance(other, LinearPoly):
            return QuadraticPoly(
                self.domain,
                self.a * other.a,
                self.a * other.b + self.b * other.a,
                self.b * other.b,
            )
        elif isinstance(other, ModularInteger):
            return LinearPoly(self.a * other, self.b * other)
        raise ValueError("Cannot multiply LinearPoly with non-LinearPoly")

    def __str__(self):
        return f"{self.a}x + {self.b}"

    def eval(self, value: Union[int, ModularInteger]):
        if not isinstance(value, ModularInteger):
            value = self.domain(value)
        return self.a * value + self.b

    def coefficients(self):
        return [self.a, self.b]


class QuadraticPoly:
    def __init__(self, domain: FiniteField, a=0, b=0, c=0):
        self.domain = domain
        if not isinstance(a, ModularInteger):
            a = self.domain(a)
        if not isinstance(b, ModularInteger):
            b = self.domain(b)
        if not isinstance(c, ModularInteger):
            c = self.domain(c)
        self.a = a
        self.b = b
        self.c = c

    def __add__(self, other):
        return QuadraticPoly(
            self.domain, self.a + other.a, self.b + other.b, self.c + other.c
        )

    def __mul__(self, other):
        if isinstance(other, ModularInteger):
            return QuadraticPoly(
                self.domain, self.a * other, self.b * other, self.c * other
            )

    def __str__(self):
        return f"{self.a}x^2 + {self.b}x + {self.c}"

    def eval(self, value: Union[int, ModularInteger]):
        if not isinstance(value, ModularInteger):
            value = self.domain(value)
        return self.a * value**2 + self.b * value + self.c

    def coefficients(self):
        return [self.a, self.b, self.c]


class CubicPoly:
    def __init__(self, domain: FiniteField, a=0, b=0, c=0, d=0):
        self.domain = domain
        if not isinstance(a, ModularInteger):
            a = self.domain(a)
        if not isinstance(b, ModularInteger):
            b = self.domain(b)
        if not isinstance(c, ModularInteger):
            c = self.domain(c)
        if not isinstance(d, ModularInteger):
            d = self.domain(d)
        self.a = a
        self.b = b
        self.c = c
        self.d = d

    def __add__(self, other):
        return CubicPoly(
            self.domain,
            self.a + other.a,
            self.b + other.b,
            self.c + other.c,
            self.d + other.d,
        )

    def __str__(self):
        return f"{self.a}x^3 + {self.b}x^2 + {self.c}x + {self.d}"

    def eval(self, value: Union[int, ModularInteger]):
        if not isinstance(value, ModularInteger):
            value = self.domain(value)
        return self.a * value**3 + self.b * value**2 + self.c * value + self.d

    def coefficients(self):
        return [self.a, self.b, self.c, self.d]


class QuadruplePoly:
    def __init__(self, domain: FiniteField, a=0, b=0, c=0, d=0, e=0):
        self.domain = domain
        if not isinstance(a, ModularInteger):
            a = self.domain(a)
        if not isinstance(b, ModularInteger):
            b = self.domain(b)
        if not isinstance(c, ModularInteger):
            c = self.domain(c)
        if not isinstance(d, ModularInteger):
            d = self.domain(d)
        if not isinstance(e, ModularInteger):
            e = self.domain(e)

        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self.e = e

    def __add__(self, other):
        if not isinstance(other, QuadruplePoly):
            raise ValueError("Cannot add QuadruplePoly with non-QuadruplePoly")
        return QuadruplePoly(
            self.domain,
            self.a + other.a,
            self.b + other.b,
            self.c + other.c,
            self.d + other.d,
            self.e + other.e,
        )

    def __str__(self):
        return f"{self.a}x^4 + {self.b}x^3 + {self.c}x^2 + {self.d}x + {self.e}"

    def eval(self, value: Union[int, ModularInteger]):
        if not isinstance(value, ModularInteger):
            value = self.domain(value)
        return (
            (((self.a * value) + self.b) * value + self.c) * value + self.d
        ) * value + self.e

    def coefficients(self):
        return [self.a, self.b, self.c, self.d, self.e]


class QuintuplePoly:
    def __init__(self, domain: FiniteField, a=0, b=0, c=0, d=0, e=0, f=0):
        self.domain = domain
        if not isinstance(a, ModularInteger):
            a = self.domain(a)
        if not isinstance(b, ModularInteger):
            b = self.domain(b)
        if not isinstance(c, ModularInteger):
            c = self.domain(c)
        if not isinstance(d, ModularInteger):
            d = self.domain(d)
        if not isinstance(e, ModularInteger):
            e = self.domain(e)
        if not isinstance(f, ModularInteger):
            f = self.domain(f)
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self.e = e
        self.f = f

    def __add__(self, other):
        if not isinstance(other, QuintuplePoly):
            raise ValueError("Cannot add QuintuplePoly with non-QuintuplePoly")
        return QuintuplePoly(
            self.domain,
            self.a + other.a,
            self.b + other.b,
            self.c + other.c,
            self.d + other.d,
            self.e + other.e,
            self.f + other.f,
        )

    def __str__(self):
        return f"{self.a}x^5 + {self.b}x^4 + {self.c}x^3 + {self.d}x^2 + {self.e}x + {self.f}"

    def eval(self, value: Union[int, ModularInteger]):
        if not isinstance(value, ModularInteger):
            value = self.domain(value)
        return (
            ((((self.a * value) + self.b) * value + self.c) * value + self.d) * value
            + self.e
        ) * value + self.f

    def coefficients(self):
        return [self.a, self.b, self.c, self.d, self.e, self.f]
