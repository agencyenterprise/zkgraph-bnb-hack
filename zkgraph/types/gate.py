from enum import Enum


class GateType(Enum):
    Mul = 1
    Add = 2
    Sub = 3
    AntiSub = 4
    Naab = 5
    AntiNaab = 6
    Input = 7
    Mulc = 8
    Addc = 9
    Xor = 10
    Not = 11
    Copy = 12
    SIZE = 13
    Relay = 14
    DirectRelay = 15
