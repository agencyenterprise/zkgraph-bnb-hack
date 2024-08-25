# Code implemented from scratch based on the paper https://eprint.iacr.org/2011/587.pdf
# Implemented during the BnB Q3 Hackathon 2024

from random import randint
from itertools import product
from typing import Union
from sympy.core.backend import Symbol
from sympy import Poly, reduced, FiniteField
from zkgraph.commitments.mkzg.ecc import (
    G1,
    G2,
    ecc_multiply,
    ecc_add,
    ecc_negate,
    pairing,
    curve_order,
    TG1P,
    TG2P,
    TPP,
)
import dill
from concurrent.futures import ProcessPoolExecutor
from collections.abc import MutableMapping


class PPStore(MutableMapping):
    def __init__(self, *args, **kwargs):
        self.store = dict()
        self.update(dict(*args, **kwargs))

    def __getitem__(self, key):
        variables_0 = list(self.store.keys())[0]
        if not isinstance(variables_0, tuple):
            raise ValueError("Key must be a tuple")
        if not isinstance(key, tuple):
            raise ValueError("Key must be a tuple")
        len_key = len(key)
        if len_key <= len(variables_0):
            size_diff = len(variables_0) - len_key
            key = (0,) * (size_diff) + key
        else:
            raise ValueError(
                "Ptau key can hold up to {} values".format(len(variables_0))
            )
        return self.store[self._keytransform(key)]

    def __setitem__(self, key, value):
        self.store[self._keytransform(key)] = value

    def __delitem__(self, key):
        del self.store[self._keytransform(key)]

    def __iter__(self):
        return iter(self.store)

    def __len__(self):
        return len(self.store)

    def _keytransform(self, key):
        return key


def save_pp(PP: TPP, filename: str = "power_of_tau.ptau") -> None:
    """Save the public parameters to a file

    Args:
        PP (TPP): The public parameters
        filename (str, optional): The filename to save the file. Defaults to
        "power_of_tau.ptau".
    """
    dill.dump(dill.dumps(PP), open(filename, "wb"))


def load_pp(filename: str = "power_of_tau.ptau") -> TPP:
    """Load the public parameters from a file

    Args:
        filename (str, optional): Proof of tau filename. Defaults to
        "power_of_tau.ptau".

    Returns:
        TPP: The public parameters
    """

    return dill.loads(dill.load(open(filename, "rb")))


def to_group_point(group: Union[TG1P, TG2P], value: int) -> Union[TG1P, TG2P]:
    """Convert the value to a group point in the provided group

    Args:
        group (Union[TG1P, TG2P]): The group to convert the value to
        value (int): The value to convert

    Returns:
        Union[TG1P, TG2P]: The group point
    """
    return ecc_multiply(group, value)


def power_of_tau_step(
    generator: TG1P, exponent_list: list[tuple[int]], t: list, modulo: int = curve_order
) -> dict[tuple[int], TG1P]:
    Wn_d = {}
    for exponents in exponent_list:
        exp_value = 1
        for i, exp in enumerate(exponents):
            exp_value *= (t[i] ** exp) % modulo

        # Exponentiate g by the computed value modulo p
        g_exp = ecc_multiply(generator, exp_value % modulo)  # Correct function call

        Wn_d[exponents] = g_exp  # Store the computed group element
    return Wn_d


def compute_univariate_exponent_list(
    max_degree: int, num_variables: int
) -> list[tuple[int]]:
    """Compute the exponent list for the multivariate with only univariate monomials case

    Args:
        max_degree (int): The maximum degree of the polynomial
        num_variables (int): The number of variables in the polynomial

    Returns:
        list[tuple[int]]: The exponent list
    """
    idxs = []
    for i in range(num_variables):
        for d in range(max_degree + 1):
            before = [0] * i
            after = [0] * (num_variables - i - 1)
            idxs.append(tuple(after + [d] + before))
    return idxs


def divide_list_into_chunks(lst: list, chunk_size: int) -> list[list]:
    """Divide a list into chunks of the specified size

    Args:
        lst (list): The list to divide
        chunk_size (int): The size of each chunk

    Returns:
        list[list]: The divided list
    """
    return [lst[i : i + chunk_size] for i in range(0, len(lst), chunk_size)]


