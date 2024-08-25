# The code below is based on the Libra C++ implementation found at https://github.com/sunblaze-ucb/Libra


from zkgraph.circuits.circuit import (
    LayeredCircuit,
    GateType,
)
import time
from zkgraph.polynomials.field import (
    FiniteField,
    ModularInteger,
    PRIME_MODULO as curve_order,
)
from typing import List, Tuple, Union
from zkgraph.polynomials.poly import (
    LinearPoly,
    QuadraticPoly,
    QuintuplePoly,
)
from zkgraph.utils.utils import my_resize, my_resize_pol
from zkgraph.transcript.transcript import CommonTranscript
from zkgraph.types.proof import ZeroKProofTranscript

DOMAIN = FiniteField(curve_order)


def interpolate(
    domain: FiniteField, zero_v: FiniteField, one_v: FiniteField
) -> LinearPoly:
    return LinearPoly(domain, one_v - zero_v, zero_v)


class ZkProver:
    def __init__(self, circuit: LayeredCircuit, domain: FiniteField = DOMAIN):
        self.domain: FiniteField = domain
        self.C: LayeredCircuit = circuit
        self.zero = domain(0, True)
        self.one = domain(1, True)
        self.two = domain(2, True)
        self.v_u: ModularInteger = self.zero
        self.v_v: ModularInteger = self.zero
        self.total_uv: int = self.zero
        self.circuit_value = [self.zero] * 1000000
        self.sumcheck_layer_id: int = 0
        self.length_g: int = 0
        self.length_u: int = 0
        self.length_v: int = 0
        self.alpha: ModularInteger = self.zero
        self.beta: ModularInteger = self.zero
        self.r_0: List[ModularInteger] = []
        self.r_1: List[ModularInteger] = []
        self.one_minus_r_0: List[ModularInteger] = []
        self.one_minus_r_1: List[ModularInteger] = []
        self.addV_array: List[LinearPoly] = []
        self.V_mult_add: List[LinearPoly] = []
        self.beta_u: List[ModularInteger] = []
        self.beta_g_r0_fhalf: List[ModularInteger] = []
        self.beta_g_r0_shalf: List[ModularInteger] = []
        self.beta_g_r1_fhalf: List[ModularInteger] = []
        self.beta_g_r1_shalf: List[ModularInteger] = []
        self.beta_u_fhalf: List[ModularInteger] = []
        self.beta_u_shalf: List[ModularInteger] = []
        self.beta_g_sum: List[ModularInteger] = []
        self.add_mult_sum: List[LinearPoly] = []
        self.total_time: float = 0.0

        self.r_0: List[ModularInteger] = []
        self.r_1: List[ModularInteger] = []
        self.r_u: List[ModularInteger] = []
        self.r_v: List[ModularInteger] = []
        self.one_minus_r_u: List[ModularInteger] = []
        self.one_minus_r_v: List[ModularInteger] = []
        self.proof_transcript = ZeroKProofTranscript()
        self.transcript = CommonTranscript(b"zerok", self.proof_transcript)
        self.inv_2: ModularInteger = self.two.inverse()
        self.maskpoly: List[ModularInteger] = []
        self.maskpoly_gmp: List[int] = []
        self.maskpoly_sumc: ModularInteger = self.zero
        self.maskpoly_sumr: ModularInteger = self.zero
        self.rho: ModularInteger = self.zero
        self.maskR: List[ModularInteger] = [self.zero] * 6
        self.preR: List[ModularInteger] = [self.zero] * 6
        self.r_f_R: int = 0
        self.r_f_mask_poly: int = 0
        self.r_f_input: int = 0
        self.r_f_input2: int = 0
        self.maskR_sumcu: ModularInteger = self.zero
        self.maskR_sumcv: ModularInteger = self.zero
        self.preZu: ModularInteger = self.zero
        self.preZv: ModularInteger = self.zero
        self.Zu: ModularInteger = self.zero
        self.Zv: ModularInteger = self.zero
        self.preu1: ModularInteger = self.zero
        self.prev1: ModularInteger = self.zero
        self.Iuv: ModularInteger = self.zero
        self.prepreu1: ModularInteger = self.zero
        self.preprev1: ModularInteger = self.zero
        self.Rg1: QuadraticPoly = QuadraticPoly(self.domain)
        self.Rg2: QuadraticPoly = QuadraticPoly(self.domain)
        self.sumRc: QuadraticPoly = QuadraticPoly(self.domain)
        self.input_mpz: List[int] = []
        self.maskr_mpz: List[int] = []
        self.maskr: List[ModularInteger] = []

    def V_res(
        self,
        one_minus_r_0: List[ModularInteger],
        r_0: List[ModularInteger],
        output_raw: List[ModularInteger],
        r_0_size: int,
        output_size: int,
    ) -> ModularInteger:
        start_timer = time.time()
        output = [self.zero] * output_size
        for i in range(output_size):
            output[i] = output_raw[i]
        for i in range(r_0_size):
            for j in range(output_size >> 1):
                output[j] = (
                    output[j << 1] * one_minus_r_0[i] + output[j << 1 | 1] * r_0[i]
                )
            output_size >>= 1
        self.total_time += time.time() - start_timer
        return output[0]

    def check_connectiveness(self):
        size = self.C.size
        for i in range(1, size):
            layer = self.C.circuit[i]
            for j in range(1, len(layer.gates)):
                gate = layer.gates[j]
                u = gate.u
                if u is None or u >= len(self.C.circuit[i - 1].gates):
                    raise ValueError(
                        f"Invalid circuit: gate {j} in layer {i} references non-existing gates"
                    )

    def evaluate(self):
        # Initialize the circuit value storage with the appropriate sizes
        self.circuit_value = my_resize(self.circuit_value, self.C.size + 1, self.domain)
        self.circuit_value[0] = my_resize(
            [], 1 << self.C.circuit[0].bitLength, self.domain
        )
        self.check_connectiveness()
        # Evaluate the input layer
        for g, gate_info in enumerate(self.C.circuit[0].gates):
            assert gate_info.ty == GateType.Input
            self.circuit_value[0][g] = self.domain(gate_info.u)

        # Evaluate each subsequent layer
        for i in range(1, self.C.size):
            self.circuit_value[i] = [
                self.zero for _ in range(len(self.C.circuit[i].gates))
            ]
            for g, gate_info in enumerate(self.C.circuit[i].gates):
                ty = gate_info.ty
                u = gate_info.u
                v = gate_info.v

                # Perform the gate operation based on the gate type
                if ty == GateType.Add:
                    self.circuit_value[i][g] = (
                        self.circuit_value[i - 1][u] + self.circuit_value[i - 1][v]
                    )
                elif ty == GateType.Sub:
                    self.circuit_value[i][g] = (
                        self.circuit_value[i - 1][u] - self.circuit_value[i - 1][v]
                    )
                elif ty == GateType.AntiSub:
                    self.circuit_value[i][g] = (
                        -self.circuit_value[i - 1][u] + self.circuit_value[i - 1][v]
                    )
                elif ty == GateType.Mul:
                    self.circuit_value[i][g] = (
                        self.circuit_value[i - 1][u] * self.circuit_value[i - 1][v]
                    )
                elif ty == GateType.Naab:
                    self.circuit_value[i][g] = (
                        self.circuit_value[i - 1][v]
                        - self.circuit_value[i - 1][u] * self.circuit_value[i - 1][v]
                    )
                elif ty == GateType.AntiNaab:
                    self.circuit_value[i][g] = (
                        self.circuit_value[i - 1][u]
                        - self.circuit_value[i - 1][u] * self.circuit_value[i - 1][v]
                    )
                elif ty == GateType.Addc:
                    self.circuit_value[i][g] = (
                        self.circuit_value[i - 1][u] + gate_info.c
                    )
                elif ty == GateType.Mulc:
                    self.circuit_value[i][g] = (
                        self.circuit_value[i - 1][u] * gate_info.c
                    )
                elif ty == GateType.Copy:
                    self.circuit_value[i][g] = self.circuit_value[i - 1][u]
                elif ty == GateType.Not:
                    self.circuit_value[i][g] = self.one - self.circuit_value[i - 1][u]
                elif ty == GateType.Xor:
                    # XOR is equivalent to addition in a field of 2 elements
                    self.circuit_value[i][g] = (
                        self.circuit_value[i - 1][u]
                        + self.circuit_value[i - 1][v]
                        - self.two
                        * self.circuit_value[i - 1][u]
                        * self.circuit_value[i - 1][v]
                    )
                elif ty == GateType.Relay:
                    self.circuit_value[i][g] = self.circuit_value[i - 1][u]
                else:
                    raise ValueError(f"Unsupported gate type: {ty}")

    def sumcheck_init(
        self,
        layer_id: int,
        bit_length_g: int,
        bit_length_u: int,
        bit_length_v: int,
        alpha: ModularInteger,
        beta: ModularInteger,
        r_0: List[ModularInteger],
        r_1: List[ModularInteger],
        o_r_0: List[ModularInteger],
        o_r_1: List[ModularInteger],
    ):
        self.r_0 = r_0
        self.r_1 = r_1
        self.alpha = alpha
        self.beta = beta
        self.sumcheck_layer_id = layer_id
        self.length_g = bit_length_g
        self.length_u = bit_length_u
        self.length_v = bit_length_v
        self.one_minus_r_0 = o_r_0
        self.one_minus_r_1 = o_r_1
        return self.generate_maskR(layer_id=layer_id)

    def init_array(self, max_bit_length: int):
        self.add_mult_sum = my_resize_pol(
            self.add_mult_sum, 1 << max_bit_length, LinearPoly(self.domain)
        )
        self.V_mult_add = my_resize_pol(
            self.V_mult_add, 1 << max_bit_length, LinearPoly(self.domain)
        )
        self.addV_array = my_resize_pol(
            self.addV_array, 1 << max_bit_length, LinearPoly(self.domain)
        )
        self.beta_g_sum = my_resize(self.beta_g_sum, 1 << max_bit_length, self.domain)
        self.beta_u = my_resize(self.beta_u, 1 << max_bit_length, self.domain)
        half_length = (max_bit_length >> 1) + 1
        self.beta_g_r0_fhalf = my_resize(
            self.beta_g_r0_fhalf, 1 << half_length, self.domain
        )
        self.beta_g_r0_shalf = my_resize(
            self.beta_g_r0_shalf, 1 << half_length, self.domain
        )
        self.beta_g_r1_fhalf = my_resize(
            self.beta_g_r1_fhalf, 1 << half_length, self.domain
        )
        self.beta_g_r1_shalf = my_resize(
            self.beta_g_r1_shalf, 1 << half_length, self.domain
        )
        self.beta_u_fhalf = my_resize(self.beta_u_fhalf, 1 << half_length, self.domain)
        self.beta_u_shalf = my_resize(self.beta_u_shalf, 1 << half_length, self.domain)

    def sumcheck_update(
        self,
        ret: Union[QuadraticPoly, QuintuplePoly],
        current_bit: int,
        previous_random: ModularInteger,
    ) -> Union[QuadraticPoly, QuintuplePoly]:
        for i in range(self.total_uv >> 1):
            g_zero = i << 1
            g_one = g_zero | 1
            self.V_mult_add[i] = interpolate(
                self.domain,
                self.V_mult_add[g_zero].eval(previous_random),
                self.V_mult_add[g_one].eval(previous_random),
            )
            self.addV_array[i] = interpolate(
                self.domain,
                self.addV_array[g_zero].eval(previous_random),
                self.addV_array[g_one].eval(previous_random),
            )
            self.add_mult_sum[i] = interpolate(
                self.domain,
                self.add_mult_sum[g_zero].eval(previous_random),
                self.add_mult_sum[g_one].eval(previous_random),
            )
            ret.a = ret.a + self.add_mult_sum[i].a * self.V_mult_add[i].a
            ret.b = (
                ret.b
                + self.add_mult_sum[i].a * self.V_mult_add[i].b
                + self.add_mult_sum[i].b * self.V_mult_add[i].a
                + self.addV_array[i].a
            )
            ret.c = (
                ret.c
                + self.add_mult_sum[i].b * self.V_mult_add[i].b
                + self.addV_array[i].b
            )

        return ret

    def sumcheck_phase1_init(self):
        start_timer = time.time()
        self.total_uv = 1 << self.C.circuit[self.sumcheck_layer_id - 1].bitLength
        for i in range(self.total_uv):
            self.V_mult_add[i] = LinearPoly(
                self.domain, b=self.circuit_value[self.sumcheck_layer_id - 1][i]
            )
            self.addV_array[i] = LinearPoly(self.domain)
            self.add_mult_sum[i] = LinearPoly(self.domain)

        self.beta_g_r0_fhalf[0] = self.alpha
        self.beta_g_r1_fhalf[0] = self.beta
        self.beta_g_r0_shalf[0] = self.one
        self.beta_g_r1_shalf[0] = self.one

        first_half = self.length_g >> 1
        second_half = self.length_g - first_half

        for i in range(first_half):
            for j in range(1 << i):
                self.beta_g_r0_fhalf[j | (1 << i)] = (
                    self.beta_g_r0_fhalf[j] * self.r_0[i]
                )
                self.beta_g_r0_fhalf[j] = (
                    self.beta_g_r0_fhalf[j] * self.one_minus_r_0[i]
                )
                self.beta_g_r1_fhalf[j | (1 << i)] = (
                    self.beta_g_r1_fhalf[j] * self.r_1[i]
                )
                self.beta_g_r1_fhalf[j] = (
                    self.beta_g_r1_fhalf[j] * self.one_minus_r_1[i]
                )
        for i in range(second_half):
            for j in range(1 << i):
                self.beta_g_r0_shalf[j | (1 << i)] = (
                    self.beta_g_r0_shalf[j] * self.r_0[i + first_half]
                )
                self.beta_g_r0_shalf[j] = (
                    self.beta_g_r0_shalf[j] * self.one_minus_r_0[i + first_half]
                )
                self.beta_g_r1_shalf[j | (1 << i)] = (
                    self.beta_g_r1_shalf[j] * self.r_1[i + first_half]
                )
                self.beta_g_r1_shalf[j] = (
                    self.beta_g_r1_shalf[j] * self.one_minus_r_1[i + first_half]
                )
        mask_fhalf = (1 << first_half) - 1
        for i in range(1 << self.length_g):
            self.beta_g_sum[i] = (
                self.beta_g_r0_fhalf[i & mask_fhalf]
                * self.beta_g_r0_shalf[i >> first_half]
                + self.beta_g_r1_fhalf[i & mask_fhalf]
                * self.beta_g_r1_shalf[i >> first_half]
            )
        for i in range(1 << self.length_g):
            u = self.C.circuit[self.sumcheck_layer_id].gates[i].u
            v = self.C.circuit[self.sumcheck_layer_id].gates[i].v
            ty = self.C.circuit[self.sumcheck_layer_id].gates[i].ty
            if ty == GateType.Add:
                tmp = (
                    self.beta_g_r0_fhalf[i & mask_fhalf]
                    * self.beta_g_r0_shalf[i >> first_half]
                ) + (
                    self.beta_g_r1_fhalf[i & mask_fhalf]
                    * self.beta_g_r1_shalf[i >> first_half]
                )
                self.addV_array[u].b = (
                    self.addV_array[u].b
                    + self.circuit_value[self.sumcheck_layer_id - 1][v] * tmp
                )
                self.add_mult_sum[u].b = self.add_mult_sum[u].b + tmp
            elif ty == GateType.Mul:
                tmp = (
                    self.beta_g_r0_fhalf[i & mask_fhalf]
                    * self.beta_g_r0_shalf[i >> first_half]
                ) + (
                    self.beta_g_r1_fhalf[i & mask_fhalf]
                    * self.beta_g_r1_shalf[i >> first_half]
                )
                self.add_mult_sum[u].b = (
                    self.add_mult_sum[u].b
                    + self.circuit_value[self.sumcheck_layer_id - 1][v] * tmp
                )
            elif ty == GateType.DirectRelay:
                tmp = (
                    self.beta_g_r0_fhalf[u & mask_fhalf]
                    * self.beta_g_r0_shalf[u >> first_half]
                    + self.beta_g_r1_fhalf[u & mask_fhalf]
                    * self.beta_g_r1_shalf[u >> first_half]
                )
                self.add_mult_sum[u] = self.add_mult_sum[u] + tmp
            elif ty == GateType.Relay:
                tmp = (
                    self.beta_g_r0_fhalf[i & mask_fhalf]
                    * self.beta_g_r0_shalf[i >> first_half]
                    + self.beta_g_r1_fhalf[i & mask_fhalf]
                    * self.beta_g_r1_shalf[i >> first_half]
                )
                self.add_mult_sum[u] = self.add_mult_sum[u] + tmp
        self.total_time += time.time() - start_timer

    def sumcheck_phase1_zk_initial_extension(
        self, previous_random: ModularInteger, ret: QuadraticPoly, current_bit: int
    ) -> QuadraticPoly:
        self.Iuv = self.Iuv * (self.one - previous_random)
        if current_bit > 0:
            self.maskR_sumcu = self.maskR_sumcu * (self.one - previous_random)
            self.maskR_sumcv = self.maskR_sumcv * (self.one - previous_random)
            self.Zu = self.Zu * (self.one - previous_random) * previous_random
        # the final polynomial will be evaluated at 0 and 1 during the sumcheck verification
        # if ret is a*x**2 + b*x + c, then adding the maskR_sumcu and maskR_sumcv terms to b and c
        # we have a*x**2 + (b - maskR_sumcu - maskR_sumcv)*x + c + maskR_sumcu + maskR_sumcv.
        # This will lead to ret(0) + ret(1)  a + b + 2*c + maskR_sumcu + maskR_sumcv, which is the
        # correct sumcheck polynomial evaluation for the current bit.
        ret.b = ret.b - self.maskR_sumcu - self.maskR_sumcv
        ret.c = ret.c + self.maskR_sumcu + self.maskR_sumcv

        tmp1 = self.maskpoly[current_bit << 1]
        tmp2 = self.maskpoly[(current_bit << 1) + 1]
        for i in range(self.length_u + self.length_v - current_bit):
            tmp1 = tmp1 + tmp1
            tmp2 = tmp2 + tmp2
        self.maskpoly_sumc = (self.maskpoly_sumc - tmp1 - tmp2) * self.inv_2
        tmp3: ModularInteger = self.zero
        if current_bit > 0:
            self.maskpoly_sumr = (
                self.maskpoly_sumr
                + self.maskpoly[(current_bit << 1) - 2]
                * previous_random
                * previous_random
                + self.maskpoly[(current_bit << 1) - 1] * previous_random
            )
            tmp3 = self.maskpoly_sumr
            for i in range(self.length_u + self.length_v - current_bit):
                tmp3 = tmp3 + tmp3
        ret.a = ret.a + tmp1
        ret.b = ret.b + tmp2
        ret.c = ret.c + self.maskpoly_sumc + tmp3

        return ret

    def sumcheck_phase1_zk_last_extension(
        self, previous_random: ModularInteger, ret: QuintuplePoly, current_bit: int
    ) -> QuintuplePoly:
        self.Iuv = self.Iuv * (self.one - previous_random)
        if current_bit > 0:
            self.maskR_sumcv = self.maskR_sumcv * (self.one - previous_random)
            self.maskR_sumcu = self.maskR_sumcu * (self.one - previous_random)
            self.Zu = self.Zu * (self.one - previous_random) * previous_random
        ret.b = ret.b - self.maskR_sumcu - self.maskR_sumcv
        ret.c = ret.c + self.maskR_sumcu + self.maskR_sumcv
        if current_bit == self.length_u - 1:
            a = self.sumRc.a
            b = self.sumRc.b
            c = self.sumRc.c
            d = self.add_mult_sum[0].a
            e = self.add_mult_sum[0].b
            ret.d = (self.zero - a) * d * self.Zu
            ret.e = (a * (d - e) - b * d) * self.Zu
            ret.f = (a * e + b * (d - e) - c * d) * self.Zu
            ret.a = ret.a + (c * (d - e) + b * e) * self.Zu
            ret.b = ret.b + c * e * self.Zu
        tmp1, tmp2, tmp4, tmp5, tmp6 = (
            self.zero,
            self.zero,
            self.zero,
            self.zero,
            self.zero,
        )
        tmp1 = self.maskpoly[current_bit << 1]
        tmp2 = self.maskpoly[(current_bit << 1) + 1]
        tmp4 = self.maskpoly[(((self.length_u + self.length_v + 1) << 1) + 1)]
        tmp5 = self.maskpoly[(((self.length_u + self.length_v + 1) << 1) + 2)]
        tmp6 = self.maskpoly[(((self.length_u + self.length_v + 1) << 1) + 3)]
        for i in range(self.length_u + self.length_v - current_bit):
            tmp1 = tmp1 + tmp1
            tmp2 = tmp2 + tmp2
            tmp4 = tmp4 + tmp4
            tmp5 = tmp5 + tmp5
            tmp6 = tmp6 + tmp6
        self.maskpoly_sumc = (
            self.maskpoly_sumc - tmp1 - tmp2 - tmp4 - tmp5 - tmp6
        ) * self.inv_2
        tmp3 = self.zero
        if current_bit > 0:
            self.maskpoly_sumr = (
                self.maskpoly_sumr
                + self.maskpoly[(current_bit << 1) - 2]
                * previous_random
                * previous_random
                + self.maskpoly[(current_bit << 1) - 1] * previous_random
            )
            tmp3 = self.maskpoly_sumr
            for i in range(self.length_u + self.length_v - current_bit):
                tmp3 = tmp3 + tmp3
        ret.a = ret.a + tmp1
        ret.b = ret.b + tmp2
        ret.c = ret.c + self.maskpoly_sumc + tmp3
        ret.d = ret.d + tmp4
        ret.e = ret.e + tmp5
        ret.f = ret.f + tmp6

        return QuintuplePoly(self.domain, ret.d, ret.e, ret.f, ret.a, ret.b, ret.c)

    def sumcheck_phase1_update(
        self, previous_random: ModularInteger, current_bit: int, last: bool
    ) -> Union[QuadraticPoly, QuintuplePoly]:
        start = time.time()
        if last:
            ret: QuintuplePoly = QuintuplePoly(self.domain)
        else:
            ret: QuadraticPoly = QuadraticPoly(self.domain)
        ret = self.sumcheck_update(ret, current_bit, previous_random)
        self.total_uv >>= 1
        if last:
            ret = self.sumcheck_phase1_zk_last_extension(
                previous_random=previous_random, ret=ret, current_bit=current_bit
            )
        else:
            ret = self.sumcheck_phase1_zk_initial_extension(
                previous_random=previous_random, ret=ret, current_bit=current_bit
            )
        self.total_time += time.time() - start
        return ret

    def sumcheck_phase2_init(
        self,
        previous_random: ModularInteger,
        r_u: List[ModularInteger],
        one_minus_r_u: List[ModularInteger],
    ):
        start_timer = time.time()

        self.preu1 = previous_random
        self.maskR_sumcu = self.maskR_sumcu * (self.one - previous_random)
        self.maskR_sumcv = self.maskR_sumcv * (self.one - previous_random)
        self.Iuv = self.Iuv * (self.one - previous_random)

        self.v_u = self.V_mult_add[0].eval(previous_random)

        self.Zu = self.Zu * (self.one - previous_random) * previous_random
        self.v_u = self.v_u + self.Zu * self.sumRc.eval(previous_random)

        first_half = self.length_u >> 1
        second_half = self.length_u - first_half

        self.beta_u_fhalf[0] = self.one
        self.beta_u_shalf[0] = self.one
        for i in range(first_half):
            for j in range(1 << i):
                self.beta_u_fhalf[j | (1 << i)] = self.beta_u_fhalf[j] * r_u[i]
                self.beta_u_fhalf[j] = self.beta_u_fhalf[j] * one_minus_r_u[i]
        for i in range(second_half):
            for j in range(1 << i):
                self.beta_u_shalf[j | (1 << i)] = (
                    self.beta_u_shalf[j] * r_u[i + first_half]
                )
                self.beta_u_shalf[j] = (
                    self.beta_u_shalf[j] * one_minus_r_u[i + first_half]
                )
        mask_fhalf = (1 << first_half) - 1
        for i in range(1 << self.length_u):
            self.beta_u[i] = (
                self.beta_u_fhalf[i & mask_fhalf] * self.beta_u_shalf[i >> first_half]
            )
        self.total_uv = 1 << self.C.circuit[self.sumcheck_layer_id - 1].bitLength
        self.total_g = 1 << self.C.circuit[self.sumcheck_layer_id].bitLength
        for i in range(self.total_uv):
            self.add_mult_sum[i] = LinearPoly(self.domain)
            self.addV_array[i] = LinearPoly(self.domain)
            self.V_mult_add[i] = LinearPoly(
                self.domain, b=self.circuit_value[self.sumcheck_layer_id - 1][i]
            )
        first_g_half = self.length_g >> 1
        mask_g_fhalf = (1 << first_g_half) - 1
        for i in range(self.total_g):
            info = self.C.circuit[self.sumcheck_layer_id].gates[i]
            u = info.u
            v = info.v
            ty = info.ty
            if ty == GateType.Add:
                tmp_u = (
                    self.beta_u_fhalf[u & mask_fhalf]
                    * self.beta_u_shalf[u >> first_half]
                )
                tmp_g = (
                    self.beta_g_r0_fhalf[i & mask_g_fhalf]
                    * self.beta_g_r0_shalf[i >> first_g_half]
                    + self.beta_g_r1_fhalf[i & mask_g_fhalf]
                    * self.beta_g_r1_shalf[i >> first_g_half]
                )
                self.add_mult_sum[v].b = self.add_mult_sum[v].b + tmp_g * tmp_u
                self.addV_array[v].b = self.addV_array[v].b + (tmp_g * tmp_u) * self.v_u
            elif ty == GateType.Mul:
                tmp_u = (
                    self.beta_u_fhalf[u & mask_fhalf]
                    * self.beta_u_shalf[u >> first_half]
                )
                tmp_g = (
                    self.beta_g_r0_fhalf[i & mask_g_fhalf]
                    * self.beta_g_r0_shalf[i >> first_g_half]
                    + self.beta_g_r1_fhalf[i & mask_g_fhalf]
                    * self.beta_g_r1_shalf[i >> first_g_half]
                )
                self.add_mult_sum[v].b = (
                    self.add_mult_sum[v].b + (tmp_g * tmp_u) * self.v_u
                )
            elif ty == GateType.Relay:
                tmp_u = (
                    self.beta_u_fhalf[u & mask_fhalf]
                    * self.beta_u_shalf[u >> first_half]
                )
                tmp_g = (
                    self.beta_g_r0_fhalf[i & mask_g_fhalf]
                    * self.beta_g_r0_shalf[i >> first_g_half]
                    + self.beta_g_r1_fhalf[i & mask_g_fhalf]
                    * self.beta_g_r1_shalf[i >> first_g_half]
                )
                self.addV_array[v].b = self.addV_array[v].b + tmp_g * tmp_u * self.v_u

        self.maskpoly_sumr = (
            self.maskpoly_sumr
            + self.maskpoly[self.length_u * 2 - 2] * previous_random * previous_random
            + self.maskpoly[self.length_u * 2 - 1] * previous_random
        )
        self.maskpoly_sumr = (
            self.maskpoly_sumr
            + self.maskpoly[(self.length_u + self.length_v + 1) * 2 + 1]
            * previous_random
            * previous_random
            * previous_random
            * previous_random
            * previous_random
        )
        self.maskpoly_sumr = (
            self.maskpoly_sumr
            + self.maskpoly[(self.length_u + self.length_v + 1) * 2 + 2]
            * previous_random
            * previous_random
            * previous_random
            * previous_random
        )
        self.maskpoly_sumr = (
            self.maskpoly_sumr
            + self.maskpoly[(self.length_u + self.length_v + 1) * 2 + 3]
            * previous_random
            * previous_random
            * previous_random
        )
        self.total_time += time.time() - start_timer

    def sumcheck_phase2_zk_initial_extension(
        self, previous_random: ModularInteger, ret: QuadraticPoly, current_bit: int
    ) -> QuadraticPoly:
        if current_bit > 0:
            self.Iuv = self.Iuv * (self.one - previous_random)
        if current_bit > 0:
            self.maskR_sumcu = self.maskR_sumcu * (self.one - previous_random)
            self.maskR_sumcv = self.maskR_sumcv * (self.one - previous_random)
            self.Zv = self.Zv * (self.one - previous_random) * previous_random
        ret.b = ret.b - self.maskR_sumcu - self.maskR_sumcv
        ret.c = ret.c + self.maskR_sumcu + self.maskR_sumcv

        current = current_bit + self.length_u
        tmp1, tmp2 = self.zero, self.zero
        tmp1 = self.maskpoly[current << 1]
        tmp2 = self.maskpoly[(current << 1) + 1]
        for i in range(self.length_u + self.length_v - current):
            tmp1 = tmp1 + tmp1
            tmp2 = tmp2 + tmp2
        self.maskpoly_sumc = (self.maskpoly_sumc - tmp1 - tmp2) * self.inv_2
        self.maskpoly_sumr = (
            self.maskpoly_sumr
            + self.maskpoly[(current << 1) - 2] * previous_random * previous_random
            + self.maskpoly[(current << 1) - 1] * previous_random
        )
        tmp3 = self.maskpoly_sumr
        for i in range(self.length_u + self.length_v - current):
            tmp3 = tmp3 + tmp3

        ret.a = ret.a + tmp1
        ret.b = ret.b + tmp2
        ret.c = ret.c + self.maskpoly_sumc + tmp3
        return ret

    def sumcheck_phase2_zk_last_extension(
        self, previous_random: ModularInteger, ret: QuintuplePoly, current_bit: int
    ) -> QuintuplePoly:
        self.Iuv = self.Iuv * (self.one - previous_random)
        if current_bit > 0:
            self.maskR_sumcu = self.maskR_sumcu * (self.one - previous_random)

            self.maskR_sumcv = self.maskR_sumcv * (self.one - previous_random)
            self.Zv = self.Zv * (self.one - previous_random) * previous_random
        ret.b = ret.b - self.maskR_sumcu - self.maskR_sumcv
        ret.c = ret.c + self.maskR_sumcu + self.maskR_sumcv

        if current_bit == self.length_v - 1:
            a = self.sumRc.a
            b = self.sumRc.b
            c = self.sumRc.c
            d = self.add_mult_sum[0].a
            e = self.add_mult_sum[0].b
            ret.d = (self.zero - a) * d * self.Zv
            ret.e = (a * (d - e) - b * d) * self.Zv
            ret.f = (a * e + b * (d - e) - c * d) * self.Zv
            ret.a = ret.a + (c * (d - e) + b * e) * self.Zv
            ret.b = ret.b + c * e * self.Zv

        current = current_bit + self.length_u
        tmp1, tmp2, tmp4, tmp5, tmp6 = (
            self.zero,
            self.zero,
            self.zero,
            self.zero,
            self.zero,
        )
        tmp1 = self.maskpoly[current << 1]
        tmp2 = self.maskpoly[(current << 1) + 1]
        tmp4 = self.maskpoly[(self.length_u + self.length_v + 1) * 2 + 4]
        tmp5 = self.maskpoly[(self.length_u + self.length_v + 1) * 2 + 5]
        tmp6 = self.maskpoly[(self.length_u + self.length_v + 1) * 2 + 6]
        for i in range(self.length_u + self.length_v - current):
            tmp1 = tmp1 + tmp1
            tmp2 = tmp2 + tmp2
            tmp4 = tmp4 + tmp4
            tmp5 = tmp5 + tmp5
            tmp6 = tmp6 + tmp6
        self.maskpoly_sumc = (
            self.maskpoly_sumc - tmp1 - tmp2 - tmp4 - tmp5 - tmp6
        ) * self.inv_2
        self.maskpoly_sumr = (
            self.maskpoly_sumr
            + self.maskpoly[(current << 1) - 2] * previous_random * previous_random
            + self.maskpoly[(current << 1) - 1] * previous_random
        )
        tmp3 = self.maskpoly_sumr
        for i in range(self.length_u + self.length_v - current):
            tmp3 = tmp3 + tmp3
        ret.d = ret.d + tmp4
        ret.e = ret.e + tmp5
        ret.f = ret.f + tmp6
        ret.a = ret.a + tmp1
        ret.b = ret.b + tmp2
        ret.c = ret.c + self.maskpoly_sumc + tmp3
        return QuintuplePoly(self.domain, ret.d, ret.e, ret.f, ret.a, ret.b, ret.c)

    def sumcheck_phase2_update(
        self, previous_random: ModularInteger, current_bit: int, last: bool
    ) -> Union[QuadraticPoly, QuintuplePoly]:
        start_timer = time.time()
        if last:
            ret: QuintuplePoly = QuintuplePoly(self.domain)
        else:
            ret: QuadraticPoly = QuadraticPoly(self.domain)
        ret = self.sumcheck_update(ret, current_bit, previous_random)
        self.total_uv >>= 1
        if last:
            ret = self.sumcheck_phase2_zk_last_extension(
                previous_random=previous_random, ret=ret, current_bit=current_bit
            )
        else:
            ret = self.sumcheck_phase2_zk_initial_extension(
                previous_random=previous_random, ret=ret, current_bit=current_bit
            )
        self.total_time += time.time() - start_timer
        return ret

    def sumcheck_final_round(
        self,
        previous_random: ModularInteger,
        current: int,
        general_value: ModularInteger,
    ) -> QuadraticPoly:
        ret = QuadraticPoly(self.domain)
        ret.a = (
            self.Iuv * self.preZu * self.Rg1.a * self.alpha
            + self.Iuv * self.preZv * self.Rg2.a * self.beta
        )
        ret.b = (
            self.Iuv * self.preZu * self.Rg1.b * self.alpha
            + self.Iuv * self.preZv * self.Rg2.b * self.beta
            + general_value
        )
        ret.c = (
            self.Iuv * self.preZu * self.Rg1.c * self.alpha
            + self.Iuv * self.preZv * self.Rg2.c * self.beta
        )
        tmp1 = self.maskpoly[current << 1]
        tmp2 = self.maskpoly[(current << 1) + 1]
        for i in range(self.length_u + self.length_v - current):
            tmp1 = tmp1 + tmp1
            tmp2 = tmp2 + tmp2
        self.maskpoly_sumc = (self.maskpoly_sumc - tmp1 - tmp2) * self.inv_2
        self.maskpoly_sumr = (
            self.maskpoly_sumr
            + self.maskpoly[(current << 1) - 2] * previous_random * previous_random
            + self.maskpoly[(current << 1) - 1] * previous_random
        )
        self.maskpoly_sumr = (
            self.maskpoly_sumr
            + self.maskpoly[(self.length_u + self.length_v + 1) * 2 + 4]
            * previous_random
            * previous_random
            * previous_random
            * previous_random
            * previous_random
        )
        self.maskpoly_sumr = (
            self.maskpoly_sumr
            + self.maskpoly[(self.length_u + self.length_v + 1) * 2 + 5]
            * previous_random
            * previous_random
            * previous_random
            * previous_random
        )
        self.maskpoly_sumr = (
            self.maskpoly_sumr
            + self.maskpoly[(self.length_u + self.length_v + 1) * 2 + 6]
            * previous_random
            * previous_random
            * previous_random
        )
        tmp3 = self.maskpoly_sumr
        for i in range(self.length_u + self.length_v - current):
            tmp3 = tmp3 + tmp3
        ret.a = ret.a + tmp1
        ret.b = ret.b + tmp2
        ret.c = ret.c + self.maskpoly_sumc + tmp3
        return ret

    def sumcheck_finalize(
        self, previous_random: ModularInteger
    ) -> Tuple[ModularInteger, ModularInteger]:
        self.prev1 = previous_random
        self.Iuv = self.Iuv * (self.one - previous_random)
        self.v_v = self.V_mult_add[0].eval(previous_random)
        self.Zv = self.Zv * (self.one - previous_random) * previous_random
        self.v_v = self.v_v + self.Zv * self.sumRc.eval(previous_random)
        return (self.v_u, self.v_v)

    def random(self) -> ModularInteger:
        return ModularInteger.random()

    def keygen_and_commit(self, input_bit_length: int, key_gen_time: float):
        self.input_mpz = [self.zero] * ((1 << input_bit_length) + 1)
        for i in range(1 << input_bit_length):
            gate = self.C.circuit[0].gates[i]
            ty = gate.ty
            u = gate.u
            if ty == GateType.Input:
                self.input_mpz[i] = u
            else:
                assert False, "Invalid gate type, must be input"
        self.maskr = [self.domain.zero] * 2
        self.maskr[0] = self.random()
        self.maskr[1] = self.random()
        self.maskr_mpz = [self.zero] * 2
        for i in range(2):
            self.maskr_mpz[i] = int(self.maskr[i]) % self.domain.characteristic()

    def generate_maskR(self, layer_id: int):
        maskR_gmp = []
        for i in range(6):
            maskR_gmp.append(self.maskR[i])
        self.prepreu1 = self.preu1
        self.preprev1 = self.prev1

        for i in range(6):
            self.preR[i] = self.maskR[i]
        self.Rg1.a = self.maskR[4]
        self.Rg1.b = self.maskR[3] + self.maskR[5] * self.preu1
        self.Rg1.c = (
            self.maskR[0]
            + self.maskR[1] * self.preu1
            + self.maskR[2] * self.preu1 * self.preu1
        )

        self.Rg2.a = self.maskR[4]
        self.Rg2.b = self.maskR[3] + self.maskR[5] * self.prev1
        self.Rg2.c = (
            self.maskR[0]
            + self.maskR[1] * self.prev1
            + self.maskR[2] * self.prev1 * self.prev1
        )
        self.sumRu = self.Rg1.a + self.Rg1.b + self.Rg1.c + self.Rg1.c
        self.sumRv = self.Rg2.a + self.Rg2.b + self.Rg2.c + self.Rg2.c

        self.maskR_sumcu = self.alpha * self.Zu * self.sumRu
        self.maskR_sumcv = self.beta * self.Zv * self.sumRv

        self.preZu = self.Zu
        self.preZv = self.Zv
        self.Zu = self.one
        self.Zv = self.one
        self.Iuv = self.one
        if layer_id > 1:
            for i in range(6):
                self.maskR[i] = self.random()
            self.sumRc.a = self.maskR[2] + self.maskR[2]
            self.sumRc.b = self.maskR[1] + self.maskR[1] + self.maskR[5]
            self.sumRc.c = self.maskR[0] + self.maskR[0] + self.maskR[3] + self.maskR[4]
        if layer_id == 1:
            self.maskR[0] = self.maskr[0]
            self.maskR[1] = self.maskr[1]
            self.sumRc.a = self.domain.zero
            self.sumRc.b = self.maskR[1]
            self.sumRc.c = self.maskR[0]

    def generate_maskpoly_pre_rho(self, length: int, degree: int):
        self.maskpoly = [self.zero] * (length * degree + 1 + 6)
        for i in range(length * degree + 1 + 6):
            self.maskpoly[i] = self.random()

        self.maskpoly_gmp = [0] * (length * degree + 1 + 6)
        for i in range(length * degree + 7):
            self.maskpoly_gmp[i] = int(self.maskpoly[i]) % self.domain.characteristic()

    def generate_maskpoly_after_rho(self, length: int, degree: int):
        for i in range(length * degree + 1 + 6):
            self.maskpoly[i] = self.maskpoly[i] * self.rho
        self.maskpoly_sumc = self.maskpoly[length * degree]
        for i in range(length * degree):
            self.maskpoly_sumc = self.maskpoly_sumc + self.maskpoly[i]
        for i in range(6):
            self.maskpoly_sumc = self.maskpoly_sumc + self.maskpoly[length * degree + i]

        for i in range(length):
            self.maskpoly_sumc = self.maskpoly_sumc + self.maskpoly_sumc

        self.maskpoly_sumr = self.zero

    def read_circuit(self):
        d = self.C.size
        max_bit_length = 0
        for i in range(d):
            if self.C.circuit[i].bitLength > max_bit_length:
                max_bit_length = self.C.circuit[i].bitLength
        self.init_array(max_bit_length)
        self.beta_g_r0 = [self.domain.zero] * (1 << max_bit_length)
        self.beta_g_r1 = [self.domain.zero] * (1 << max_bit_length)
        self.beta_u = [self.domain.zero] * (1 << max_bit_length)
        self.beta_v = [self.domain.zero] * (1 << max_bit_length)

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
                    self.domain.one - r_g[i] - r_u[i] + self.two * r_g[i] * r_u[i]
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

    def beta_init(
        self,
        depth: int,
        alpha: ModularInteger,
        beta: ModularInteger,
        r_0: List[ModularInteger],
        r_1: List[ModularInteger],
        r_u: List[ModularInteger],
        r_v: List[ModularInteger],
        one_minus_r_0: List[ModularInteger],
        one_minus_r_1: List[ModularInteger],
        one_minus_r_u: List[ModularInteger],
        one_minus_r_v: List[ModularInteger],
    ):
        self.beta_g_r0[0] = alpha
        self.beta_g_r1[0] = beta
        for i in range(self.C.circuit[depth].bitLength):
            for j in range(1 << i):
                self.beta_g_r0[j | (1 << i)] = self.beta_g_r0[j] * r_0[i]
                self.beta_g_r1[j | (1 << i)] = self.beta_g_r1[j] * r_1[i]
            for j in range(1 << i):
                self.beta_g_r0[j] = self.beta_g_r0[j] * one_minus_r_0[i]
                self.beta_g_r1[j] = self.beta_g_r1[j] * one_minus_r_1[i]
        self.beta_u[0] = self.domain.one
        self.beta_v[0] = self.domain.one
        for i in range(self.C.circuit[depth - 1].bitLength):
            for j in range(1 << i):
                self.beta_u[j | (1 << i)] = self.beta_u[j] * r_u[i]
                self.beta_v[j | (1 << i)] = self.beta_v[j] * r_v[i]
            for j in range(1 << i):
                self.beta_u[j] = self.beta_u[j] * one_minus_r_u[i]
                self.beta_v[j] = self.beta_v[j] * one_minus_r_v[i]

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
            output[i] = ModularInteger(output_raw[i], False)
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
            last = j == self.C.circuit[i - 1].bitLength - 1
            poly = self.sumcheck_phase1_update(
                previous_random=previous_random, current_bit=j, last=last
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
        direct_relay_value: ModularInteger,
        i: int,
    ):
        previous_random = self.domain.zero
        for j in range(previous_bit_len):
            last = j == self.C.circuit[i - 1].bitLength - 1
            poly = self.sumcheck_phase2_update(
                previous_random=previous_random, current_bit=j, last=last
            )
            self.transcript.append_sympy_ff_list(b"phase_2", poly.coefficients())
            previous_random = self.r_v[j]
            self.transcript.append_sympy_ff(b"v_u", direct_relay_value * self.v_u)
            claim = (
                (poly.eval(self.zero) + poly.eval(self.one)) != alpha_beta_sum
                if j == 0
                else (
                    poly.eval(self.zero)
                    + poly.eval(self.one)
                    + direct_relay_value * self.v_u
                )
                != alpha_beta_sum
            )
            if claim:
                (poly.eval(self.zero) + poly.eval(self.one)) != alpha_beta_sum
                assert False, f"Verification fail, phase 2, circuit {i}, bit {j}"
            alpha_beta_sum = poly.eval(self.r_v[j]) + direct_relay_value * self.v_u
        return alpha_beta_sum, previous_random

    def verify_gkr_round(
        self, previous_random, alpha_beta_sum, i, alpha, beta, direct_relay_value, r_c
    ):
        self.v_u, self.v_v = self.sumcheck_finalize(previous_random)
        self.transcript.append_sympy_ff(b"v_u", self.v_u)
        self.transcript.append_sympy_ff(b"v_v", self.v_v)
        self.beta_init(
            i,
            alpha=alpha,
            beta=beta,
            r_0=self.r_0,
            r_1=self.r_1,
            r_u=self.r_u,
            r_v=self.r_v,
            one_minus_r_0=self.one_minus_r_0,
            one_minus_r_1=self.one_minus_r_1,
            one_minus_r_u=self.one_minus_r_u,
            one_minus_r_v=self.one_minus_r_v,
        )
        mult_value = self.mult(i)
        add_value = self.add(i)
        relay_value = self.relay_gate(i)
        correct_output = (
            add_value * (self.v_u + self.v_v)
            + mult_value * self.v_u * self.v_v
            + direct_relay_value * self.v_u
            + relay_value * self.v_u
        )
        poly = self.sumcheck_final_round(
            previous_random=previous_random,
            current=self.C.circuit[i - 1].bitLength << 1,
            general_value=correct_output,
        )
        self.transcript.append_sympy_ff_list(b"final_gkr_round", poly.coefficients())
        self.transcript.append_sympy_ff(b"v_u_direct_relay", direct_relay_value)
        claim = (
            poly.eval(self.zero) + poly.eval(self.one)
            if i == 1
            else poly.eval(self.zero)
            + poly.eval(self.one)
            + direct_relay_value * self.v_u
        )
        if alpha_beta_sum != claim:
            assert False, f"Verification fail, circuit {i}"
        self.alpha = self.generate_randomness(size=1, label="alpha")[0]
        self.beta = self.generate_randomness(size=1, label="beta")[0]
        if i != 1:
            alpha_beta_sum = alpha * self.v_u + beta * self.v_v
        else:
            alpha_beta_sum = self.v_u
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
        input_0 = self.V_in(
            self.r_0,
            self.one_minus_r_0,
            input,
            self.C.circuit[0].bitLength,
            1 << self.C.circuit[0].bitLength,
        )
        input_0 = input_0 + self.Zu * self.sumRc.eval(self.preu1)
        self.transcript.append_sympy_ff(b"input", input_0)
        if alpha_beta_sum != input_0:
            assert False, "Verification fail, final input check fail"
        return alpha_beta_sum

    def prove(self):
        self.read_circuit()
        self.evaluate()
        self.keygen_and_commit(self.C.circuit[0].bitLength, 0)

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
        a_0 = self.V_res(
            one_minus_r_0=self.one_minus_r_0,
            r_0=self.r_0,
            output_raw=self.circuit_value[self.C.total_depth - 1],
            r_0_size=bit_len,
            output_size=1 << bit_len,
        )
        a_0 = alpha * a_0
        alpha_beta_sum = a_0
        direct_relay_value = self.domain.zero
        for i in list(reversed(range(1, self.C.total_depth))):
            current_bit_len = self.C.circuit[i].bitLength
            previous_bit_len = self.C.circuit[i - 1].bitLength
            rho = self.generate_randomness(size=1, label="rho")[0]
            self.sumcheck_init(
                i,
                current_bit_len,
                previous_bit_len,
                previous_bit_len,
                alpha,
                beta,
                self.r_0,
                self.r_1,
                self.one_minus_r_0,
                self.one_minus_r_1,
            )
            self.generate_maskpoly_pre_rho(previous_bit_len * 2 + 1, 2)
            self.rho = rho
            self.generate_maskpoly_after_rho(previous_bit_len * 2 + 1, 2)

            alpha_beta_sum = alpha_beta_sum + self.maskpoly_sumc
            if not hasattr(alpha_beta_sum, "val"):
                pass
            self.transcript.append_sympy_ff(b"alpha_beta_sum", alpha_beta_sum)
            self.sumcheck_phase1_init()
            previous_random = self.domain.zero
            self.r_u = self.generate_randomness(size=previous_bit_len, label="r_u")
            self.r_v = self.generate_randomness(size=previous_bit_len, label="r_v")
            direct_relay_value = alpha * self.direct_relay(
                i, self.r_0, self.r_u
            ) + beta * self.direct_relay(i, self.r_1, self.r_u)
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
            self.sumcheck_phase2_init(
                previous_random=previous_random,
                r_u=self.r_u,
                one_minus_r_u=self.one_minus_r_u,
            )
            previous_random = self.domain.zero
            alpha_beta_sum, previous_random = self.verify_phase_2(
                previous_random=previous_random,
                alpha_beta_sum=alpha_beta_sum,
                previous_bit_len=previous_bit_len,
                direct_relay_value=direct_relay_value,
                i=i,
            )

            alpha_beta_sum = self.verify_gkr_round(
                previous_random=previous_random,
                alpha_beta_sum=alpha_beta_sum,
                i=i,
                alpha=alpha,
                beta=beta,
                direct_relay_value=direct_relay_value,
                r_c=r_c,
            )
        self.verify_input(alpha_beta_sum)
        return True
