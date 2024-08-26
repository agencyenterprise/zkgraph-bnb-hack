from py_ecc.optimized_bls12_381.optimized_curve import (
    G1,
    G2,
    multiply as ecc_multiply,
    add as ecc_add,
    is_on_curve,
    curve_order,
    FQ,
    FQ2,
    neg as ecc_negate,
)
from py_ecc.optimized_bls12_381.optimized_pairing import pairing


from collections.abc import MutableMapping
from enum import Enum


class PPType(Enum):
    EXPONENTIAL = 1  # Base implementation (Used for random polynomial R) Usefull when the number of variables is small
    LINEAR = (
        2  # Linear (Used for generating powers of tau for the zk sumcheck polynomial)
    )


class PPStore(MutableMapping):
    pp_type: PPType

    def __init__(self, *args, **kwargs):
        self.store = dict()
        self.pp_type = PPType.EXPONENTIAL
        if kwargs.get("pp_type"):
            self.pp_type = kwargs.get("pp_type")
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
                "Wrong key {} Ptau key can hold up to {} values".format(
                    key, len(variables_0)
                )
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


TG2P = tuple[FQ2, PPStore]
TG1P = tuple[FQ, PPStore]
TPP = tuple[TG2P, TG2P]
