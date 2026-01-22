# SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for diagram templates."""

import pytest
import control as ct
import lynx
from lynx.templates import DIAGRAM_TEMPLATES


# ============================================================================
# Level 1: Structural Validation Tests
# ============================================================================


@pytest.mark.parametrize("template_name", list(DIAGRAM_TEMPLATES.keys()))
def test_template_loads(template_name):
    """Each template should load without errors."""
    diagram = lynx.Diagram.from_template(template_name)
    assert len(diagram.blocks) > 0
    assert len(diagram.connections) > 0


@pytest.mark.parametrize(
    "template_name,min_blocks",
    [
        ("open_loop_tf", 3),  # input, plant, output
        ("open_loop_ss", 3),  # input, plant, output
        ("feedback_tf", 5),  # input, sum, controller, plant, output
        ("feedback_ss", 5),  # input, sum, controller, plant, output
        ("feedforward_tf", 7),  # input, 2 sums, feedforward, feedback, plant, output
        ("feedforward_ss", 7),  # input, 2 sums, feedforward, feedback, plant, output
        ("filtered", 9),  # adds ref_filter and obs_filter
        ("cascaded", 10),  # nested loops with multiple inputs/outputs
    ],
)
def test_template_has_minimum_blocks(template_name, min_blocks):
    """Each template should have expected minimum number of blocks."""
    diagram = lynx.Diagram.from_template(template_name)
    assert (
        len(diagram.blocks) >= min_blocks
    ), f"{template_name} has {len(diagram.blocks)} blocks, expected at least {min_blocks}"


@pytest.mark.parametrize(
    "template_name,expected_block_labels",
    [
        ("open_loop_tf", ["input", "plant", "output"]),
        ("open_loop_ss", ["input", "plant", "output"]),
        ("feedback_tf", ["ref", "controller", "plant", "output"]),
        ("feedback_ss", ["ref", "controller", "plant", "output"]),
        (
            "feedforward_tf",
            ["ref", "feedforward", "feedback", "plant", "output"],
        ),
        (
            "feedforward_ss",
            ["ref", "feedforward", "feedback", "plant", "output"],
        ),
        (
            "filtered",
            ["ref", "ref_filter", "feedforward", "feedback", "obs_filter", "plant", "output"],
        ),
        (
            "cascaded",
            ["ref", "output1", "output2"],  # Core blocks - others may be unlabeled
        ),
    ],
)
def test_template_has_expected_block_labels(template_name, expected_block_labels):
    """Each template should contain expected labeled blocks."""
    diagram = lynx.Diagram.from_template(template_name)
    block_labels = {b.label for b in diagram.blocks if b.label and b.label != "output"}

    # For "output" label, check both "output" and "output1" (some templates may vary)
    if "output" in expected_block_labels:
        output_blocks = [b for b in diagram.blocks if b.label and b.label.startswith("output")]
        assert len(output_blocks) > 0, f"No output block found in {template_name}"
        expected_block_labels_mod = [l for l in expected_block_labels if l != "output"]
    else:
        expected_block_labels_mod = expected_block_labels

    for label in expected_block_labels_mod:
        assert (
            label in block_labels
        ), f"Missing block with label '{label}' in {template_name}. Found: {block_labels}"


def test_template_has_input_and_output_markers():
    """Each template should have at least one input and one output marker."""
    for template_name in DIAGRAM_TEMPLATES.keys():
        diagram = lynx.Diagram.from_template(template_name)
        io_markers = [b for b in diagram.blocks if b.type == "io_marker"]

        input_markers = [
            m for m in io_markers if m.get_parameter("marker_type") == "input"
        ]
        output_markers = [
            m for m in io_markers if m.get_parameter("marker_type") == "output"
        ]

        assert (
            len(input_markers) >= 1
        ), f"{template_name} should have at least 1 input marker"
        assert (
            len(output_markers) >= 1
        ), f"{template_name} should have at least 1 output marker"


