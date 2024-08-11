from typing import Union

PRIME_MODULO = 2**255 - 19
PRECISION_BITS = 64
SCALE = 2**PRECISION_BITS
NEGATIVE_POINT = PRIME_MODULO // 2


def quantization(x, precision_bits=PRECISION_BITS, modulus=PRIME_MODULO):
    """
    Quantize a real number x with handling for negative values.

    Args:
    x (float): The real number to quantize.
    precision_bits (int): The number of bits of precision.
    modulus (int): The modulus of the finite field.

    Returns:
    int: The quantized value.
    """

    sign = 1 if x >= 0 else -1
    x = abs(x)
    quantization_scale = 2**precision_bits
    x_quantized = int(round(x * quantization_scale, 0))

    if sign < 0:
        x_quantized = (modulus - x_quantized) % modulus

    return x_quantized


def dequantization(
    x_quantized,
    precision_bits=PRECISION_BITS,
    modulus=PRIME_MODULO,
    negative_point=NEGATIVE_POINT,
):
    """
    Dequantize a value from a finite field back to a floating-point number, considering negative values.

    Args:
    x_quantized (FiniteField element): The quantized value in the finite field.
    precision_bits (int): The number of bits of precision.
    modulus (int): The modulus of the finite field.
    negative_point (int): The point above which values are considered negative.

    Returns:
    float: The dequantized floating-point number.
    """
    quantization_scale = 2**precision_bits
    x_int = int(x_quantized)  # Convert to integer for calculations

    # Handle negative values represented in two's complement
    if x_int > negative_point:
        x_int = x_int - modulus

    x_dequantized = x_int / quantization_scale
    return round(x_dequantized, 2)


def qmul(a, b, modulus=PRIME_MODULO, precision_bits=PRECISION_BITS):
    """
    Multiply two quantized numbers within a finite field and adjust by dividing
    by the quantization scale to handle the increased scale from multiplication.

    Args:
    a (FiniteField element): The first quantized value.
    b (FiniteField element): The second quantized value.
    modulus (int): The modulus of the finite field.
    precision_bits (int): The number of bits of precision.

    Returns:
    FiniteField: The result of the multiplication, correctly scaled.
    """
    quantization_scale = 2**precision_bits
    # Calculate the product in the finite field
    if hasattr(a, "val"):
        a = a.val
    elif not isinstance(a, int) and not isinstance(a, float):
        raise ValueError("a must be an integer or float")
    if hasattr(b, "val"):
        b = b.val
    elif not isinstance(b, int) and not isinstance(b, float):
        raise ValueError("b must be an integer or float")
    adq, bdq = dequantization(a), dequantization(b)
    ap = a
    if adq < 0:
        ap = quantization(-adq)
    bp = b
    if bdq < 0:
        bp = quantization(-bdq)
    product = ap * bp
    sign_neg = (adq < 0) ^ (
        bdq < 0
    )  # XOR to determine if the result should be negative
    if product > modulus:
        product = product % modulus
    # Adjust the scale by dividing by the quantization scale
    # inverse_scale =
    scaled_result = (product / quantization_scale) % modulus
    if sign_neg:
        scaled_result = quantization(-dequantization(scaled_result))
    return int(scaled_result) % modulus


def qadd(a, b, modulus=PRIME_MODULO, precision_bits=PRECISION_BITS):
    """
    Add two quantized numbers within a finite field.

    Args:
    a (FiniteField element): The first quantized number.
    b (FiniteField element): The second quantized number.
    modulus (int): The modulus of the finite field.

    Returns:
    FiniteField: The result of the addition.
    """
    # Addition within the finite field
    if hasattr(a, "val"):
        a = a.val
    if hasattr(b, "val"):
        b = b.val
    return int(a + b) % modulus


def qexp(base, exponent, modulus=PRIME_MODULO, precision_bits=PRECISION_BITS):
    """
    Exponentiate a base to a power using defined finite field multiplication (qmul).

    Args:
    base (int or FiniteField element): The base of the exponentiation.
    exponent (int): The exponent to which the base is raised.
    modulus (int): The modulus of the finite field.
    precision_bits (int): The number of precision bits used in qmul for scaling.

    Returns:
    FiniteField element: The result of the exponentiation.
    """
    result = quantization(
        1, precision_bits, modulus
    )  # Identity element of multiplication in the field

    while exponent > 0:
        if exponent % 2 == 1:
            result = qmul(
                result, base, modulus, precision_bits
            )  # Multiply result by base if the current exp bit is 1
        base = qmul(base, base, modulus, precision_bits)  # Square the base
        exponent //= 2  # Right shift the exponent

    return int(result)


def qdiv(a, b):
    """
    Perform fixed-point division on scaled integers, correctly handling negative numbers.

    Args:
    a (int): The quantized numerator, already scaled by 2^precision_bits.
    b (int): The quantized denominator, already scaled by 2^precision_bits.
    precision_bits (int): The number of fractional bits in the fixed-point representation.

    Returns:
    int: The result of the division, scaled by 2^precision_bits.
    """
    if hasattr(a, "val"):
        a = a.val
    elif not isinstance(a, int) and not isinstance(a, float):
        raise ValueError("a must be an integer or float")
    if hasattr(b, "val"):
        b = b.val
    elif not isinstance(b, int) and not isinstance(b, float):
        raise ValueError("b must be an integer or float")
    if b == 0:
        raise ValueError("Division by zero is not allowed.")

    b = dequantization(b) * SCALE
    a = dequantization(a) * SCALE
    # Determine the sign of the result
    sign_neg = (a < 0) ^ (b < 0)  # XOR to determine if the result should be negative

    # Use absolute values for division to ensure correctness
    abs_a = abs(a)
    abs_b = abs(b)

    # Adjust 'a' by the scaling factor to maintain precision after division
    scaled_a = abs_a * SCALE

    # Perform the division using absolute values
    abs_result = scaled_a // abs_b
    if not sign_neg:
        return abs_result % PRIME_MODULO
    else:
        return quantization(-dequantization(abs_result)) % PRIME_MODULO


