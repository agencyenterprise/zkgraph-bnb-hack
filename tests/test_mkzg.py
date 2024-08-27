from zkgraph.commitments.mkzg.mkzg import (
    Open,
    Verify,
    KeyGen,
    Commit,
    curve_order,
    commit_zk_sumcheck_polynomial,
    verify_zk_sumcheck_polynomial,
    prove_zk_sumcheck_polynomial,
)
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


def test_mzkg_zk_sumcheck():
    num_variables = 3
    max_degree = 2
    random_point = [5, 6, 7]
    x0, x1, x2 = symbols("x0 x1 x2")
    domain = FiniteField(curve_order)
    p = domain.characteristic()
    # Generate the public and secret keys
    G1PK, G2PK = KeyGen(
        (2 * num_variables) + 1,
        max_degree,
        p,
        univariate=True,
        generate_zk_sumcheck_pp=True,
    )
    # Public parameters
    PP = [G1PK, G2PK]
    # Example polynomial
    f_poly = Poly(
        1 + 2 * x0 + 3 * x0**2 + 4 * x1 + 5 * x1**2 + 6 * x2 + 7 * x2**2,
        x0,
        x1,
        x2,
        domain=domain,
    )
    # Setup the polynomial
    FK_f = commit_zk_sumcheck_polynomial(f_poly.coeffs(), PP)
    evaluation, openings = prove_zk_sumcheck_polynomial(
        f_poly.coeffs(), random_point, PP
    )
    assert verify_zk_sumcheck_polynomial(FK_f, random_point, evaluation, openings, PP)

    # testing with a smaller polynomial

    f_poly = Poly(
        1 + 2 * x0 + 3 * x0**2 + 4 * x1 + 5 * x1**2,
        x0,
        x1,
        domain=domain,
    )
    random_point = [5, 6]
    FK_f = commit_zk_sumcheck_polynomial(f_poly.coeffs(), PP)
    evaluation, openings = prove_zk_sumcheck_polynomial(
        f_poly.coeffs(), random_point, PP
    )
    assert verify_zk_sumcheck_polynomial(FK_f, random_point, evaluation, openings, PP)