def SequencialKeyGen(
    num_variables: int,
    max_degree: int,
    modulo: int = curve_order,
    univariate: int = False,
) -> TPP:
    """Generate the public parameters (powers of tau) for the multilinear map

    Args:
        num_variables (int): Max number of variables in the polynomial
        max_degree (int): Maximum degree of the polynomial
        modulo (int, optional): Prime modulus. Defaults to curve_order.

    Returns:
        TPP: The public parameters
    """
    # Base point of G1 from BLS G1 primitives
    t = [randint(1, modulo - 1) for _ in range(num_variables)]
    # exponent list size: (max_degree + 1)^num_variables
    if univariate:
        exponents_list = compute_univariate_exponent_list(max_degree, num_variables)
    else:
        exponents_list = list(product(range(max_degree + 1), repeat=num_variables))
    Wn_d_g1 = power_of_tau_step(G1, exponents_list, t, modulo)
    G1PK = (G1, PPStore(Wn_d_g1))
    Wn_d_g2 = power_of_tau_step(G2, exponents_list, t, modulo)
    G2PK = (G2, PPStore(Wn_d_g2))
    return G1PK, G2PK


def DistributedKeyGen(
    num_variables: int,
    max_degree: int,
    modulo: int = curve_order,
    chunk_len: int = 16384,
) -> TPP:
    """Generate the public parameters (powers of tau) for the multilinear map using distributed computing

    Args:
        num_variables (int): Max number of variables in the polynomial
        max_degree (int): Maximum degree of the polynomial
        modulo (int, optional): Prime modulus. Defaults to curve_order.
        chunk_len (int, optional): The size of the chunk to divide the exponent list. Defaults to 16384 (2**14)

    Returns:
        TPP: The public parameters
    """
    t = [randint(1, modulo - 1) for _ in range(num_variables)]
    exponents_list = list(product(range(max_degree + 1), repeat=num_variables))
    chunk_size = len(exponents_list) // chunk_len
    exponents_list_chunk = divide_list_into_chunks(
        exponents_list, chunk_size=chunk_size
    )
    Wn_d_g1 = {}
    Wn_d_g2 = {}
    with ProcessPoolExecutor() as executor:
        g1_promises = [
            executor.submit(power_of_tau_step, G1, exponents_chunk, t, modulo)
            for exponents_chunk in exponents_list_chunk
        ]
        g2_promises = [
            executor.submit(power_of_tau_step, G2, exponents_chunk, t, modulo)
            for exponents_chunk in exponents_list_chunk
        ]
    for idx in range(len(g1_promises)):
        g1_chunk = g1_promises[idx].result()
        g2_chunk = g2_promises[idx].result()
        Wn_d_g1 = {**Wn_d_g1, **g1_chunk}
        Wn_d_g2 = {**Wn_d_g2, **g2_chunk}


def KeyGen(
    num_variables: int, max_degree: int, modulo: int = curve_order, univariate=False
) -> TPP:
    """Generate the public parameters (powers of tau) for the multilinear map

    Args:
        num_variables (int): Max number of variables in the polynomial
        max_degree (int): Maximum degree of the polynomial
        modulo (int, optional): Prime modulus. Defaults to curve_order.

    Returns:
        TPP: The public parameters
    """
    # @TODO: YOU MUST IMPLEMENT THE KNOWLEDGE OF COEFFICIENTS POWERS OF TAU
    # BEFORE GOING TO PRODUCTION. DO NOT SKIP THIS STEP
    # NOTE: THIS IMPLEMENTATION IS NOT GENERATING THE POWERS OF TAU CORRECTLY.
    # YOU MUST ALSO IMPLEMENT THE ADDITIONAL gˆ(at) POINTS
    # TO ALLOW CHECKING THE KNOWLEDGE OF THE EXPONENT.
    if not univariate:
        size = (max_degree + 1) ** num_variables
        if size > 2**14:
            return DistributedKeyGen(num_variables, max_degree, modulo)
    return SequencialKeyGen(num_variables, max_degree, modulo, univariate=univariate)


def SumcheckGKRKeyGen(
    num_variables: int, max_degree: int, modulo: int = curve_order
) -> TPP:
    """Generate the public parameters (powers of tau) for the multilinear map when computing the zk sumcheck g multilinear univiariate polynomial

    Args:
        num_variables (int): Max number of variables in the polynomial
        max_degree (int): Maximum degree of the polynomial
        modulo (int, optional): Prime modulus. Defaults to curve_order.

    Returns:
        TPP: The public parameters
    """
    return KeyGen(num_variables, max_degree, modulo, univariate=True)


