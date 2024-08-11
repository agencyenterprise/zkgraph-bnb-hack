from typing import List
from abc import ABC, abstractmethod

LayerList: List[List["BaseValue"]] = []


class BaseValue(ABC):
    """stores a single scalar value and its gradient"""

    @abstractmethod
    def compute_layer_id(
        self, left: "BaseValue", right: "BaseValue", output: "BaseValue"
    ):
        pass

    @abstractmethod
    def get_layers(self):
        pass

    @abstractmethod
    def set_layer_element(self, layer_id: int, element: "BaseValue"):
        pass

    @abstractmethod
    def delete_layer_element(self, layer_id: int, element: "BaseValue"):
        pass

    @abstractmethod
    def __add__(self, other: "BaseValue"):
        pass

    @abstractmethod
    def __mul__(self, other: "BaseValue"):
        pass

    @abstractmethod
    def __pow__(self, other: "BaseValue"):
        pass

    @abstractmethod
    def tanh(self):
        pass

    @abstractmethod
    def exp(self):
        pass

    @abstractmethod
    def log(self):
        pass

    @abstractmethod
    def relu(self):
        pass

    @abstractmethod
    def __neg__(self):  # -self
        pass

    @abstractmethod
    def __radd__(self, other: "BaseValue"):  # other + self
        pass

    @abstractmethod
    def __sub__(self, other: "BaseValue"):  # self - other
        pass

    @abstractmethod
    def __rsub__(self, other: "BaseValue"):  # other - self
        pass

    @abstractmethod
    def __rmul__(self, other: "BaseValue"):  # other * self
        pass

    @abstractmethod
    def __truediv__(self, other: "BaseValue"):  # self / other
        pass

    def __rtruediv__(self, other):  # other / self
        return other * self**-1

    def __repr__(self):
        return f"Value(data={self.data}, grad={self.grad})"

    @staticmethod
    def to_circuit(output: "BaseValue", debug: bool = False):
        raise NotImplementedError("Not implemented yet")

    @staticmethod
    def compile_layered_circuit(output: "BaseValue", debug: bool = False):
        raise NotImplementedError("Not implemented yet")

    @staticmethod
    def proprocess_circuit(output: "BaseValue", debug: bool = False):
        raise NotImplementedError("Not implemented yet")
