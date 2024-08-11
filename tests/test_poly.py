from zkgraph.polynomials.poly import LinearPoly, QuadraticPoly
from zkgraph.polynomials.field import FiniteField, ModularInteger, PRIME_MODULO

DOMAIN = FiniteField(PRIME_MODULO)


def test_operations():
    a = LinearPoly(DOMAIN, ModularInteger(3), ModularInteger(1))
    b = LinearPoly(DOMAIN, ModularInteger(3), ModularInteger(1))
    c = a + b
    d = c * b
    eval_tests = [ModularInteger(2), ModularInteger(-2)]
    for eval_test in eval_tests:
        assert isinstance(d, QuadraticPoly)
        assert isinstance(c, LinearPoly)
        assert c.eval(eval_test) == a.eval(eval_test) + b.eval(eval_test)
        assert d.eval(eval_test) == c.eval(eval_test) * b.eval(eval_test)
