"""Build the deterministic tiny ONNX GPU probe with only the Python standard library.

The graph is deliberately small and uses MatMul, Add and Relu so that the
browser can exercise a static WebGPU execution path without shipping a
training dependency or claiming gaze accuracy.
"""

from __future__ import annotations

import struct
from pathlib import Path


HERE = Path(__file__).parent


def varint(value: int) -> bytes:
    if value < 0:
        value += 1 << 64
    output = bytearray()
    while value > 0x7F:
        output.append((value & 0x7F) | 0x80)
        value >>= 7
    output.append(value)
    return bytes(output)


def field(number: int, wire_type: int, value: bytes) -> bytes:
    return varint((number << 3) | wire_type) + value


def integer(number: int, value: int) -> bytes:
    return field(number, 0, varint(value))


def text(number: int, value: str) -> bytes:
    return field(number, 2, value.encode("utf-8"))


def message(number: int, value: bytes) -> bytes:
    return field(number, 2, varint(len(value)) + value)


def tensor(name: str, shape: tuple[int, ...], values: list[float]) -> bytes:
    raw = struct.pack(f"<{len(values)}f", *values)
    output = bytearray()
    for dimension in shape:
        output += integer(1, dimension)
    output += integer(2, 1)  # TensorProto.DataType.FLOAT
    output += text(8, name)
    output += field(9, 2, varint(len(raw)) + raw)  # TensorProto.raw_data
    return bytes(output)


def dimension(value: int) -> bytes:
    return integer(1, value)


def value_info(name: str, shape: tuple[int, ...]) -> bytes:
    tensor_shape = b"".join(message(1, dimension(size)) for size in shape)
    tensor_type = integer(1, 1) + message(2, tensor_shape)  # float tensor
    type_proto = message(1, tensor_type)
    return text(1, name) + message(2, type_proto)


def node(op_type: str, inputs: tuple[str, ...], output: str, name: str) -> bytes:
    result = bytearray()
    for item in inputs:
        result += text(1, item)
    result += text(2, output)
    result += text(3, name)
    result += text(4, op_type)
    return bytes(result)


def metadata(key: str, value: str) -> bytes:
    return text(1, key) + text(2, value)


def build() -> bytes:
    # Deterministic, non-trained weights. The only purpose is backend wiring.
    w1 = [(((row * 7 + col * 11) % 29) - 14) / 50 for row in range(16) for col in range(24)]
    b1 = [((index % 5) - 2) / 100 for index in range(24)]
    w2 = [(((row * 5 + col * 3) % 17) - 8) / 40 for row in range(24) for col in range(8)]
    b2 = [((index % 3) - 1) / 100 for index in range(8)]
    w3 = [(((row * 3 + col * 2) % 13) - 6) / 30 for row in range(8) for col in range(3)]
    b3 = [0.0, 0.0, 0.5]
    initializers = [
        tensor("W1", (16, 24), w1),
        tensor("B1", (24,), b1),
        tensor("W2", (24, 8), w2),
        tensor("B2", (8,), b2),
        tensor("W3", (8, 3), w3),
        tensor("B3", (3,), b3),
    ]
    nodes = [
        node("MatMul", ("features", "W1"), "hidden1_linear", "gpu_probe_matmul_1"),
        node("Add", ("hidden1_linear", "B1"), "hidden1_bias", "gpu_probe_add_1"),
        node("Relu", ("hidden1_bias",), "hidden1", "gpu_probe_relu_1"),
        node("MatMul", ("hidden1", "W2"), "hidden2_linear", "gpu_probe_matmul_2"),
        node("Add", ("hidden2_linear", "B2"), "hidden2_bias", "gpu_probe_add_2"),
        node("Relu", ("hidden2_bias",), "hidden2", "gpu_probe_relu_2"),
        node("MatMul", ("hidden2", "W3"), "output_linear", "gpu_probe_matmul_3"),
        node("Add", ("output_linear", "B3"), "embedding", "gpu_probe_add_3"),
    ]
    graph = bytearray()
    for item in nodes:
        graph += message(1, item)
    graph += text(2, "farmaxia_vizz_031_gpu_probe")
    for item in initializers:
        graph += message(5, item)
    graph += text(6, "Deterministic smoke graph; not trained on human data.")
    graph += message(11, value_info("features", (1, 16)))
    graph += message(12, value_info("embedding", (1, 3)))

    model = bytearray()
    model += integer(1, 9)  # ONNX IR version
    model += text(2, "FARMAXIA")
    model += text(3, "031")
    model += text(6, "GPU-only infrastructure probe; not a gaze predictor.")
    model += message(7, bytes(graph))
    model += message(8, integer(2, 13))  # default ONNX opset 13
    model += message(14, metadata("training_status", "untrained_deterministic_smoke_model"))
    model += message(14, metadata("execution_policy", "webgpu_only_no_fallback"))
    return bytes(model)


if __name__ == "__main__":
    output_path = HERE / "models" / "tiny_gaze_encoder.onnx"
    output_path.write_bytes(build())
    print(f"WROTE {output_path} bytes={output_path.stat().st_size}")
