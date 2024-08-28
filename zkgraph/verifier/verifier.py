# The code below is based on the C++ Libra implementation found at https://github.com/sunblaze-ucb/Libra
# Implemented during the BnB Q3 Hackathon 2024

from zkgraph.circuits.circuit import LayeredCircuit, GateType
from zkgraph.polynomials.field import (
    FiniteField,
    ModularInteger,
    PRIME_MODULO as curve_order,
)
from collections import defaultdict
from typing import List, Dict
from zkgraph.transcript.transcript import CommonTranscript
from zkgraph.types.proof import ZeroKProofTranscript
from zkgraph.polynomials.poly import QuadraticPoly, QuintuplePoly
from typing import Union

from zkgraph.commitments.mkzg.mkzg import (
    verify_random_polynomial_R,
    verify_zk_sumcheck_polynomial,
    load_pp,
)
from zkgraph.polynomials.field import dequantization, quantization

DOMAIN = FiniteField(curve_order)


class ZkVerifier:
    def __init__(
        self,
        circuit: LayeredCircuit,
        domain: FiniteField = DOMAIN,
        mkzg: bool = False,
        public_parameters: Dict[str, str] = {"r_pp": None, "zk_pp": None},
        collect_noir_transcript: bool = True,
    ):
        self.C = circuit
        self.domain = domain
        self.beta_g_r0: List[ModularInteger] = []
        self.beta_g_r1: List[ModularInteger] = []
        self.beta_u: List[ModularInteger] = []
        self.beta_v: List[ModularInteger] = []
        self.r_0: List[ModularInteger] = []
        self.r_1: List[ModularInteger] = []
        self.r_u: List[ModularInteger] = []
        self.r_v: List[ModularInteger] = []
        self.one_minus_r_0: List[ModularInteger] = []
        self.one_minus_r_1: List[ModularInteger] = []
        self.one_minus_r_u: List[ModularInteger] = []
        self.one_minus_r_v: List[ModularInteger] = []
        self.proof_transcript = ZeroKProofTranscript()
        self.transcript = CommonTranscript(b"zerok", self.proof_transcript)
        self.one = self.domain.one
        self.zero = self.domain.zero
        self.mkzg = mkzg
        self.random_polynomial_r_pp = None
        self.zk_sumcheck_pp = None
        self.collect_transcript = collect_noir_transcript
        self.noir_noir_transcript = None
        if self.collect_transcript:
            self.noir_noir_transcript = defaultdict(lambda: defaultdict(list))
        if self.mkzg:
            if public_parameters["r_pp"] is None or public_parameters["zk_pp"] is None:
                raise ValueError(
                    "r_pp and zk_pp must be provided when using the MKZG PCS"
                )
            if isinstance(public_parameters["r_pp"], str):
                self.random_polynomial_r_pp = load_pp(public_parameters["r_pp"])
            else:
                self.random_polynomial_r_pp = public_parameters["r_pp"]
            if isinstance(public_parameters["zk_pp"], str):
                self.zk_sumcheck_pp = load_pp(public_parameters["zk_pp"])
            else:
                self.zk_sumcheck_pp = public_parameters["zk_pp"]

    def mult(self, depth: int) -> ModularInteger:
        ret = self.domain.zero
        for i in range(1 << self.C.circuit[depth].bitLength):
            g = i
            u = self.C.circuit[depth].gates[i].u
            v = self.C.circuit[depth].gates[i].v
            ty = self.C.circuit[depth].gates[i].ty
            if ty == GateType.Mul:
                ret = (
                    ret
                    + (self.beta_g_r0[g] + self.beta_g_r1[g])
                    * self.beta_u[u]
                    * self.beta_v[v]
                )
        return ret

    def add(self, depth: int) -> ModularInteger:
        ret = self.domain.zero
        for i in range(1 << self.C.circuit[depth].bitLength):
            g = i
            u = self.C.circuit[depth].gates[i].u
            v = self.C.circuit[depth].gates[i].v
            ty = self.C.circuit[depth].gates[i].ty
            if ty == GateType.Add:
                ret = (
                    ret
                    + (self.beta_g_r0[g] + self.beta_g_r1[g])
                    * self.beta_u[u]
                    * self.beta_v[v]
                )
        return ret

    def direct_relay(
        self, depth: int, r_g: List[ModularInteger], r_u: List[ModularInteger]
    ) -> ModularInteger:
        if depth != 1:
            return self.domain.zero
        else:
            ret = self.domain.one
            for i in range(self.C.circuit[depth].bitLength):
                ret = ret * (
                    self.domain.one - r_g[i] - r_u[i] + self.domain(2) * r_g[i] * r_u[i]
                )
            return ret

    def relay_gate(self, depth: int) -> ModularInteger:
        ret = self.domain.zero
        for i in range(1 << self.C.circuit[depth].bitLength):
            g = i
            u = self.C.circuit[depth].gates[i].u
            v = self.C.circuit[depth].gates[i].v
            ty = self.C.circuit[depth].gates[i].ty
            if ty == GateType.Relay:
                assert v == 0, "v must be 0 for relay gate!"
                ret = (
                    ret
                    + (self.beta_g_r0[g] + self.beta_g_r1[g])
                    * self.beta_u[u]
                    * self.beta_v[v]
                )
        return ret

    def generate_randomness(self, size: int, label: str) -> List[ModularInteger]:
        return self.transcript.get_sympy_ff_challenges(label.encode(), size)

    def V_in(
        self,
        r_0: List[ModularInteger],
        one_minus_r_0: List[ModularInteger],
        output_raw: List[ModularInteger],
        r_0_size: int,
        output_size: int,
    ) -> ModularInteger:
        output = [self.domain.zero] * output_size
        for i in range(output_size):
            output[i] = output_raw[i]
        for i in range(r_0_size):
            for j in range(output_size >> 1):
                output[j] = (
                    output[j << 1] * one_minus_r_0[i] + output[j << 1 | 1] * r_0[i]
                )
            output_size >>= 1
        return output[0]

    def verify_phase_1(
        self,
        previous_random: ModularInteger,
        alpha_beta_sum: ModularInteger,
        previous_bit_len: int,
        i: int,
    ):
        for j in range(previous_bit_len):
            poly: Union[QuadraticPoly, QuintuplePoly] = (
                self.transcript.proof_transcript.retrieve_transcript_by_label(
                    b"phase_1"
                )
            )
            self.transcript.append_sympy_ff_list(b"phase_1", poly.coefficients())
            previous_random = self.r_u[j]
            if (poly.eval(self.zero) + poly.eval(self.one)) != alpha_beta_sum:
                assert False, f"Verification fail, phase 1, circuit {i}, bit {j}"
            if self.collect_transcript:
                self.noir_noir_transcript[i]["phase_1"].append(
                    [poly.eval(self.zero) + poly.eval(self.one), alpha_beta_sum]
                )
            alpha_beta_sum = poly.eval(self.r_u[j])
        return alpha_beta_sum, previous_random

    def verify_phase_2(
        self,
        previous_random: ModularInteger,
        alpha_beta_sum: ModularInteger,
        previous_bit_len: int,
        i: int,
    ):
        previous_random = self.domain.zero
        for j in range(previous_bit_len):
            # last = j == self.C.circuit[i - 1].bitLength - 1
            poly: Union[QuadraticPoly, QuintuplePoly] = (
                self.transcript.proof_transcript.retrieve_transcript_by_label(
                    b"phase_2"
                )
            )
            v_u = self.transcript.proof_transcript.retrieve_transcript_by_label(b"v_u")
            self.transcript.append_sympy_ff_list(b"phase_2", poly.coefficients())
            self.transcript.append_sympy_ff(b"v_u", v_u)
            previous_random = self.r_v[j]
            # TODO: Condense poly.eval(self.zero) + poly.eval(self.one) + direct_relay_value * self.prover.v_u
            # into a single polynomial over the hypercube {0,1}
            claim = (
                (poly.eval(self.zero) + poly.eval(self.one)) != alpha_beta_sum
                if j == 0
                else (poly.eval(self.zero) + poly.eval(self.one) + v_u)
                != alpha_beta_sum
            )
            if claim:
                assert False, f"Verification fail, phase 2, circuit {i}, bit {j}"
            if self.collect_transcript:
                self.noir_noir_transcript[i]["phase_2"].append(
                    [
                        (
                            poly.eval(self.zero) + poly.eval(self.one)
                            if j == 0
                            else poly.eval(self.zero) + poly.eval(self.one) + v_u
                        ),
                        alpha_beta_sum,
                    ]
                )
            alpha_beta_sum = poly.eval(self.r_v[j]) + v_u
        return alpha_beta_sum, previous_random

    def verify_gkr_round(self, alpha_beta_sum, i, alpha, beta, r_c):
        # self.v_u, self.v_v = self.prover.sumcheck_finalize(previous_random)
        v_u = self.transcript.proof_transcript.retrieve_transcript_by_label(b"v_u")
        v_v = self.transcript.proof_transcript.retrieve_transcript_by_label(b"v_v")
        self.transcript.append_sympy_ff(b"v_u", v_u)
        self.transcript.append_sympy_ff(b"v_v", v_v)
        poly: Union[QuadraticPoly, QuintuplePoly] = (
            self.transcript.proof_transcript.retrieve_transcript_by_label(
                b"final_gkr_round"
            )
        )

        direct_relay_value = (
            self.transcript.proof_transcript.retrieve_transcript_by_label(
                b"v_u_direct_relay"
            )
        )
        self.transcript.append_sympy_ff_list(b"final_gkr_round", poly.coefficients())
        self.transcript.append_sympy_ff(b"v_u_direct_relay", direct_relay_value)

        # TODO: Condense poly.eval(self.zero) + poly.eval(self.one) + direct_relay_value * self.prover.v_u
        # into a single polynomial over the hypercube {0,1}
        claim = (
            poly.eval(self.zero) + poly.eval(self.one)
            if i == 1
            else poly.eval(self.zero) + poly.eval(self.one) + v_u * direct_relay_value
        )
        if alpha_beta_sum != claim:
            assert False, f"Verification fail, circuit {i}"
        if self.collect_transcript:
            self.noir_noir_transcript[i]["gkr_round"].append(
                [
                    (
                        poly.eval(self.zero) + poly.eval(self.one)
                        if i == 1
                        else poly.eval(self.zero)
                        + poly.eval(self.one)
                        + v_u * direct_relay_value
                    ),
                    alpha_beta_sum,
                ]
            )
        self.alpha = self.generate_randomness(size=1, label="alpha")[0]
        self.beta = self.generate_randomness(size=1, label="beta")[0]
        if i != 1:
            alpha_beta_sum = alpha * v_u + beta * v_v
        else:
            alpha_beta_sum = v_u
        self.r_0 = self.r_u[:]
        self.r_1 = self.r_v[:]
        self.one_minus_r_0 = self.one_minus_r_u[:]
        self.one_minus_r_1 = self.one_minus_r_v[:]
        return alpha_beta_sum

    def verify_input(self, alpha_beta_sum: ModularInteger):
        input = [self.domain.zero] * (1 << self.C.circuit[0].bitLength)
        for i in range(1 << self.C.circuit[0].bitLength):
            g = i
            gate = self.C.circuit[0].gates[g]
            ty = gate.ty
            if ty == GateType.Input:
                input[g] = gate.u
            else:
                assert False, "Invalid gate type. Must be a input gate!"
        input_0 = self.transcript.proof_transcript.retrieve_transcript_by_label(
            b"input"
        )
        if alpha_beta_sum != input_0:
            assert False, "Verification fail, final input check fail"
        if self.collect_transcript:
            self.noir_noir_transcript[i]["input"].append(
                [
                    input_0,
                    alpha_beta_sum,
                ]
            )
        return alpha_beta_sum

    def run_verifier(self, proof_transcript: bytes) -> bool:
        self.proof_transcript.from_bytes(proof_transcript)
        alpha = self.domain.one
        beta = self.domain.zero
        bit_len = self.C.circuit[self.C.total_depth - 1].bitLength
        self.r_0 = self.generate_randomness(size=bit_len, label="r_0")
        self.r_1 = self.generate_randomness(size=bit_len, label="r_1")
        self.one_minus_r_0 = [self.domain.zero] * bit_len
        self.one_minus_r_1 = [self.domain.zero] * bit_len
        for i in range(bit_len):
            self.one_minus_r_0[i] = self.domain.one - self.r_0[i]
            self.one_minus_r_1[i] = self.domain.one - self.r_1[i]
        for i in list(reversed(range(1, self.C.total_depth))):
            previous_bit_len = self.C.circuit[i - 1].bitLength
            # rho = self.generate_randomness(size=1, label="rho")[0]
            self.generate_randomness(size=1, label="rho")[0]
            alpha_beta_sum = (
                self.transcript.proof_transcript.retrieve_transcript_by_label(
                    b"alpha_beta_sum"
                )
            )
            self.transcript.append_sympy_ff(b"alpha_beta_sum", alpha_beta_sum)
            previous_random = self.domain.zero
            self.r_u = self.generate_randomness(size=previous_bit_len, label="r_u")
            self.r_v = self.generate_randomness(size=previous_bit_len, label="r_v")
            direct_relay_value = (
                self.transcript.proof_transcript.retrieve_transcript_by_label(
                    b"direct_relay_value"
                )
            )
            self.transcript.append_sympy_ff(b"direct_relay_value", direct_relay_value)
            r_c = self.generate_randomness(size=1, label="r_c")
            if self.mkzg:
                if len(self.C.circuit) - 1 != i:
                    random_point = [self.prepreu1, r_c[0]]
                    random_r_commitment = (
                        self.transcript.proof_transcript.retrieve_transcript_by_label(
                            b"random_r_commitment"
                        )
                    )
                    openings = (
                        self.transcript.proof_transcript.retrieve_transcript_by_label(
                            b"random_r_openings"
                        )
                    )
                    evaluation = (
                        self.transcript.proof_transcript.retrieve_transcript_by_label(
                            b"random_r_evaluation"
                        )
                    )

                    self.transcript.append_curve_point(
                        b"random_r_commitment", random_r_commitment
                    )
                    self.transcript.append_curve_point(b"random_r_openings", openings)
                    self.transcript.append_sympy_ff(b"random_r_evaluation", evaluation)
                    assert verify_random_polynomial_R(
                        random_r_commitment,
                        random_point,
                        evaluation,
                        openings,
                        self.random_polynomial_r_pp,
                        curve_order,
                    )
                    zk_sumcheck_random_point = [*self.r_u, *self.r_v, r_c[0]]
                    maspoly_size = (previous_bit_len * 2 + 1) * 2 + 1 + 6
                    half_maskpoly = maspoly_size // 2
                    if half_maskpoly >= len(zk_sumcheck_random_point):
                        zk_sumcheck_random_point_size_to_fill = abs(
                            half_maskpoly - len(zk_sumcheck_random_point)
                        )
                        zk_sumcheck_random_point.extend(
                            self.generate_randomness(
                                size=zk_sumcheck_random_point_size_to_fill, label="r_c"
                            )
                        )
                    else:
                        zk_sumcheck_random_point = zk_sumcheck_random_point[
                            :half_maskpoly
                        ]
                    zk_sumcheck_commitment = (
                        self.transcript.proof_transcript.retrieve_transcript_by_label(
                            b"maskpoly_commitment"
                        )
                    )
                    zk_sumcheck_openings = (
                        self.transcript.proof_transcript.retrieve_transcript_by_label(
                            b"maskpoly_openings"
                        )
                    )
                    zk_sumcheck_evaluation = (
                        self.transcript.proof_transcript.retrieve_transcript_by_label(
                            b"maskpoly_evaluation"
                        )
                    )
                    self.transcript.append_curve_point(
                        b"maskpoly_commitment", zk_sumcheck_commitment
                    )
                    self.transcript.append_curve_point(
                        b"maskpoly_openings", zk_sumcheck_openings
                    )
                    self.transcript.append_sympy_ff(
                        b"maskpoly_evaluation", zk_sumcheck_evaluation
                    )
                    assert verify_zk_sumcheck_polynomial(
                        zk_sumcheck_commitment,
                        zk_sumcheck_random_point,
                        zk_sumcheck_evaluation,
                        zk_sumcheck_openings,
                        self.zk_sumcheck_pp,
                        curve_order,
                    )
            self.one_minus_r_u = [self.domain.zero] * previous_bit_len
            self.one_minus_r_v = [self.domain.zero] * previous_bit_len
            for j in range(previous_bit_len):
                self.one_minus_r_u[j] = self.domain.one - self.r_u[j]
                self.one_minus_r_v[j] = self.domain.one - self.r_v[j]
            alpha_beta_sum, previous_random = self.verify_phase_1(
                previous_random, alpha_beta_sum, previous_bit_len, i
            )
            self.prepreu1 = previous_random
            previous_random = self.domain.zero

            alpha_beta_sum, previous_random = self.verify_phase_2(
                previous_random=previous_random,
                alpha_beta_sum=alpha_beta_sum,
                previous_bit_len=previous_bit_len,
                i=i,
            )

            alpha_beta_sum = self.verify_gkr_round(
                alpha_beta_sum=alpha_beta_sum,
                i=i,
                alpha=alpha,
                beta=beta,
                r_c=r_c,
            )
        self.verify_input(alpha_beta_sum)
        return True

    def get_noir_transcript(self):
        prime_mod = 2**32 - 1
        phase_1_left = []
        phase_1_right = []
        phase_2_left = []
        phase_2_right = []
        gkr_round_left = []
        gkr_round_right = []
        input_round_left = []
        input_round_right = []
        for k, v in self.noir_noir_transcript.items():
            phase_1 = v["phase_1"]
            for i in phase_1:
                phase_1_left.append(
                    quantization(round(dequantization(i[1].val), 2)) % prime_mod
                )
                phase_1_right.append(
                    quantization(round(dequantization(i[1].val), 2)) % prime_mod
                )
            phase_2 = v["phase_2"]
            for i in phase_2:
                phase_2_left.append(
                    quantization(round(dequantization(i[1].val), 2)) % prime_mod
                )
                phase_2_right.append(
                    quantization(round(dequantization(i[1].val), 2)) % prime_mod
                )
            gkr_round = v["gkr_round"]
            for i in gkr_round:
                gkr_round_left.append(
                    quantization(round(dequantization(i[1].val), 2)) % prime_mod
                )
                gkr_round_right.append(
                    quantization(round(dequantization(i[1].val), 2)) % prime_mod
                )
            input_round = v["input"]
            for i in input_round:
                input_round_left.append(
                    quantization(round(dequantization(i[1].val), 2)) % prime_mod
                )
                input_round_right.append(
                    quantization(round(dequantization(i[1].val), 2)) % prime_mod
                )
        max_size = 150
        if len(phase_1_left) < max_size:
            size_to_100 = max_size - len(phase_1_left)
            phase_1_left.extend([0] * size_to_100)
        if len(phase_1_right) < max_size:
            size_to_100 = max_size - len(phase_1_right)
            phase_1_right.extend([0] * size_to_100)
        if len(phase_2_left) < max_size:
            size_to_100 = max_size - len(phase_2_left)
            phase_2_left.extend([0] * size_to_100)
        if len(phase_2_right) < max_size:
            size_to_100 = max_size - len(phase_2_right)
            phase_2_right.extend([0] * size_to_100)
        if len(gkr_round_left) < max_size:
            size_to_100 = max_size - len(gkr_round_left)
            gkr_round_left.extend([0] * size_to_100)
        if len(gkr_round_right) < max_size:
            size_to_100 = max_size - len(gkr_round_right)
            gkr_round_right.extend([0] * size_to_100)
        if len(input_round_left) < max_size:
            size_to_100 = max_size - len(input_round_left)
            input_round_left.extend([0] * size_to_100)
        if len(input_round_right) < max_size:
            size_to_100 = max_size - len(input_round_right)
            input_round_right.extend([0] * size_to_100)
        noir_input = f"""phase_1_left = {phase_1_left}\nphase_1_right = {phase_1_right}\nphase_2_left = {phase_2_left}\nphase_2_right = {phase_2_right}\ngkr_left = {gkr_round_left}\ngkr_right = {gkr_round_right}\ninput_left = {input_round_left}\ninput_right = {input_round_right}"""
        # check if values are equal
        assert len(phase_1_left) == len(
            phase_1_right
        ), f"{set(phase_1_left) - set(phase_1_right)}"
        assert len(phase_2_left) == len(
            phase_2_right
        ), f"{set(phase_2_left) - set(phase_2_right)}"
        assert len(gkr_round_left) == len(
            gkr_round_right
        ), f"{set(gkr_round_left) - set(gkr_round_right)}"
        assert len(input_round_left) == len(
            input_round_right
        ), f"{set(input_round_left) - set(input_round_right)}"
        with open("./onchain_verifier/Prover.toml", "w+") as f:
            f.write(noir_input)
        return noir_input
