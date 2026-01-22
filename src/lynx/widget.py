# SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Lynx widget - anywidget integration and traitlet definitions.

This module provides the main widget class that connects:
- Python backend (Diagram, validation, persistence)
- JavaScript frontend (React Flow UI)

Communication via anywidget traitlets.
"""

import pathlib
from typing import Any, Dict, Optional, cast

import anywidget
import traitlets

from lynx.config.constants import ActionTypes
from lynx.diagram import Diagram, ValidationResult
from lynx.expression_eval import evaluate_expression
from lynx.utils.logging_config import setup_logger
from lynx.utils.theme_config import resolve_theme, validate_theme_name
from lynx.validation import validate_diagram


class LynxWidget(anywidget.AnyWidget):
    """Lynx block diagram widget.

    anywidget that provides interactive block diagram editing in Jupyter.

    Traitlets:
        diagram_state: Python → JS (diagram serialization)
        validation_result: Python → JS (validation errors/warnings)
        _action: JS → Python (user actions like addBlock, deleteBlock)
    """

    # Path to bundled JavaScript (Vite output)
    _esm = pathlib.Path(__file__).parent / "static" / "index.js"
    _css = pathlib.Path(__file__).parent / "static" / "index.css"

    # State traitlets (Python → JavaScript)
    diagram_state = traitlets.Dict(default_value={}).tag(sync=True)
    validation_result = traitlets.Dict(default_value={}).tag(sync=True)
    selected_block_id = traitlets.Unicode(default_value=None, allow_none=True).tag(
        sync=True
    )
    grid_snap_enabled = traitlets.Bool(default_value=True).tag(sync=True)
    theme = traitlets.Unicode(default_value="light").tag(sync=True)

    # Command traitlets (JavaScript → Python)
    _action = traitlets.Dict(default_value={}).tag(sync=True)
    _save_request = traitlets.Unicode(default_value="").tag(sync=True)
    _load_request = traitlets.Unicode(default_value="").tag(sync=True)

    # Capture traitlets (for static diagram export)
    _capture_request = traitlets.Dict(default_value={}).tag(sync=True)
    _capture_result = traitlets.Dict(default_value={}).tag(sync=True)
    _capture_mode = traitlets.Bool(default_value=False).tag(sync=True)

    def __init__(self, diagram: Optional[Diagram] = None, **kwargs: Any) -> None:
        """Initialize widget with a diagram.

        Args:
            diagram: Optional Diagram instance to edit. If not provided,
                creates empty diagram.
            **kwargs: Additional anywidget parameters
        """
        super().__init__(**kwargs)

        # Set up logger
        self.logger = setup_logger("lynx.widget")

        # Use provided diagram or create new one
        self.diagram = diagram if diagram is not None else Diagram()

        # Initialize theme from diagram or defaults
        diagram_theme = getattr(self.diagram, "theme", None)
        self.theme = resolve_theme(diagram_theme)

        # Initialize diagram_state
        self._update_diagram_state()

        # Set up observers for actions
        self.observe(self._on_action, names=["_action"])
        self.observe(self._on_save_request, names=["_save_request"])
        self.observe(self._on_load_request, names=["_load_request"])
        self.observe(self._on_capture_request, names=["_capture_request"])
        self.observe(self._on_theme_change, names=["theme"])

        # Track last action timestamp to avoid duplicate processing
        self._last_action_timestamp: float = 0.0

    def _update_diagram_state(self) -> None:
        """Update diagram_state traitlet from current diagram."""
        import time

        new_state = self.diagram.to_dict()

        # Add version timestamp to force traitlet sync
        # (traitlets may not detect nested dict changes)
        new_state["_version"] = time.time()

        # Update the traitlet
        self.diagram_state = new_state

    def _run_validation(self) -> None:
        """Run control theory validation and update validation_result.

        Checks for:
        - Algebraic loops (errors)
        - Label uniqueness (errors)
        - System completeness (warnings)
        - Disconnected blocks (warnings)
        """
        result = validate_diagram(self.diagram)
        self.validation_result = result.to_dict()

    def update(self) -> None:
        """Public method to update diagram_state after direct modifications.

        Call this after modifying widget.diagram directly
        (e.g., widget.diagram.add_block(...)) to sync the state to JavaScript.
        """
        self._update_diagram_state()
        self._run_validation()

    def _on_action(self, change: Dict[str, Any]) -> None:
        """Handle user actions from JavaScript.

        Args:
            change: Traitlet change dictionary with 'new' value
        """
        action = change["new"]
        if not action:
            return

        # Deduplicate actions by timestamp
        timestamp = action.get("timestamp", 0.0)
        if timestamp <= self._last_action_timestamp:
            return

        self._last_action_timestamp = timestamp

        # Dispatch action by type
        action_type = action.get("type", "")
        payload = action.get("payload", {})

        if action_type == ActionTypes.ADD_BLOCK:
            self._handle_add_block(payload)
        elif action_type == ActionTypes.DELETE_BLOCK:
            self._handle_delete_block(payload)
        elif action_type == ActionTypes.MOVE_BLOCK:
            self._handle_move_block(payload)
        elif action_type == ActionTypes.ADD_CONNECTION:
            self._handle_add_connection(payload)
        elif action_type == ActionTypes.UPDATE_PARAMETER:
            self._handle_update_parameter(payload)
        elif action_type == ActionTypes.DELETE_CONNECTION:
            self._handle_delete_connection(payload)
        elif action_type == ActionTypes.UPDATE_BLOCK_LABEL:
            self._handle_update_block_label(payload)
        elif action_type == ActionTypes.FLIP_BLOCK:
            self._handle_flip_block(payload)
        elif action_type == ActionTypes.TOGGLE_LABEL_VISIBILITY:
            self._handle_toggle_label_visibility(payload)
        elif action_type == ActionTypes.UNDO:
            self._handle_undo(payload)
        elif action_type == ActionTypes.REDO:
            self._handle_redo(payload)
        elif action_type == ActionTypes.UPDATE_CONNECTION_ROUTING:
            self._handle_update_connection_routing(payload)
        elif action_type == ActionTypes.RESET_CONNECTION_ROUTING:
            self._handle_reset_connection_routing(payload)
        elif action_type == ActionTypes.TOGGLE_CONNECTION_LABEL_VISIBILITY:
            self._handle_toggle_connection_label_visibility(payload)
        elif action_type == ActionTypes.UPDATE_CONNECTION_LABEL:
            self._handle_update_connection_label(payload)
        elif action_type == ActionTypes.RESIZE_BLOCK:
            self._handle_resize_block(payload)
        elif action_type == ActionTypes.UPDATE_THEME:
            self._handle_update_theme(payload)

    def _handle_add_block(self, payload: Dict[str, Any]) -> None:
        """Handle addBlock action.

        Args:
            payload: Contains blockType, id, position, and parameters
        """
        block_type = payload.get("blockType", "")
        block_id = payload.get("id", "")
        position = payload.get("position", {"x": 0.0, "y": 0.0})

        # Extract type-specific parameters
        excluded = ["blockType", "id", "position"]
        params = {k: v for k, v in payload.items() if k not in excluded}

        try:
            self.diagram.add_block(
                block_type=block_type, id=block_id, position=position, **params
            )
            self._update_diagram_state()
            self._run_validation()
        except (ValueError, KeyError) as e:
            # Phase 4 will add proper error handling via validation_result
            self.logger.error(f"Error adding block: {e}")

    def _handle_delete_block(self, payload: Dict[str, Any]) -> None:
        """Handle deleteBlock action.

        Args:
            payload: Contains blockId
        """
        block_id = payload.get("blockId", "")
        if self.diagram.remove_block(block_id):
            self._update_diagram_state()
            self._run_validation()

    def _handle_move_block(self, payload: Dict[str, Any]) -> None:
        """Handle moveBlock action.

        Args:
            payload: Contains blockId and position
        """
        block_id = payload.get("blockId", "")
        position = payload.get("position", {})

        # Use diagram method to ensure undo/redo support
        if self.diagram.update_block_position(block_id, position):
            self._update_diagram_state()

    def _handle_add_connection(self, payload: Dict[str, Any]) -> None:
        """Handle addConnection action.

        Args:
            payload: Contains connectionId, sourceBlockId, sourcePortId,
                targetBlockId, targetPortId
        """
        connection_id = payload.get("connectionId", "")
        source_block_id = payload.get("sourceBlockId", "")
        source_port_id = payload.get("sourcePortId", "")
        target_block_id = payload.get("targetBlockId", "")
        target_port_id = payload.get("targetPortId", "")

        # Validate and add connection
        connection_validation = self.diagram.add_connection(
            connection_id=connection_id,
            source_block_id=source_block_id,
            source_port_id=source_port_id,
            target_block_id=target_block_id,
            target_port_id=target_port_id,
        )

        # If connection was invalid, show error and return
        if not connection_validation.is_valid:
            self.validation_result = connection_validation.to_dict()
            return

        # Connection added successfully - update state and run comprehensive validation
        self._update_diagram_state()
        self._run_validation()

    def _handle_update_parameter(self, payload: Dict[str, Any]) -> None:
        """Handle updateParameter action.

        For State Space matrix parameters, evaluates expressions and stores
        both expression and resolved value (hybrid storage).

        Args:
            payload: Contains blockId, parameterName, value
        """
        block_id = payload.get("blockId", "")
        parameter_name = payload.get("parameterName", "")
        value = payload.get("value")

        # Find block and update parameter
        block = self.diagram.get_block(block_id)
        if not block:
            return

        # Special case: custom_latex is a top-level block attribute, not a parameter
        if parameter_name == "custom_latex":
            # Save state for undo
            self.diagram._save_state()
            # Update custom_latex directly
            block.custom_latex = value
            self._update_diagram_state()
            return

        # Check if this is an expression-based parameter
        is_matrix_param = (
            block.type == "state_space"
            and parameter_name in ["A", "B", "C", "D"]
            and isinstance(value, str)
        )
        is_scalar_param = (
            block.type == "gain" and parameter_name == "K" and isinstance(value, str)
        )
        is_vector_param = (
            block.type == "transfer_function"
            and parameter_name in ["numerator", "denominator"]
            and isinstance(value, str)
        )

        # Process parameter update with validation
        if is_matrix_param or is_scalar_param or is_vector_param:
            # Get notebook namespace for expression evaluation
            namespace = self._get_notebook_namespace()

            # Get current parameter value for fallback
            try:
                current_value = block.get_parameter(parameter_name)
            except KeyError:
                return

            # Evaluate expression with fallback to current value
            # Type narrowing: value is guaranteed to be str by the conditions above
            assert isinstance(value, str)
            result = evaluate_expression(value, namespace, fallback=current_value)

            if result.success:
                # Validate shape based on parameter type
                validation_error = self._validate_parameter_shape(
                    parameter_name, result.value, block.type
                )

                if validation_error:
                    validation = ValidationResult(
                        is_valid=False,
                        errors=[f"Parameter '{parameter_name}': {validation_error}"],
                        warnings=[],
                    )
                    self.validation_result = validation.to_dict()
                else:
                    # Shape is valid - update parameter (with undo support)
                    self.diagram.update_block_parameter(
                        block_id, parameter_name, result.value, expression=value
                    )

                    # Show warning if fallback was used
                    if result.used_fallback and result.warning:
                        validation = ValidationResult(
                            is_valid=True, errors=[], warnings=[result.warning]
                        )
                        self.validation_result = validation.to_dict()

                    # Update diagram state to reflect changes
                    self._update_diagram_state()
            else:
                # Expression evaluation failed - show error
                validation = ValidationResult(
                    is_valid=False,
                    errors=[f"Parameter '{parameter_name}': {result.error}"],
                    warnings=[],
                )
                self.validation_result = validation.to_dict()
                # Keep old value - don't call update method
        else:
            # Non-expression parameter - simple value update via diagram method
            if self.diagram.update_block_parameter(block_id, parameter_name, value):
                self._update_diagram_state()

    def _get_notebook_namespace(self) -> Dict[str, Any]:
        """Get the notebook's global namespace for expression evaluation.

        Returns:
            Dictionary of variables available in the notebook.
            Returns empty dict if not in notebook environment.
        """
        try:
            # Try to get IPython instance
            from IPython import get_ipython

            ipython = get_ipython()
            if ipython is not None:
                # Return user namespace (variables defined in notebook)
                return cast(Dict[str, Any], ipython.user_ns)
        except (ImportError, AttributeError):
            pass

        # Not in notebook environment, return empty namespace
        return {}

    def _validate_parameter_shape(
        self, parameter_name: str, value: Any, block_type: str
    ) -> Optional[str]:
        """Validate that parameter value has the correct shape.

        Args:
            parameter_name: Name of the parameter
            value: Evaluated value to validate
            block_type: Type of block (gain, transfer_function, state_space)

        Returns:
            Error message if validation fails, None if valid
        """
        import numpy as np

        try:
            # Gain block - K must be scalar
            if block_type == "gain" and parameter_name == "K":
                # Try to convert to numpy array
                arr = np.asarray(value)
                if arr.ndim != 0:  # Not a scalar
                    return f"Gain K must be a scalar, got array with shape {arr.shape}"
                # Valid scalar
                return None

            # Transfer function - numerator/denominator must be 1D arrays
            elif block_type == "transfer_function" and parameter_name in [
                "numerator",
                "denominator",
            ]:
                arr = np.asarray(value)
                if arr.ndim == 0:
                    # Scalar - convert to 1D array
                    return None
                elif arr.ndim == 1:
                    # Already 1D
                    return None
                else:
                    msg = (
                        f"{parameter_name} must be a 1D array (vector), "
                        f"got shape {arr.shape}"
                    )
                    return msg

            # State space - A, B, C, D must be 2D arrays (matrices)
            elif block_type == "state_space" and parameter_name in ["A", "B", "C", "D"]:
                arr = np.asarray(value)
                if arr.ndim != 2:
                    return f"Matrix {parameter_name} must be 2D, got shape {arr.shape}"
                return None

        except Exception as e:
            return f"Could not validate shape: {e}"

        return None

    def _handle_delete_connection(self, payload: Dict[str, Any]) -> None:
        """Handle deleteConnection action.

        Args:
            payload: Contains connectionId
        """
        connection_id = payload.get("connectionId", "")
        if self.diagram.remove_connection(connection_id):
            self._update_diagram_state()
            self._run_validation()

    def _handle_update_block_label(self, payload: Dict[str, Any]) -> None:
        """Handle updateBlockLabel action.

        Args:
            payload: Contains blockId and label
        """
        block_id = payload.get("blockId", "")
        new_label = payload.get("label", "")

        # Update label via diagram method (with undo support)
        if self.diagram.update_block_label(block_id, new_label):
            self._update_diagram_state()
            self._run_validation()

    def _handle_resize_block(self, payload: Dict[str, Any]) -> None:
        """Handle resizeBlock action.

        Args:
            payload: Contains blockId, width, and height
        """
        block_id = payload.get("blockId", "")
        width = payload.get("width", 0.0)
        height = payload.get("height", 0.0)

        # Update dimensions via diagram method (with undo support)
        if self.diagram.update_block_dimensions(block_id, width, height):
            self._update_diagram_state()

    def _handle_flip_block(self, payload: Dict[str, Any]) -> None:
        """Handle flipBlock action.

        Args:
            payload: Contains blockId
        """
        block_id = payload.get("blockId", "")

        # Flip block via diagram method (with undo support)
        if self.diagram.flip_block(block_id):
            self._update_diagram_state()

    def _handle_toggle_label_visibility(self, payload: Dict[str, Any]) -> None:
        """Handle toggleLabelVisibility action.

        Args:
            payload: Contains blockId
        """
        block_id = payload.get("blockId", "")

        # Toggle label visibility via diagram method (with undo support)
        if self.diagram.toggle_label_visibility(block_id):
            self._update_diagram_state()

    def _handle_undo(self, payload: Dict[str, Any]) -> None:
        """Handle undo action.

        Args:
            payload: Empty payload (undo has no parameters)
        """
        if self.diagram.undo():
            self._update_diagram_state()
            self._run_validation()

    def _handle_redo(self, payload: Dict[str, Any]) -> None:
        """Handle redo action.

        Args:
            payload: Empty payload (redo has no parameters)
        """
        if self.diagram.redo():
            self._update_diagram_state()
            self._run_validation()

    def _handle_update_connection_routing(self, payload: Dict[str, Any]) -> None:
        """Handle updateConnectionRouting action.

        Updates the waypoints for a connection's custom routing.

        Args:
            payload: Contains connectionId and waypoints
        """
        connection_id = payload.get("connectionId", "")
        waypoints = payload.get("waypoints", [])

        if self.diagram.update_connection_waypoints(connection_id, waypoints):
            self._update_diagram_state()

    def _handle_reset_connection_routing(self, payload: Dict[str, Any]) -> None:
        """Handle resetConnectionRouting action.

        Resets a connection to automatic routing by clearing waypoints.

        Args:
            payload: Contains connectionId
        """
        connection_id = payload.get("connectionId", "")

        if self.diagram.update_connection_waypoints(connection_id, []):
            self._update_diagram_state()

    def _handle_toggle_connection_label_visibility(
        self, payload: Dict[str, Any]
    ) -> None:
        """Handle toggleConnectionLabelVisibility action.

        Args:
            payload: Contains connectionId
        """
        connection_id = payload.get("connectionId", "")

        # Toggle label visibility via diagram method (with undo support)
        if self.diagram.toggle_connection_label_visibility(connection_id):
            self._update_diagram_state()

    def _handle_update_connection_label(self, payload: Dict[str, Any]) -> None:
        """Handle updateConnectionLabel action.

        Args:
            payload: Contains connectionId and label
        """
        connection_id = payload.get("connectionId", "")
        new_label = payload.get("label", "")

        # Update label via diagram method (with undo support)
        if self.diagram.update_connection_label(connection_id, new_label):
            self._update_diagram_state()
            self._run_validation()

    def _on_save_request(self, change: Dict[str, Any]) -> None:
        """Handle save request from JavaScript.

        Args:
            change: Traitlet change dictionary with filename
        """
        filename = change["new"]
        if not filename:
            return

        try:
            self.diagram.save(filename)
            # Could add a success notification traitlet here in the future
        except Exception as e:
            # Log error (could add error traitlet for UI notification)
            self.logger.error(f"Error saving diagram: {e}")

    def _on_load_request(self, change: Dict[str, Any]) -> None:
        """Handle load request from JavaScript.

        Args:
            change: Traitlet change dictionary with filename
        """
        filename = change["new"]
        if not filename:
            return

        try:
            # Load diagram from file
            loaded_diagram = self.diagram.load(filename)

            # Re-evaluate all expressions against current notebook namespace
            warnings = loaded_diagram.re_evaluate_expressions(
                self._get_notebook_namespace()
            )

            # Log warnings for debugging
            if warnings:
                self.logger.warning("Expression re-evaluation warnings:")
                for warning in warnings:
                    self.logger.warning(f"  - {warning}")

            # Replace current diagram
            self.diagram = loaded_diagram

            # Update UI and run validation
            self._update_diagram_state()
            self._run_validation()

        except FileNotFoundError as e:
            self.logger.error(f"File not found: {e}")
        except Exception as e:
            self.logger.error(f"Error loading diagram: {e}")

    def _on_capture_request(self, change: Dict[str, Any]) -> None:
        """Handle capture request changes.

        This observer exists primarily for future extensibility (e.g., logging).
        The actual capture is handled by JavaScript which reads _capture_request
        and writes to _capture_result.

        Args:
            change: Traitlet change dictionary with 'new' value
        """
        request = change["new"]
        if not request:
            return

        # Log capture request for debugging
        request.get("timestamp", 0)
        request.get("format", "")

    def _handle_update_theme(self, payload: Dict[str, Any]) -> None:
        """Handle updateTheme action from UI.

        Updates the diagram's theme attribute when user selects a theme
        from the settings menu.

        Args:
            payload: Contains theme name
        """
        theme_name = payload.get("theme", "")

        # Validate theme name
        validated = validate_theme_name(theme_name)

        if validated is not None:
            # Update widget traitlet (syncs to JS)
            self.theme = validated

            # Update diagram theme attribute (will be persisted on save)
            if hasattr(self.diagram, "theme"):
                self.diagram.theme = validated

    def _on_theme_change(self, change: Dict[str, Any]) -> None:
        """Observer for theme traitlet changes.

        Keeps diagram.theme in sync with widget.theme.
        This ensures programmatic changes to widget.theme are reflected
        in the diagram object.

        Args:
            change: Traitlet change dictionary with 'new' value
        """
        new_theme = change["new"]

        # Sync to diagram attribute
        if hasattr(self.diagram, "theme"):
            self.diagram.theme = new_theme
