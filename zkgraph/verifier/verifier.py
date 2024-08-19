from zkgraph.circuits.circuit import LayeredCircuit, GateType
from zkgraph.polynomials.field import (
    FiniteField,
    ModularInteger,
    PRIME_MODULO as curve_order,
)
from typing import List
from zkgraph.transcript.transcript import CommonTranscript
from zkgraph.types.proof import ZeroKProofTranscript
from zkgraph.polynomials.poly import QuadraticPoly, QuintuplePoly
from typing import Union

DOMAIN = FiniteField(curve_order)


class ZkVerifier:
    def __init__(self, circuit: LayeredCircuit, domain: FiniteField = DOMAIN):
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
            last = j == self.C.circuit[i - 1].bitLength - 1
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
            rho = self.generate_randomness(size=1, label="rho")[0]
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
            self.one_minus_r_u = [self.domain.zero] * previous_bit_len
            self.one_minus_r_v = [self.domain.zero] * previous_bit_len
            for j in range(previous_bit_len):
                self.one_minus_r_u[j] = self.domain.one - self.r_u[j]
                self.one_minus_r_v[j] = self.domain.one - self.r_v[j]
            alpha_beta_sum, previous_random = self.verify_phase_1(
                previous_random, alpha_beta_sum, previous_bit_len, i
            )
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
