# Code extracted from the https://github.com/NOOMA-42/pylookup/tree/main/src/plookup repository


from typing import Type, TypeVar
from zkgraph.transcript.merlin.keccak import KeccakF1600

STROBE_R = 166

FLAG_I = 1
FLAG_A = 1 << 1
FLAG_C = 1 << 2
FLAG_T = 1 << 3
FLAG_M = 1 << 4
FLAG_K = 1 << 5

T_Strobe128 = TypeVar("T_Strobe128", bound="Strobe128")


class Strobe128:
    def __init__(self, state: bytearray, pos: int, pos_begin: int, cur_flags: int):
        self.state = state
        self.pos = pos
        self.pos_begin = pos_begin
        self.cur_flags = cur_flags

    @classmethod
    def new(cls: Type[T_Strobe128], protocol_label: bytes) -> T_Strobe128:
        state = bytearray(200)
        state[0:6] = bytes([1, STROBE_R + 2, 1, 0, 1, 96])
        state[6:18] = b"STROBEv1.0.2"
        state = KeccakF1600(state)

        strobe = cls(state, 0, 0, 0)
        strobe.meta_ad(protocol_label, False)

        # print("init state hex", strobe.state.hex())

        return strobe

    def meta_ad(self, data: bytes, more: bool):
        self.begin_op(FLAG_M | FLAG_A, more)
        # print("cur data post begin op ", data, " state ", self.state.hex(), " pos ", self.pos, " pos_begin ", self.pos_begin, " cur_flags ", self.cur_flags)
        self.absorb(data)
        # print("cur data ", data, " state ", self.state.hex(), " pos ", self.pos, " pos_begin ", self.pos_begin, " cur_flags ", self.cur_flags)

    def ad(self, data: bytes, more: bool):
        self.begin_op(FLAG_A, more)
        self.absorb(data)

    def prf(self, data_len: int, more: bool):
        self.begin_op(FLAG_I | FLAG_A | FLAG_C, more)
        return self.squeeze(data_len)

    def key(self, data: bytes, more: bool):
        self.begin_op(FLAG_A | FLAG_C, more)
        self.overwrite(data)

    def run_f(self):
        self.state[self.pos] ^= self.pos_begin
        self.state[(self.pos + 1)] ^= int(0x04)
        self.state[(STROBE_R + 1)] ^= int(0x80)
        self.state = KeccakF1600(self.state)
        self.pos = 0
        self.pos_begin = 0

    def absorb(self, data: bytes):
        for b in data:
            self.state[self.pos] ^= b
            self.pos += 1
            if self.pos == STROBE_R:
                self.run_f()

    def overwrite(self, data: bytes):
        for b in data:
            self.state[self.pos] = b
            self.pos += 1
            if self.pos == STROBE_R:
                self.run_f()

    def squeeze(self, data_len: int):
        data = bytearray(data_len)
        for i in range(data_len):
            # print("squeeze", i, self.pos, self.state[self.pos])
            data[i] = self.state[self.pos]
            self.state[self.pos] = 0
            self.pos += 1
            if self.pos == STROBE_R:
                self.run_f()

        return data

    def begin_op(self, flags: int, more: bool):
        if more:
            assert self.cur_flags == flags
            return

        assert flags & FLAG_T == 0

        old_begin = self.pos_begin
        self.pos_begin = self.pos + 1
        self.cur_flags = flags

        # print("pre absorb hex", self.state.hex())
        self.absorb(bytes([old_begin, flags]))
        # print("post absorb hex", self.state.hex())

        force_f = (flags & (FLAG_C | FLAG_K)) != 0

        if force_f and self.pos != 0:
            self.run_f()