# Setup algorithm on the paper
def Commit(PP: TPP, f_poly: Poly, modulo: int = curve_order) -> TG2P:
    """Commits to a polynomial using the provided public parameters

    Args:
        PP (tuple[FQ2P, tuple[tuple[int]], FQ2P]): Public parameters
        f_poly (Poly): Polynomial to commit
        modulo (int, optional): prime modulo. Defaults to curve_order.

    Raises:
        ValueError: Raised when then monomial exponent vector not precomputed in Wn,d


    Returns:
        FQ2P: Committed polynomial
    """
    _, Wn_d = PP

    # Initialize FK_f as the identity element of the group
    FK_f = None  # Replace this with the correct way to get the identity element in G1
    # Iterate over each term in the polynomial
    for monomial, coefficient in zip(f_poly.monoms(), f_poly.coeffs()):
        # Convert monomial tuple to exponent vector usable with Wn_d
        exp_vector = tuple(monomial)
        if exp_vector in Wn_d:
            # Retrieve the precomputed group element corresponding to g^(t1^e1 * t2^e2 * ... * tn^en)
            g_exp = Wn_d[exp_vector]
            # Multiply this element by the coefficient (modulo curve order)
            term_element = ecc_multiply(g_exp, coefficient % modulo)
            if FK_f is None:
                FK_f = term_element
            else:
                # Add the term's group element to FK_f
                FK_f = ecc_add(FK_f, term_element)
        else:
            raise ValueError("Monomial exponent vector not precomputed in Wn,d")

    return FK_f


def decompose_polynomial(
    polynomial: Poly,
    random_point: list[int],
    variables: Symbol,
    domain: FiniteField = FiniteField(curve_order),
) -> list[Poly]:
    """Decompose the polynomial into divisors and quotient polynomials

    Args:
        polynomial (Poly): The polynomial used as reference for decomposition
        random_point (list[int]): The random point used to construct the divisor polynomials.
        The evaluation point used to construct the final for of the decomposed polynomial. e.g f(x) - f(r)
        variables (Symbol): The variables used in the polynomial
        domain (FiniteField, optional): the finite field mod p. Defaults to FiniteField(curve_order).

    Raises:
        ValueError: Raised when having a non-zero remainder after decomposition

    Returns:
        list[Poly]: The list of quotient polynomials
    """

    # Compute f(a) to find f(x) - f(a)
    f_a = polynomial.subs(
        {variables[i]: random_point[i] for i in range(len(variables))}
    )  # domain(f_poly.subs({variables[i]: a[i] for i in range(len(variables))}))

    # Start decomposition
    base_poly = polynomial - f_a
    remainder = base_poly
    quotients = []
    # Iteratively divide
    for i in range(len(variables) - 1):
        divisor = Poly(
            random_point[i] * (variables[i] - random_point[i])
            + variables[i + 1]
            - random_point[i + 1],
            *variables[i : i + 2],
            domain=domain,
        )
        quotient, remainder = reduced(remainder, [divisor], domain=domain)
        quotient = quotient[0]
        quotients.append(quotient)

    divisor = Poly(variables[-1] - random_point[-1], *variables, domain=domain)
    quotient, remainder = reduced(remainder, [divisor], domain=domain)
    quotient = quotient[0]
    quotients.append(quotient)
    # remainder should be zero if f(x) evaluates to f(a)
    if remainder != 0:
        raise ValueError(
            "Non-zero remainder, check the polynomial and points provided."
        )

    return quotients


# Compute algorithm on the paper
def Open(
    PK: TG1P,
    polynomial: Poly,
    variables: list[Symbol],
    random_point: list[int],
    domain=FiniteField(curve_order),
) -> tuple[int, Union[list[TG1P], list[TG2P]]]:
    """Open the polynomial commitment and compute the cryptographic representation of the quotient polynomials

    Args:
        PK (TG1P): Public parameters
        polynomial (Poly): The polynomial to open
        variables (list[Symbol]): The variables used in the polynomial
        random_point (list[int]): The random point used in the divisor polynomials. The evaluation point used in f(x) - f(r)
        domain (_type_, optional): The finite field domain used. Defaults to FiniteField(curve_order).
    Returns:
        tuple[int, Union[list[TG1P],list[TG2P]]]: The evaluation of the polynomial and the cryptographic representation of the quotient polynomials (proofs)
    """
    evaluation = domain(
        polynomial.subs({variables[i]: random_point[i] for i in range(len(variables))})
    )
    decomposed_qs = decompose_polynomial(polynomial, random_point, variables, domain)

    # Compute wi = FK(qi) using Setup for 1 ≤ i ≤ n - 1
    commited_quotients = []
    for q_poly in decomposed_qs[
        :-1
    ]:  # Exclude the last qn(xn) as it's handled separately
        # Setup for each q to get the cryptographic representation
        FK_q = Commit(PK, q_poly, domain.characteristic())
        commited_quotients.append(FK_q)

    last_quotient = decomposed_qs[-1]
    commited_quotients.append(last_quotient.as_poly())

    return int(evaluation) % domain.characteristic(), commited_quotients