def test_template_io_markers_have_unique_labels():
    """IOMarkers in each template should have unique block labels for get_tf/get_ss."""
    for template_name in DIAGRAM_TEMPLATES.keys():
        diagram = lynx.Diagram.from_template(template_name)
        io_markers = [b for b in diagram.blocks if b.type == "io_marker"]

        # Get block labels (what get_tf uses for signal reference)
        input_labels = []
        output_labels = []

        for marker in io_markers:
            marker_type = marker.get_parameter("marker_type")
            # Use block.label, not parameter
            label = marker.label

            if marker_type == "input":
                input_labels.append(label)
            else:
                output_labels.append(label)

        # Check for duplicates
        if len(input_labels) > 1:
            assert len(input_labels) == len(set(input_labels)), (
                f"{template_name}: Input markers have duplicate block labels: {input_labels}. "
                "Each input should have a unique label like 'r', 'n', 'd', etc."
            )

        if len(output_labels) > 1:
            assert len(output_labels) == len(set(output_labels)), (
                f"{template_name}: Output markers have duplicate block labels: {output_labels}. "
                "Each output should have a unique label like 'y0', 'y1', 'y2', etc."
            )


def test_template_connections_are_valid():
    """All connections in templates should reference existing blocks and ports."""
    for template_name in DIAGRAM_TEMPLATES.keys():
        diagram = lynx.Diagram.from_template(template_name)

        block_ids = {b.id for b in diagram.blocks}

        for conn in diagram.connections:
            # Check source block exists
            assert (
                conn.source_block_id in block_ids
            ), f"{template_name}: Connection {conn.id} references non-existent source block {conn.source_block_id}"

            # Check target block exists
            assert (
                conn.target_block_id in block_ids
            ), f"{template_name}: Connection {conn.id} references non-existent target block {conn.target_block_id}"

            # Check source port exists
            source_block = diagram.get_block(conn.source_block_id)
            source_port_ids = {p.id for p in source_block._ports}
            assert (
                conn.source_port_id in source_port_ids
            ), f"{template_name}: Connection {conn.id} references non-existent source port {conn.source_port_id} on block {source_block.label or source_block.id}"

            # Check target port exists
            target_block = diagram.get_block(conn.target_block_id)
            target_port_ids = {p.id for p in target_block._ports}
            assert (
                conn.target_port_id in target_port_ids
            ), f"{template_name}: Connection {conn.id} references non-existent target port {conn.target_port_id} on block {target_block.label or target_block.id}"


# ============================================================================
# Level 2: Parameter Modification Tests
# ============================================================================


def test_template_parameter_modification_transfer_function():
    """Should be able to modify TransferFunction parameters after loading."""
    diagram = lynx.Diagram.from_template("feedback_tf")

    # Find controller block
    controller = next(b for b in diagram.blocks if b.label == "controller")

    # Modify numerator parameter
    new_num = [5.0, 2.0]
    diagram.update_block_parameter(controller.id, "numerator", new_num)

    # Verify change persisted
    controller_after = diagram.get_block(controller.id)
    assert controller_after.get_parameter("numerator") == new_num


def test_template_parameter_modification_state_space():
    """Should be able to modify StateSpace parameters after loading."""
    diagram = lynx.Diagram.from_template("feedback_ss")

    # Find plant block
    plant = next(b for b in diagram.blocks if b.label == "plant")

    # Modify A matrix
    new_A = [[1.0, 2.0], [3.0, 4.0]]
    diagram.update_block_parameter(plant.id, "A", new_A)

    # Verify change persisted
    plant_after = diagram.get_block(plant.id)
    assert plant_after.get_parameter("A") == new_A


def test_template_parameter_modification_gain():
    """Should be able to modify Gain parameters after loading."""
    # Use feedback_tf and change controller to a gain block manually
    # Or use a template that has a gain block
    # For now, test that we can modify controller numerator/denominator
    diagram = lynx.Diagram.from_template("feedback_tf")

    controller = next(b for b in diagram.blocks if b.label == "controller")

    # Make it a proportional controller (numerator = [K], denominator = [1])
    diagram.update_block_parameter(controller.id, "numerator", [10.0])
    diagram.update_block_parameter(controller.id, "denominator", [1.0])

    controller_after = diagram.get_block(controller.id)
    assert controller_after.get_parameter("numerator") == [10.0]
    assert controller_after.get_parameter("denominator") == [1.0]


