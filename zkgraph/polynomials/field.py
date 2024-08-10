from typing import Union

USE_SYMPY = False
SMALL_PRIME = (2**32) - 1
curve_order = 2**255 - 19

from sympy.polys.domains.modularinteger import ModularInteger as FModularInteger

PRIME_MODULO = curve_order  # 2**255 - 19
PRECISION_BITS = 16
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
    return x_dequantized


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
