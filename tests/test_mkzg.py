from zkgraph.commitments.mkzg.mkzg import Open, Verify, KeyGen, Commit, curve_order
from sympy import Poly, symbols, FiniteField


def test_mzkg():
    num_variables = 3
    max_degree = 3
    random_point = [5, 6, 7]
    x0, x1, x2 = symbols("x0 x1 x2")
    variables = [x0, x1, x2]
    domain = FiniteField(curve_order)
    p = domain.characteristic()
    # Generate the public and secret keys
    G1PK, G2PK = KeyGen(num_variables, max_degree, p)
    # Public parameters
    PP = [G1PK, G2PK]
    # Example polynomial
    f_poly = Poly(x0**3 + 3 * x1**2 - x2, x0, x1, x2, domain=domain)
    # Setup the polynomial
    FK_f = Commit(G2PK, f_poly, p)
    # Compute (v, w) signature
    evaluation, openings = Open(G1PK, f_poly, variables, random_point, domain)

    assert Verify(PP, FK_f, evaluation, openings, random_point, p)


def test_mzkg_multilinear_univariate():
    num_variables = 3
    max_degree = 3
    random_point = [5, 6, 7]
    x0, x1, x2 = symbols("x0 x1 x2")
    variables = [x0, x1, x2]
    domain = FiniteField(curve_order)
    p = domain.characteristic()
    # Generate the public and secret keys
    G1PK, G2PK = KeyGen(num_variables, max_degree, p, univariate=True)
    # Public parameters
    PP = [G1PK, G2PK]
    # Example polynomial
    f_poly = Poly(x0 + x2 + x1, x0, x1, x2, domain=domain)
    # Setup the polynomial
    FK_f = Commit(G2PK, f_poly, p)
    # Compute (v, w) signature
    evaluation, openings = Open(G1PK, f_poly, variables, random_point, domain)

    assert Verify(PP, FK_f, evaluation, openings, random_point, p)