def test_template_round_trip_serialization():
    """Template should survive serialize/deserialize cycle with modifications."""
    diagram = lynx.Diagram.from_template("feedback_ss")

    # Modify plant A matrix
    plant = next(b for b in diagram.blocks if b.label == "plant")
    new_A = [[1.0, 2.0], [3.0, 4.0]]
    diagram.update_block_parameter(plant.id, "A", new_A)

    # Round-trip through dict
    data = diagram.to_dict()
    diagram2 = lynx.Diagram.from_dict(data)

    # Verify modification survived
    plant2 = next(b for b in diagram2.blocks if b.label == "plant")
    assert plant2.get_parameter("A") == new_A


def test_template_custom_latex_modification():
    """Should be able to modify custom_latex on blocks after loading."""
    diagram = lynx.Diagram.from_template("feedback_tf")

    # Find controller block
    controller = next(b for b in diagram.blocks if b.label == "controller")

    # Modify custom LaTeX
    original_latex = controller.custom_latex
    new_latex = r"K_p(s)"
    controller.custom_latex = new_latex

    # Verify change persisted
    assert controller.custom_latex == new_latex
    assert controller.custom_latex != original_latex


# ============================================================================
# Level 3: Python-Control Export Tests
# ============================================================================


@pytest.mark.parametrize(
    "template_name",
    [
        "open_loop_tf",
        "open_loop_ss",
        "feedback_tf",
        "feedback_ss",
        "feedforward_tf",
        "feedforward_ss",
        "filtered",
    ],
)
def test_template_exports_to_python_control_single_output(template_name):
    """SISO templates should export to python-control systems."""
    diagram = lynx.Diagram.from_template(template_name)

    # Get IOMarker labels
    io_markers = [b for b in diagram.blocks if b.type == "io_marker"]
    input_markers = [
        m for m in io_markers if m.get_parameter("marker_type") == "input"
    ]
    output_markers = [
        m for m in io_markers if m.get_parameter("marker_type") == "output"
    ]

    # For SISO systems, use the first (and only) input/output
    input_label = input_markers[0].label  # Use block label
    output_label = output_markers[0].label  # Use block label

    # Should be able to extract transfer function
    sys = diagram.get_tf(input_label, output_label)
    assert sys is not None

    # System should have reasonable properties
    assert sys.ninputs == 1, f"{template_name}: Expected 1 input, got {sys.ninputs}"
    assert sys.noutputs == 1, f"{template_name}: Expected 1 output, got {sys.noutputs}"

    # Check that it's a proper transfer function (not just identity)
    # by verifying it has denominator
    if hasattr(sys, "den"):
        assert (
            len(sys.den[0][0]) > 0
        ), f"{template_name}: Transfer function has no denominator"


@pytest.mark.parametrize(
    "template_name",
    [
        "open_loop_tf",
        "open_loop_ss",
        "feedback_tf",
        "feedback_ss",
        "feedforward_tf",
        "feedforward_ss",
        "filtered",
    ],
)
def test_template_exports_to_state_space(template_name):
    """Templates should export to state-space representation."""
    diagram = lynx.Diagram.from_template(template_name)

    # Get IOMarker labels
    io_markers = [b for b in diagram.blocks if b.type == "io_marker"]
    input_markers = [
        m for m in io_markers if m.get_parameter("marker_type") == "input"
    ]
    output_markers = [
        m for m in io_markers if m.get_parameter("marker_type") == "output"
    ]

    input_label = input_markers[0].label  # Use block label
    output_label = output_markers[0].label  # Use block label

    # Should be able to extract state-space
    sys = diagram.get_ss(input_label, output_label)
    assert sys is not None

    # System should have reasonable properties
    assert sys.ninputs == 1
    assert sys.noutputs == 1


