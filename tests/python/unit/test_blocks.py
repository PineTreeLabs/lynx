# SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for block models

Testing:
- Gain block with single scalar K parameter
- Input/Output marker blocks with no parameters
- Sum block with signs array and multiple inputs
- Transfer Function block with numerator/denominator arrays
- State Space block with A, B, C, D matrices
"""

import pytest

from lynx.blocks.gain import GainBlock
from lynx.blocks.io_marker import InputMarker, OutputMarker


class TestGainBlock:
    """Test Gain block model (T012)"""

    def test_gain_block_creation(self) -> None:
        """Gain block can be created with K parameter"""
        block = GainBlock(id="gain1", K=5.0)

        assert block.id == "gain1"
        assert block.type == "gain"
        assert block.get_parameter("K") == 5.0

    def test_custom_latex_property_default(self) -> None:
        """Test custom_latex defaults to None - T011"""
        block = GainBlock(id="test", K=1.0)
        assert block.custom_latex is None

    def test_custom_latex_property_setter(self) -> None:
        """Test setting custom_latex - T012"""
        block = GainBlock(id="test", K=1.0)
        block.custom_latex = r"\alpha"
        assert block.custom_latex == r"\alpha"

    def test_custom_latex_property_clear(self) -> None:
        """Test clearing custom_latex reverts to None - T013"""
        block = GainBlock(id="test", K=1.0)
        block.custom_latex = r"\beta"
        block.custom_latex = None
        assert block.custom_latex is None

    def test_custom_latex_serializes_to_dict(self) -> None:
        """Test custom_latex is included in serialization when set"""
        block = GainBlock(id="test", K=1.0)
        block.custom_latex = r"K_p"

        data = block.to_dict()
        assert data["custom_latex"] == r"K_p"

    def test_custom_latex_not_serialized_when_none(self) -> None:
        """Test custom_latex not included in serialization
        when None (backward compatibility)"""
        block = GainBlock(id="test", K=1.0)

        data = block.to_dict()
        assert "custom_latex" not in data

    def test_gain_block_has_one_input_port(self) -> None:
        """Gain block has exactly one input port"""
        block = GainBlock(id="gain1", K=1.0)

        ports = block.get_ports()
        input_ports = [p for p in ports if p["type"] == "input"]

        assert len(input_ports) == 1
        assert input_ports[0]["id"] == "in"

    def test_gain_block_has_one_output_port(self) -> None:
        """Gain block has exactly one output port"""
        block = GainBlock(id="gain1", K=1.0)

        ports = block.get_ports()
        output_ports = [p for p in ports if p["type"] == "output"]

        assert len(output_ports) == 1
        assert output_ports[0]["id"] == "out"

    def test_gain_block_k_parameter_is_required(self) -> None:
        """Gain block requires K parameter"""
        with pytest.raises(TypeError):
            GainBlock(id="gain1")  # type: ignore

    def test_gain_block_serializes_to_dict(self) -> None:
        """Gain block can serialize to dictionary"""
        block = GainBlock(id="gain1", K=2.5, position={"x": 100, "y": 200})

        data = block.to_dict()

        assert data["id"] == "gain1"
        assert data["type"] == "gain"
        assert data["position"] == {"x": 100, "y": 200}
        assert len(data["parameters"]) == 1
        assert data["parameters"][0]["name"] == "K"
        assert data["parameters"][0]["value"] == 2.5


class TestInputMarker:
    """Test Input marker block model (T013)"""

    def test_input_marker_creation(self) -> None:
        """Input marker can be created without parameters"""
        block = InputMarker(id="input1")

        assert block.id == "input1"
        assert block.type == "io_marker"

    def test_input_marker_has_one_output_port(self) -> None:
        """Input marker has exactly one output port (signals flow OUT)"""
        block = InputMarker(id="input1")

        ports = block.get_ports()
        output_ports = [p for p in ports if p["type"] == "output"]
        input_ports = [p for p in ports if p["type"] == "input"]

        assert len(output_ports) == 1
        assert len(input_ports) == 0

    def test_input_marker_has_label_parameter(self) -> None:
        """Input marker can have optional label"""
        block = InputMarker(id="input1", label="u")

        assert block.get_parameter("label") == "u"

    def test_input_marker_serializes_to_dict(self) -> None:
        """Input marker can serialize to dictionary"""
        block = InputMarker(id="input1", label="u", position={"x": 50, "y": 100})

        data = block.to_dict()

        assert data["id"] == "input1"
        assert data["type"] == "io_marker"
        assert data["position"] == {"x": 50, "y": 100}


class TestOutputMarker:
    """Test Output marker block model (T013)"""

    def test_output_marker_creation(self) -> None:
        """Output marker can be created without parameters"""
        block = OutputMarker(id="output1")

        assert block.id == "output1"
        assert block.type == "io_marker"

    def test_output_marker_has_one_input_port(self) -> None:
        """Output marker has exactly one input port (signals flow IN)"""
        block = OutputMarker(id="output1")

        ports = block.get_ports()
        input_ports = [p for p in ports if p["type"] == "input"]
        output_ports = [p for p in ports if p["type"] == "output"]

        assert len(input_ports) == 1
        assert len(output_ports) == 0

    def test_output_marker_serializes_to_dict(self) -> None:
        """Output marker can serialize to dictionary"""
        block = OutputMarker(id="output1", label="y", position={"x": 300, "y": 100})

        data = block.to_dict()

        assert data["id"] == "output1"
        assert data["type"] == "io_marker"
        assert data["position"] == {"x": 300, "y": 100}


class TestSumBlock:
    """Test Sum block model (T031)"""

    def test_sum_block_creation(self) -> None:
        """Sum block can be created with signs parameter"""
        from lynx.blocks.sum import SumBlock

        block = SumBlock(id="sum1", signs=["+", "+", "-"])

        assert block.id == "sum1"
        assert block.type == "sum"
        assert block.get_parameter("signs") == ["+", "+", "-"]

    def test_sum_block_has_multiple_input_ports(self) -> None:
        """Sum block creates one input port per sign"""
        from lynx.blocks.sum import SumBlock

        block = SumBlock(id="sum1", signs=["+", "-", "+"])

        ports = block.get_ports()
        input_ports = [p for p in ports if p["type"] == "input"]

        assert len(input_ports) == 3
        assert input_ports[0]["id"] == "in1"
        assert input_ports[1]["id"] == "in2"
        assert input_ports[2]["id"] == "in3"

    def test_sum_block_has_one_output_port(self) -> None:
        """Sum block has exactly one output port"""
        from lynx.blocks.sum import SumBlock

        block = SumBlock(id="sum1", signs=["+", "+", "-"])

        ports = block.get_ports()
        output_ports = [p for p in ports if p["type"] == "output"]

        assert len(output_ports) == 1
        assert output_ports[0]["id"] == "out"

    def test_sum_block_requires_three_inputs(self) -> None:
        """Sum block must have at exactly 3 input ports"""
        from lynx.blocks.sum import SumBlock

        with pytest.raises(ValueError, match="exactly 3 signs"):
            SumBlock(id="sum1", signs=["+"])

    def test_sum_block_serializes_to_dict(self) -> None:
        """Sum block can serialize to dictionary"""
        from lynx.blocks.sum import SumBlock

        block = SumBlock(
            id="sum1", signs=["+", "-", "|"], position={"x": 150, "y": 200}
        )

        data = block.to_dict()

        assert data["id"] == "sum1"
        assert data["type"] == "sum"
        assert data["position"] == {"x": 150, "y": 200}
        assert any(p["name"] == "signs" for p in data["parameters"])


class TestTransferFunctionBlock:
    """Test Transfer Function block model (T032)"""

    def test_transfer_function_creation(self) -> None:
        """Transfer function can be created with numerator and denominator"""
        from lynx.blocks.transfer_function import TransferFunctionBlock

        block = TransferFunctionBlock(id="tf1", numerator=[1, 2], denominator=[1, 3, 2])

        assert block.id == "tf1"
        assert block.type == "transfer_function"
        assert block.get_parameter("numerator") == [1, 2]
        assert block.get_parameter("denominator") == [1, 3, 2]

    def test_transfer_function_has_one_input_one_output(self) -> None:
        """Transfer function has one input and one output port"""
        from lynx.blocks.transfer_function import TransferFunctionBlock

        block = TransferFunctionBlock(id="tf1", numerator=[1], denominator=[1, 1])

        ports = block.get_ports()
        input_ports = [p for p in ports if p["type"] == "input"]
        output_ports = [p for p in ports if p["type"] == "output"]

        assert len(input_ports) == 1
        assert len(output_ports) == 1

    def test_transfer_function_serializes_to_dict(self) -> None:
        """Transfer function can serialize to dictionary"""
        from lynx.blocks.transfer_function import TransferFunctionBlock

        block = TransferFunctionBlock(
            id="tf1",
            numerator=[1, 0],
            denominator=[1, 2, 1],
            position={"x": 200, "y": 150},
        )

        data = block.to_dict()

        assert data["id"] == "tf1"
        assert data["type"] == "transfer_function"
        assert data["position"] == {"x": 200, "y": 150}
        assert any(p["name"] == "numerator" for p in data["parameters"])
        assert any(p["name"] == "denominator" for p in data["parameters"])


class TestStateSpaceBlock:
    """Test State Space block model (T033)"""

    def test_state_space_creation(self) -> None:
        """State space block can be created with A, B, C, D matrices"""
        from lynx.blocks.state_space import StateSpaceBlock

        block = StateSpaceBlock(
            id="ss1",
            A=[[0, 1], [-2, -3]],
            B=[[0], [1]],
            C=[[1, 0]],
            D=[[0]],
        )

        assert block.id == "ss1"
        assert block.type == "state_space"
        assert block.get_parameter("A") == [[0, 1], [-2, -3]]
        assert block.get_parameter("B") == [[0], [1]]
        assert block.get_parameter("C") == [[1, 0]]
        assert block.get_parameter("D") == [[0]]

    def test_state_space_has_one_input_one_output(self) -> None:
        """State space block has one input and one output port (SISO only for MVP)"""
        from lynx.blocks.state_space import StateSpaceBlock

        block = StateSpaceBlock(
            id="ss1",
            A=[[0, 1], [-1, -1]],
            B=[[0], [1]],
            C=[[1, 0]],
            D=[[0]],
        )

        ports = block.get_ports()
        input_ports = [p for p in ports if p["type"] == "input"]
        output_ports = [p for p in ports if p["type"] == "output"]

        assert len(input_ports) == 1
        assert len(output_ports) == 1

    def test_state_space_serializes_to_dict(self) -> None:
        """State space block can serialize to dictionary"""
        from lynx.blocks.state_space import StateSpaceBlock

        block = StateSpaceBlock(
            id="ss1",
            A=[[1, 0], [0, 1]],
            B=[[1], [0]],
            C=[[1, 1]],
            D=[[0]],
            position={"x": 250, "y": 200},
        )

        data = block.to_dict()

        assert data["id"] == "ss1"
        assert data["type"] == "state_space"
        assert data["position"] == {"x": 250, "y": 200}
        assert any(p["name"] == "A" for p in data["parameters"])
        assert any(p["name"] == "B" for p in data["parameters"])
        assert any(p["name"] == "C" for p in data["parameters"])
        assert any(p["name"] == "D" for p in data["parameters"])