def qcompare(a, b, modulus=PRIME_MODULO):
    """Helper function to adjust numbers based on their value relative to modulus/2."""
    if a >= NEGATIVE_POINT:
        a -= modulus
    if b >= NEGATIVE_POINT:
        b -= modulus
    return a, b


def qlt(a, b):
    """Less than comparison for quantized numbers."""
    a, b = dequantization(a), dequantization(b)
    return a < b


def qgt(a, b):
    """Greater than comparison for quantized numbers."""
    a, b = dequantization(a), dequantization(b)
    return a > b


def qle(a, b):
    """Less than or equal comparison for quantized numbers."""
    a, b = dequantization(a), dequantization(b)
    return a <= b


def qge(a, b):
    """Greater than or equal comparison for quantized numbers."""
    a, b = dequantization(a), dequantization(b)
    return a >= b


def qne(a, b):
    """Not equal comparison for quantized numbers."""
    return a.val != b.val


class ModularInteger:
    def __init__(self, val: float, scale=True):
        if scale:
            self.val = quantization(val)
        else:
            self.val = val

    def __int__(self):
        return int(self.val)

    def __lt__(self, other: "ModularInteger"):
        if isinstance(other, ModularInteger):
            other = ModularInteger(other.val, False)
        if isinstance(other, float):
            other = ModularInteger(other, True)
        if isinstance(other, int):
            other = ModularInteger(other, True)
        return qlt(self.val, other.val)

    def __gt__(self, other: "ModularInteger"):
        if isinstance(other, ModularInteger):
            other = ModularInteger(other.val, False)
        if isinstance(other, float):
            other = ModularInteger(other, True)
        if isinstance(other, int):
            other = ModularInteger(other, True)
        return qgt(self.val, other.val)

    def __le__(self, other: "ModularInteger"):
        if isinstance(other, ModularInteger):
            other = ModularInteger(other.val, False)
        if isinstance(other, float):
            other = ModularInteger(other, True)
        if isinstance(other, int):
            other = ModularInteger(other, True)
        return qle(self.val, other.val)

    def __ge__(self, other: "ModularInteger"):
        if isinstance(other, ModularInteger):
            other = ModularInteger(other.val, False)
        if isinstance(other, float):
            other = ModularInteger(other, True)
        if isinstance(other, int):
            other = ModularInteger(other, True)
        return qge(self.val, other.val)

    def __ne__(self, other: "ModularInteger"):
        if isinstance(other, ModularInteger):
            other = ModularInteger(other.val, False)
        if isinstance(other, float):
            other = ModularInteger(other, True)
        if isinstance(other, int):
            other = ModularInteger(other, True)
        return qne(self, other)

    def __add__(self, other: "ModularInteger"):
        if isinstance(other, ModularInteger):
            other = ModularInteger(other.val, False)
        if isinstance(other, float):
            other = ModularInteger(other, True)
        if isinstance(other, int):
            other = ModularInteger(other, True)
        return ModularInteger(qadd(self, other), False)

    def __sub__(self, other: "ModularInteger"):
        if isinstance(other, ModularInteger):
            other = ModularInteger(other.val, False)
        if isinstance(other, float):
            other = ModularInteger(other, True)
        if isinstance(other, int):
            other = ModularInteger(other, True)
        return ModularInteger(qadd(self, -other), False)

    def __neg__(self):
        return ModularInteger(quantization(-dequantization(self.val)), False)

    def __eq__(self, other: "ModularInteger"):
        if isinstance(other, ModularInteger):
            other = ModularInteger(other.val, False)
        if isinstance(other, float):
            other = ModularInteger(other, True)
        if isinstance(other, int):
            other = ModularInteger(other, True)
        return self.val == other.val

    def __mul__(self, other: "ModularInteger"):
        if isinstance(other, ModularInteger):
            other = ModularInteger(other.val, False)
        if isinstance(other, float):
            other = ModularInteger(other, True)
        if isinstance(other, int):
            other = ModularInteger(other, True)
        return ModularInteger(qmul(self, other), False)

    def __truediv__(self, other: "ModularInteger"):
        if isinstance(other, ModularInteger):
            other = ModularInteger(other.val, False)
        if isinstance(other, float):
            other = ModularInteger(other, True)
        if isinstance(other, int):
            other = ModularInteger(other, True)
        return ModularInteger(qdiv(self, other), False)

    def __pow__(self, exponent: Union[int, float]):
        if not isinstance(exponent, int):
            raise ValueError("Exponent must be an integer")
        return ModularInteger(qexp(self, exponent % PRIME_MODULO), False)

    def inverse(self):
        one = ModularInteger(1)
        return one / self

    def __repr__(self) -> str:
        return f"({self.val}, {dequantization(self.val)})"

    def __str__(self) -> str:
        return f"({self.val}, {dequantization(self.val)})"


class FiniteField:
    zero = ModularInteger(0, True)
    one = ModularInteger(1, True)

    def characteristic(self):
        return PRIME_MODULO

    def __init__(self, mod: int):
        self.mod = mod

    def __call__(self, val: float, scale=False):
        return ModularInteger(val, scale)