def get_pk_tuple(idx: int, length: int) -> tuple[int]:
    """Get the tuple representation of the key for Wn,d

    Args:
        idx (int): The index of the key
        length (int): The length of the tuple

    Returns:
        tuple[int]: The tuple representation of the key
    """
    return tuple(1 if j == idx else 0 for j in range(length))


# ri*ti + ti+1 - ri*ai - ai+1
def build_divisor_poly(
    PK: Union[TG1P, TG2P], idx: int, random_point: list[int], modulo: int = curve_order
) -> Poly:
    """Build the divisor polynomial (ri*ti + ti+1 - ri*ai - ai+1) for the given index

    Args:
        PK (Union[TG1P, TG2P]): Public parameters
        idx (int): The index of the divisor polynomial to build
        random_point (list[int]): The random point used in the divisor polynomials
        modulo (int, optional): Prime modulus. Defaults to curve_order.

    Raises:
        ValueError: Raised when the key is not found in Wn,d

    Returns:
        Poly: The divisor polynomial
    """
    g, Wn_d = PK
    key = get_pk_tuple(idx, len(random_point))
    key_p = get_pk_tuple(idx + 1, len(random_point))
    if idx == len(random_point) - 1:
        raise ValueError("Last index, no divisor polynomial to build")
    if key in Wn_d:
        ti = Wn_d[key]
        tip1 = Wn_d[key_p]
        ri_ti = ecc_multiply(ti, random_point[idx])
        ri_ai = ecc_negate(
            ecc_multiply(g, (random_point[idx] * random_point[idx]) % modulo)
        )
        a_ip1 = ecc_negate(ecc_multiply(g, random_point[idx + 1]))
        i_term = ecc_add(ri_ti, ri_ai)
        ip_term = ecc_add(tip1, a_ip1)
        divisor_poly = ecc_add(i_term, ip_term)
        return divisor_poly
    raise ValueError(
        f"Key not found in Wn,d. Failed to build divisor polynomial for idx {idx}"
    )


def Verify(
    PP: TPP,
    FK_f: TG1P,
    evaluation: int,
    openings: list[Union[TG2P, Poly]],
    random_point: list[int],
    modulo: int = curve_order,
) -> bool:
    """Verify the polynomial commitment agains the multilinear kgzg scheme

    Args:
        PP (TPP): Public parameters
        FK_f (TG1P): the commitment to the polynomial f
        evaluation (int): The evaluation of f(x) - f(r)
        openings (list[Union[TG2P, Poly]]): The openings of the quotient polynomials from 0...n-1
        random_point (list[int]): The random point used in the divisor polynomials. The evaluation point used in f(x) - f(r)
        modulo (int, optional): The field modulo. Defaults to curve_order.

    Raises:
        ValueError: Raised when the key is not found in Wn,d

    Returns:
        bool: True if the verification passes, False otherwise
    """
    G1PK, G2PK = PP
    g, Wn_d_g2 = G2PK

    # Compute g^(-v)
    g_neg_v = ecc_negate(ecc_multiply(g, evaluation % modulo))

    # Setup left hand side of the equation
    left_hand_side = ecc_add(FK_f, g_neg_v)
    # Compute the product of pairings on the right hand side
    right_hand_side = 1  # Identity element for the pairing product
    for i, w_i in enumerate(openings[:-1]):
        key = get_pk_tuple(i, len(random_point))  # Construct the key for accessing Wn_d
        if key in Wn_d_g2:
            divisor_poly = build_divisor_poly(G2PK, i, random_point, modulo)
            pairing_result = pairing(divisor_poly, w_i)
            if right_hand_side is None:
                right_hand_side = pairing_result
            else:
                right_hand_side *= pairing_result
        else:
            raise ValueError("Key not found in Wn,d")

    tn_key = get_pk_tuple(len(openings) - 1, len(random_point))
    power_of_t_n_g2 = Wn_d_g2[tn_key]
    power_of_evaluation_pn = ecc_negate(ecc_multiply(G2, random_point[-1] % modulo))
    power_of_divisor_n = ecc_add(power_of_t_n_g2, power_of_evaluation_pn)
    qn = openings[-1]
    g_qn_tn = Commit(G1PK, qn)
    pairing_result = pairing(power_of_divisor_n, g_qn_tn)
    right_hand_side = right_hand_side * pairing_result
    left_hand_pairing = pairing(left_hand_side, G1)
    # Compare the left and right hand sides
    return left_hand_pairing == right_hand_side