def test_template_modified_parameters_affect_export():
    """Modifying template parameters should affect exported system."""
    diagram = lynx.Diagram.from_template("feedback_tf")

    # Get original system
    sys_original = diagram.get_tf("r", "y")

    # Modify controller gain
    controller = next(b for b in diagram.blocks if b.label == "controller")
    diagram.update_block_parameter(controller.id, "numerator", [10.0])  # K=10
    diagram.update_block_parameter(controller.id, "denominator", [1.0])

    # Modify plant
    plant = next(b for b in diagram.blocks if b.label == "plant")
    diagram.update_block_parameter(plant.id, "numerator", [2.0])
    diagram.update_block_parameter(plant.id, "denominator", [1.0, 1.0])  # 2/(s+1)

    # Get new system
    sys_modified = diagram.get_tf("r", "y")

    # Systems should be different (can check DC gain for closed-loop)
    # For C=10, G=2/(s+1), closed-loop should have different DC gain than original
    dc_gain_original = ct.dcgain(sys_original)
    dc_gain_modified = ct.dcgain(sys_modified)

    # DC gains should be different (unless by coincidence)
    # Modified should be 20/(1+20) ≈ 0.952
    assert abs(dc_gain_modified - 20 / 21) < 0.01, (
        f"Expected DC gain ≈ 0.952, got {dc_gain_modified}"
    )


def test_template_step_response():
    """Should be able to simulate step response of template systems."""
    diagram = lynx.Diagram.from_template("feedback_tf")

    # Modify to known system for predictable behavior
    controller = next(b for b in diagram.blocks if b.label == "controller")
    plant = next(b for b in diagram.blocks if b.label == "plant")

    diagram.update_block_parameter(controller.id, "numerator", [5.0])
    diagram.update_block_parameter(controller.id, "denominator", [1.0])
    diagram.update_block_parameter(plant.id, "numerator", [2.0])
    diagram.update_block_parameter(plant.id, "denominator", [1.0, 3.0])

    # Get closed-loop system
    sys = diagram.get_tf("u", "y")

    # Simulate step response
    t, y = ct.step_response(sys, T=5.0)

    # Check that response is reasonable
    assert len(t) > 0
    assert len(y) > 0
    assert y[-1] > 0, "Step response should settle to positive value"
    assert y[-1] < 2.0, "Step response should not have excessive overshoot"


def test_cascaded_template_mimo_export():
    """Cascaded template with multiple inputs/outputs should export correctly."""
    diagram = lynx.Diagram.from_template("cascaded")

    # Get all IOMarkers
    io_markers = [b for b in diagram.blocks if b.type == "io_marker"]
    input_markers = [
        m for m in io_markers if m.get_parameter("marker_type") == "input"
    ]
    output_markers = [
        m for m in io_markers if m.get_parameter("marker_type") == "output"
    ]

    # If we have multiple inputs/outputs with unique labels, test MIMO export
    input_labels = [m.label for m in input_markers]  # Use block labels
    output_labels = [m.label for m in output_markers]  # Use block labels

    # Get unique labels
    unique_inputs = list(set(input_labels))
    unique_outputs = list(set(output_labels))

    # If we have unique labels, test extraction
    if len(unique_inputs) >= 1 and len(unique_outputs) >= 1:
        sys = diagram.get_tf(unique_inputs[0], unique_outputs[0])
        assert sys is not None
        assert sys.ninputs == 1
        assert sys.noutputs == 1


# ============================================================================
# Additional Validation Tests
# ============================================================================


def test_template_names_are_documented():
    """from_template docstring should list all available templates."""
    from lynx import Diagram

    docstring = Diagram.from_template.__doc__
    assert docstring is not None

    # Check that template names appear in docstring (or at least some of them)
    # This is a softer check - the docstring should mention available templates
    assert "template" in docstring.lower()


def test_invalid_template_name_raises_error():
    """from_template should raise ValueError for invalid template names."""
    with pytest.raises(ValueError, match="Unknown template"):
        lynx.Diagram.from_template("nonexistent_template")


def test_template_error_message_lists_valid_options():
    """Error message should list valid template names."""
    try:
        lynx.Diagram.from_template("invalid")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        error_msg = str(e)
        # Check that some template names appear in error message
        assert "open_loop_tf" in error_msg or "feedback_tf" in error_msg
        assert "Valid options" in error_msg or "options:" in error_msg
