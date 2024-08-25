# Code extracted from the https://github.com/NOOMA-42/pylookup/tree/main/src/plookup repository


from zkgraph.transcript.merlin.strobe import Strobe128

MERLIN_PROTOCOL_LABEL = b"Merlin v1.0"


class MerlinTranscript:
    def __init__(self, label: bytes) -> None:
        self.strobe: Strobe128 = Strobe128.new(MERLIN_PROTOCOL_LABEL)
        self.append_message(b"dom-sep", label)

    def append_message(self, label: bytes, message: bytes) -> None:
        data_len = len(message).to_bytes(4, "little")
        self.strobe.meta_ad(label, False)
        self.strobe.meta_ad(data_len, True)
        self.strobe.ad(message, False)

    def append_u64(self, label: bytes, x: int) -> None:
        self.append_message(label, x.to_bytes(8, "little"))

    def challenge_bytes(self, label: bytes, length: int) -> bytes:
        data_len = length.to_bytes(4, "little")
        self.strobe.meta_ad(label, False)
        self.strobe.meta_ad(data_len, True)
        return self.strobe.prf(length, False)
