"""Builds a tiny real ONNX classifier by hand (protobuf wire format, no `onnx` package).

Graph: input[1,3,S,S] -> ReduceMean(axes 2,3) -> [1,3] -> MatMul(W[3,N]) -> logits[1,N]
where only W[channel, peak_class] is non-zero, so the model predicts `peak_class`
whenever the chosen *RGB* channel of the normalised input is strongly positive.
"""

import struct
from pathlib import Path


def _varint(value: int) -> bytes:
    value &= (1 << 64) - 1
    out = bytearray()
    while True:
        byte = value & 0x7F
        value >>= 7
        out.append(byte | (0x80 if value else 0))
        if not value:
            return bytes(out)


def _field(number: int, wire: int, payload: bytes) -> bytes:
    return _varint(number << 3 | wire) + payload


def _int(number: int, value: int) -> bytes:
    return _field(number, 0, _varint(value))


def _bytes(number: int, data: bytes) -> bytes:
    return _field(number, 2, _varint(len(data)) + data)


def _str(number: int, text: str) -> bytes:
    return _bytes(number, text.encode())


def _attr_ints(name: str, values: list[int]) -> bytes:
    body = _str(1, name) + b"".join(_int(8, v) for v in values) + _int(20, 7)
    return _bytes(5, body)


def _attr_int(name: str, value: int) -> bytes:
    return _bytes(5, _str(1, name) + _int(3, value) + _int(20, 2))


def _node(op: str, inputs: list[str], outputs: list[str], attrs: bytes = b"") -> bytes:
    body = b"".join(_str(1, i) for i in inputs) + b"".join(_str(2, o) for o in outputs)
    return _bytes(1, body + _str(4, op) + attrs)


def _value_info(number: int, name: str, dims: list[int]) -> bytes:
    shape = b"".join(_bytes(1, _int(1, d)) for d in dims)
    tensor_type = _int(1, 1) + _bytes(2, shape)
    return _bytes(number, _str(1, name) + _bytes(2, _bytes(1, tensor_type)))


def _initializer(name: str, dims: list[int], values: list[float]) -> bytes:
    raw = struct.pack(f"<{len(values)}f", *values)
    body = b"".join(_int(1, d) for d in dims) + _int(2, 1) + _str(8, name) + _bytes(9, raw)
    return _bytes(5, body)


def build_onnx_bytes(num_classes: int, peak_class: int, channel: int, input_size: int = 224, scale: float = 40.0) -> bytes:
    """Serialised ONNX model that predicts `peak_class` when RGB `channel` is bright."""
    weights = [0.0] * (3 * num_classes)
    weights[channel * num_classes + peak_class] = scale
    graph = (
        _node("ReduceMean", ["input"], ["pooled"], _attr_ints("axes", [2, 3]) + _attr_int("keepdims", 0))
        + _node("MatMul", ["pooled", "W"], ["logits"])
        + _str(2, "tiny_classifier")
        + _initializer("W", [3, num_classes], weights)
        + _value_info(11, "input", [1, 3, input_size, input_size])
        + _value_info(12, "logits", [1, num_classes])
    )
    opset = _str(1, "") + _int(2, 13)
    return _int(1, 7) + _str(2, "tests") + _bytes(7, graph) + _bytes(8, opset)


def write_onnx(path: Path, num_classes: int, peak_class: int, channel: int = 0) -> None:
    path.write_bytes(build_onnx_bytes(num_classes, peak_class, channel))
