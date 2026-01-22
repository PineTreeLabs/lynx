// SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
//
// SPDX-License-Identifier: GPL-3.0-or-later

/**
 * DiagramCanvas - Main React Flow canvas component
 *
 * Displays blocks and connections, handles user interactions
 */

import React, { useCallback, useState, useEffect, useContext, useRef } from "react";
import { AnyWidgetModelContext } from "./index";
import ReactFlow, {
  Background,
  Controls,
  ControlButton,
  Panel,
  // MiniMap, // Commented out - takes up too much space, can restore later if needed
  Node,
  Edge,
  EdgeTypes,
  OnNodesChange,
  OnEdgesChange,
  OnConnect,
  applyNodeChanges,
  applyEdgeChanges,
  Connection as ReactFlowConnection,
  ReactFlowInstance,
} from "reactflow";
import "reactflow/dist/style.css";
import OrthogonalEditableEdge from "./connections/OrthogonalEditableEdge";

import { getDiagramState, onDiagramStateChange, sendAction } from "./utils/traitletSync";
import { findCollinearSnap } from "./utils/collinearSnapping";
import { INTERACTION } from "./config/constants";
import lynxLogo from "./assets/lynx-logo.png";
import type {
  DiagramState,
  Block as DiagramBlock,
  Connection as DiagramConnection,
} from "./utils/traitletSync";
import { nodeTypes } from "./blocks";
import BlockPalette from "./palette/BlockPalette";
import ParameterPanel from "./components/ParameterPanel";
import { ValidationStatusIcon } from "./components/ValidationStatusIcon";
import { BlockContextMenu } from "./components/BlockContextMenu";
import { EdgeContextMenu } from "./components/EdgeContextMenu";
import SettingsMenu from "./components/SettingsMenu";
import { validateThemeName } from "./utils/themeUtils";
import { MENU_CONTAINER, SETTINGS_MENU_POSITION } from "./utils/menuStyles";

/**
 * Map edge types to custom edge components
 */
const edgeTypes: EdgeTypes = {
  orthogonal: OrthogonalEditableEdge,
};

/**
 * Convert backend block to React Flow node
 */
function blockToNode(block: DiagramBlock): Node {
  return {
    id: block.id,
    type: block.type,
    position: block.position,
    data: {
      parameters: block.parameters,
      ports: block.ports,
      label: block.label,
      flipped: block.flipped || false,
      custom_latex: block.custom_latex,
      label_visible: block.label_visible || false,
      width: block.width,
      height: block.height,
    },
  };
}

/**
 * Calculate squared distance between two points (avoids sqrt overhead)
 * Used for drag detection threshold comparison
 */
function calculateDistanceSquared(
  start: { x: number; y: number },
  end: { x: number; y: number }
): number {
  const dx = end.x - start.x;
  const dy = end.y - start.y;
  return dx * dx + dy * dy;
}

export default function DiagramCanvas() {
  const model = useContext(AnyWidgetModelContext);
  const [nodes, setNodes] = useState<Node[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);
  const [selectedBlockId, setSelectedBlockId] = useState<string | null>(null);
  const [diagramState, setDiagramState] = useState<DiagramState | null>(null);
  const [validationResult, setValidationResult] = useState<{
    is_valid: boolean;
    errors: string[];
    warnings: string[];
  } | null>(null);
  const [showSettings, setShowSettings] = useState(false);
  const [currentTheme, setCurrentTheme] = useState<string>("light");
  const [markerColor, setMarkerColor] = useState<string>("#3e4d98"); // Default primary-600 from light theme
  const containerRef = useRef<HTMLDivElement>(null);

  // Context menu state
  const [contextMenu, setContextMenu] = useState<{
    x: number;
    y: number;
    blockId: string;
    blockType: string;
    labelVisible: boolean;
  } | null>(null);

  // Edge context menu state
  const [edgeContextMenu, setEdgeContextMenu] = useState<{
    x: number;
    y: number;
    connectionId: string;
    hasCustomRouting: boolean;
    labelVisible: boolean;
  } | null>(null);

  // Track ReactFlow instance for programmatic control
  const reactFlowInstance = useRef<ReactFlowInstance | null>(null);

  // Track drag start positions for distance calculation (drag detection)
  const dragStartPos = useRef<Record<string, { x: number; y: number }>>({});

  // Subscribe to theme changes from Python
  useEffect(() => {
    if (!model) return;

    // Read initial theme
    const initialTheme = model.get("theme") || "light";
    const validatedTheme = validateThemeName(initialTheme);
    setCurrentTheme(validatedTheme);

    // Apply theme to container
    if (containerRef.current) {
      containerRef.current.setAttribute("data-theme", validatedTheme);
    }

    // Listen for theme changes from Python
    const handleThemeChange = () => {
      const newTheme = model.get("theme") || "light";
      const validated = validateThemeName(newTheme);
      setCurrentTheme(validated);

      // Apply theme to container (pure DOM manipulation for performance)
      if (containerRef.current) {
        containerRef.current.setAttribute("data-theme", validated);
      }
    };

    model.on("change:theme", handleThemeChange);

    return () => {
      model.off("change:theme", handleThemeChange);
    };
  }, [model]);

  // Compute marker color from CSS variable after theme is applied
  useEffect(() => {
    if (!containerRef.current) return;

    // Wait for next frame to ensure theme CSS is applied
    requestAnimationFrame(() => {
      if (!containerRef.current) return;

      const computedStyle = getComputedStyle(containerRef.current);
      const primaryColor = computedStyle.getPropertyValue("--color-primary-600").trim();

      if (primaryColor) {
        setMarkerColor(primaryColor);

        // Update all existing edges to use the new marker color
        setEdges((currentEdges) =>
          currentEdges.map((edge) => ({
            ...edge,
            style: { ...edge.style, stroke: primaryColor },
            markerEnd: edge.markerEnd
              ? {
                  ...edge.markerEnd,
                  color: primaryColor,
                }
              : undefined,
          }))
        );
      }
    });
  }, [currentTheme]);

  // Memoized edge converter that uses current marker color
  const connectionToEdgeWithColor = useCallback(
    (conn: DiagramConnection): Edge => {
      return {
        id: conn.id,
        source: conn.source_block_id,
        sourceHandle: conn.source_port_id,
        target: conn.target_block_id,
        targetHandle: conn.target_port_id,
        type: "orthogonal",
        data: {
          waypoints: conn.waypoints || [],
          label: conn.label,
          label_visible: conn.label_visible || false,
        },
        style: { stroke: markerColor, strokeWidth: 2.5 },
        markerEnd: {
          type: "arrowclosed",
          width: 14,
          height: 14,
          color: markerColor,
        },
      };
    },
    [markerColor]
  );

  // Subscribe to diagram state changes from Python
  useEffect(() => {
    if (!model) return;

    // Initial load
    const initialState = getDiagramState(model);
    setNodes(initialState.blocks.map(blockToNode));
    setEdges(initialState.connections.map(connectionToEdgeWithColor));

    // Subscribe to changes
    const unsubscribe = onDiagramStateChange(model, (state: DiagramState) => {
      // Store full diagram state for parameter panel
      setDiagramState(state);

      /**
       * Smart Merge: Selective State Preservation During Python→React Sync
       *
       * Problem: When Python sends updated state, we need to decide which values to use:
       * - Python's values (authoritative source, handles undo/redo)
       * - React's values (handles in-progress UI operations like dragging)
       *
       * Strategy: Detect significant changes and trust Python, otherwise preserve React.
       * This prevents:
       * - Position jumping during drag operations (Python round-trip delay)
       * - Label flickering during editing (Python state snapshot)
       * - Selection state loss (UI-only concern, not managed by Python)
       */
      setNodes((currentNodes) => {
        const newNodes = state.blocks.map(blockToNode);

        // Create lookup map for O(1) access
        const currentNodesMap = new Map(currentNodes.map((node) => [node.id, node]));

        return newNodes.map((newNode) => {
          const currentNode = currentNodesMap.get(newNode.id);

          if (currentNode) {
            // Detect position changes from Python (undo/redo, programmatic moves)
            // Use threshold to avoid floating-point comparison issues
            const pythonPos = newNode.position;
            const reactPos = currentNode.position;
            const positionChanged =
              Math.abs(pythonPos.x - reactPos.x) > INTERACTION.positionChangeThresholdPx ||
              Math.abs(pythonPos.y - reactPos.y) > INTERACTION.positionChangeThresholdPx;

            // Detect label changes from Python (undo/redo, external edits)
            const pythonLabel = newNode.data.label;
            const reactLabel = currentNode.data.label;
            const labelChanged = pythonLabel !== reactLabel;

            const mergedNode = {
              ...newNode,

              // Position: Trust Python if changed significantly (undo/redo),
              // otherwise preserve React's value (in-progress drag).
              // Always create new object {...} to force React Flow re-render.
              position: positionChanged ? newNode.position : { ...currentNode.position },

              // Label: Trust Python if changed (undo/redo), otherwise preserve React.
              // Prevents label flickering during Python round-trip.
              data: {
                ...newNode.data,
                label: labelChanged ? pythonLabel : reactLabel,
              },

              // Selection: Always preserve React's selection state.
              // This is UI-only state that Python doesn't manage.
              // Required for keyboard delete and visual feedback.
              selected: currentNode.selected || false,
            };

            return mergedNode;
          }

          // New node: Use Python's values directly (no React state to preserve)
          return newNode;
        });
      });

      // Edges can be safely recreated (no local state)
      setEdges(state.connections.map(connectionToEdgeWithColor));
    });

    return unsubscribe;
  }, [model, connectionToEdgeWithColor]);

  // Subscribe to validation result changes from Python
  useEffect(() => {
    if (!model) return;

    const handleValidationChange = () => {
      const result = model.get("validation_result");
      if (result && (result.errors?.length > 0 || result.warnings?.length > 0)) {
        setValidationResult(result);
      } else {
        // Clear validation if no errors/warnings
        setValidationResult(null);
      }
    };

    // Initial load
    handleValidationChange();

    // Subscribe to changes
    model.on("change:validation_result", handleValidationChange);

    return () => {
      model.off("change:validation_result", handleValidationChange);
    };
  }, [model]);

  // Handle node changes (position, selection, removal)
  // Track edges that should be suppressed (connected to nodes being deleted)
  const suppressedEdges = useRef<Set<string>>(new Set());

  const onNodesChange: OnNodesChange = useCallback(
    (changes) => {
      // For each node being removed, find and suppress its connected edges
      changes.forEach((change) => {
        if (change.type === "remove") {
          // Find all edges connected to this node BEFORE applying changes
          edges.forEach((edge) => {
            if (edge.source === change.id || edge.target === change.id) {
              suppressedEdges.current.add(edge.id);
            }
          });
        }
      });

      // Drag Detection: Filter position changes based on 5-pixel movement threshold
      // This implements click-to-select (< 5px) vs drag-to-move (≥ 5px) behavior
      const filteredChanges = changes.filter((change) => {
        // Only process when drag completes (dragging: false)
        if (change.type === "position" && !change.dragging) {
          const startPos = dragStartPos.current[change.id];
          // Get final position from nodes state since change.position might be undefined
          const currentNode = nodes.find((n) => n.id === change.id);
          const finalPos =
            change.position ||
            ("positionAbsolute" in change ? change.positionAbsolute : undefined) ||
            currentNode?.position;

          if (startPos && finalPos) {
            // Calculate squared distance to avoid expensive sqrt() call
            const distanceSquared = calculateDistanceSquared(startPos, finalPos);
            const THRESHOLD_SQUARED = INTERACTION.dragThresholdPx * INTERACTION.dragThresholdPx;

            // Small movement (< threshold): treat as click-to-select
            if (distanceSquared < THRESHOLD_SQUARED) {
              // Select this block exclusively, clear others
              setNodes((nds) =>
                nds.map((n) => ({
                  ...n,
                  selected: n.id === change.id,
                }))
              );
              // Clean up tracking state and prevent position update
              delete dragStartPos.current[change.id];
              return false; // Filter out this position change
            }

            // Large movement (≥ 5px): treat as drag-to-move
            // Selection was already cleared in onNodeDragStart, so nothing to do here
            // Just clean up tracking state
            delete dragStartPos.current[change.id];
          }
        }
        return true; // Apply all other changes (dimensions, remove, etc.)
      });

      setNodes((nds) => applyNodeChanges(filteredChanges, nds));

      // Send deletion events to Python
      changes.forEach((change) => {
        if (change.type === "remove") {
          sendAction(model, "deleteBlock", {
            blockId: change.id,
          });
        }
      });
    },
    [model, edges, nodes]
  );

  // Keyboard shortcuts
  useEffect(() => {
    if (!model) return;

    const handleKeyDown = (event: KeyboardEvent) => {
      // Check if user is typing in an input/textarea
      const target = event.target as HTMLElement;
      const isInputField =
        target.tagName === "INPUT" || target.tagName === "TEXTAREA" || target.isContentEditable;

      // Undo: Ctrl+Z (Cmd+Z on Mac)
      if (
        (event.ctrlKey || event.metaKey) &&
        event.key === "z" &&
        !event.shiftKey &&
        !isInputField
      ) {
        event.preventDefault();
        sendAction(model, "undo", {});
        return;
      }

      // Redo: Ctrl+Y or Ctrl+Shift+Z (Cmd+Shift+Z on Mac)
      if (
        ((event.ctrlKey || event.metaKey) && event.key === "y") ||
        ((event.ctrlKey || event.metaKey) && event.shiftKey && event.key === "z")
      ) {
        if (!isInputField) {
          event.preventDefault();
          sendAction(model, "redo", {});
          return;
        }
      }

      // Delete/Backspace: Remove selected nodes
      if ((event.key === "Delete" || event.key === "Backspace") && !isInputField) {
        event.preventDefault();

        // Get selected nodes and trigger removal
        setNodes((nodes) => {
          const selectedNodes = nodes.filter((node) => node.selected);

          // Trigger onNodesChange with remove events
          if (selectedNodes.length > 0) {
            const removeChanges = selectedNodes.map((node) => ({
              id: node.id,
              type: "remove" as const,
            }));
            onNodesChange(removeChanges);
          }

          return nodes;
        });
        return;
      }

      // Spacebar: Zoom to fit
      if (event.key === " " && !isInputField) {
        event.preventDefault();
        reactFlowInstance.current?.fitView({ padding: 0.4, minZoom: 0.3, maxZoom: 1 });
        return;
      }

      // Skip block shortcuts if typing in input field
      if (isInputField) return;

      // Block addition shortcuts
      const blockShortcuts: { [key: string]: string } = {
        g: "gain",
        s: "sum",
        t: "transfer_function",
        i: "io_marker", // Input
        o: "io_marker", // Output (will need to distinguish in handler if needed)
      };

      const blockType = blockShortcuts[event.key.toLowerCase()];
      if (blockType && !event.ctrlKey && !event.metaKey && !event.altKey) {
        event.preventDefault();

        // Generate unique ID
        const blockId = `${blockType}_${Date.now()}`;

        // Determine marker type for I/O blocks
        const isInput = event.key.toLowerCase() === "i";
        const markerType = isInput ? "input" : "output";

        // Get canvas center for new block position
        const centerX = 400; // Default center-ish position
        const centerY = 300;

        // Send addBlock action
        const payload: Record<string, unknown> = {
          blockId,
          blockType,
          position: { x: centerX, y: centerY },
        };

        // Add type-specific parameters
        if (blockType === "gain") {
          payload.K = 1.0;
        } else if (blockType === "sum") {
          payload.signs = ["+", "+"];
        } else if (blockType === "transfer_function") {
          payload.numerator = [1];
          payload.denominator = [1, 1];
        } else if (blockType === "io_marker") {
          payload.marker_type = markerType;
          payload.label = isInput ? "u" : "y";
        }

        sendAction(model, "addBlock", payload);
      }
    };

    // Add keyboard listener
    window.addEventListener("keydown", handleKeyDown);

    // Cleanup
    return () => {
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [model, onNodesChange]);

  // Handle drag start - clear waypoints immediately for WYSIWYG preview
  const onNodeDragStart = useCallback((_event: React.MouseEvent, node: Node) => {
    // Store initial position for distance calculation (drag detection)
    dragStartPos.current[node.id] = { x: node.position.x, y: node.position.y };

    // Clear selection immediately when drag starts (≥5px movement detected)
    // This ensures resize handles don't show during drag preview (FR-002, FR-005, SC-003)
    // Note: onNodeDragStart only fires when movement ≥ 5px (nodeDragThreshold={5})
    setNodes((nds) =>
      nds.map((n) => ({
        ...n,
        selected: false,
      }))
    );

    // Clear waypoints locally for immediate auto-routing preview
    setEdges((currentEdges) =>
      currentEdges.map((edge) => {
        if (edge.source === node.id || edge.target === node.id) {
          // Clear waypoints for connections to/from this block
          return {
            ...edge,
            data: {
              ...edge.data,
              waypoints: [],
            },
          };
        }
        return edge;
      })
    );
  }, []);

  // Handle drag completion - send position updates to Python
  const onNodeDragStop = useCallback(
    (_event: React.MouseEvent, node: Node) => {
      // Apply collinear snapping (snap to create straight connections)
      const finalPosition = findCollinearSnap(node.id, node.position, nodes, edges, 20);

      // Update local React state immediately for smooth UX
      if (finalPosition.x !== node.position.x || finalPosition.y !== node.position.y) {
        setNodes((currentNodes) =>
          currentNodes.map((n) => (n.id === node.id ? { ...n, position: finalPosition } : n))
        );
      }

      // Send snapped position to Python
      sendAction(model, "moveBlock", {
        blockId: node.id,
        position: finalPosition,
      });
    },
    [model, nodes, edges]
  );

  // Handle connection creation (drag between ports)
  const onConnect: OnConnect = useCallback(
    (connection: ReactFlowConnection) => {
      if (!connection.source || !connection.target) return;

      // Generate unique connection ID
      const connectionId = `conn_${Date.now()}`;

      // Send addConnection action to Python
      sendAction(model, "addConnection", {
        connectionId,
        sourceBlockId: connection.source,
        sourcePortId: connection.sourceHandle || "out",
        targetBlockId: connection.target,
        targetPortId: connection.targetHandle || "in",
      });
    },
    [model]
  );

  // Handle edge changes (including deletion)
  const onEdgesChange: OnEdgesChange = useCallback(
    (changes) => {
      setEdges((eds) => {
        const updatedEdges = applyEdgeChanges(changes, eds);

        // Send deletion events to Python, but ONLY for explicit edge deletions
        // (not for edges deleted as part of node deletion cascade)
        changes.forEach((change) => {
          if (change.type === "remove") {
            // Check if this edge is suppressed (part of node deletion)
            if (suppressedEdges.current.has(change.id)) {
              // This edge is being auto-deleted by React Flow due to node deletion
              // Python will cascade the deletion, so don't send deleteConnection
              suppressedEdges.current.delete(change.id);
            } else {
              // This is an explicit edge deletion (user clicked X on edge)
              sendAction(model, "deleteConnection", {
                connectionId: change.id,
              });
            }
          }
        });

        return updatedEdges;
      });
    },
    [model]
  );

  // Handle block selection (single-click for resize handles only)
  const onNodeClick = useCallback(() => {
    // NOTE: Selection is now handled entirely by drag detection in onNodesChange
    // This prevents the flicker of resize handles before drag starts
    // Selection will only be applied if drag completes with < 5px movement

    // Close settings menu when clicking on a block
    setShowSettings(false);
  }, []);

  // Handle block double-click (opens parameter panel)
  const onNodeDoubleClick = useCallback(
    (_event: React.MouseEvent, node: Node) => {
      // Update our custom selectedBlockId for ParameterPanel
      setSelectedBlockId(node.id);
      if (model) {
        model.set("selected_block_id", node.id);
        model.save_changes();
      }
    },
    [model]
  );

  // Handle canvas click (deselect)
  const onPaneClick = useCallback(() => {
    // Clear our custom selectedBlockId
    setSelectedBlockId(null);
    if (model) {
      model.set("selected_block_id", null);
      model.save_changes();
    }

    // Clear React Flow's selection state
    setNodes((nodes) =>
      nodes.map((n) => ({
        ...n,
        selected: false, // Deselect all nodes
      }))
    );

    // Close context menus
    setContextMenu(null);
    setEdgeContextMenu(null);
    // Close settings menu when clicking on canvas
    setShowSettings(false);
  }, [model]);

  // Handle right-click on node
  const onNodeContextMenu = useCallback((event: React.MouseEvent, node: Node) => {
    event.preventDefault();

    setContextMenu({
      x: event.clientX,
      y: event.clientY,
      blockId: node.id,
      blockType: node.type || "unknown",
      labelVisible: node.data?.label_visible || false,
    });
  }, []);

  // Handle block flip
  const handleFlipBlock = useCallback(
    (blockId: string) => {
      if (model) {
        sendAction(model, "flipBlock", { blockId });
      }
    },
    [model]
  );

  // Handle toggle label visibility
  const handleToggleLabelVisibility = useCallback(
    (blockId: string) => {
      if (model) {
        sendAction(model, "toggleLabelVisibility", { blockId });
      }
    },
    [model]
  );

  // Handle block delete
  const handleDeleteBlock = useCallback(
    (blockId: string) => {
      if (model) {
        sendAction(model, "deleteBlock", { blockId });
      }
    },
    [model]
  );

  // Handle edge right-click for context menu
  const onEdgeContextMenu = useCallback((event: React.MouseEvent, edge: Edge) => {
    event.preventDefault();

    // Check if edge has custom waypoints
    const waypoints = edge.data?.waypoints || [];
    const hasCustomRouting = waypoints.length > 0;
    const labelVisible = edge.data?.label_visible || false;

    setEdgeContextMenu({
      x: event.clientX,
      y: event.clientY,
      connectionId: edge.id,
      hasCustomRouting,
      labelVisible,
    });
  }, []);

  // Handle toggle connection label visibility
  const handleToggleConnectionLabelVisibility = useCallback(
    (connectionId: string) => {
      if (model) {
        sendAction(model, "toggleConnectionLabelVisibility", { connectionId });
      }
    },
    [model]
  );

  // Handle reset routing to auto
  const handleResetRouting = useCallback(
    (connectionId: string) => {
      if (model) {
        sendAction(model, "resetConnectionRouting", { connectionId });
      }
    },
    [model]
  );

  // Handle delete connection
  const handleDeleteConnection = useCallback(
    (connectionId: string) => {
      if (model) {
        sendAction(model, "deleteConnection", { connectionId });
      }
    },
    [model]
  );

  // Handle parameter updates
  const handleParameterUpdate = useCallback(
    (blockId: string, parameterName: string, value: unknown) => {
      // Route label updates to updateBlockLabel action (Feature 013)
      if (parameterName === "label") {
        sendAction(model, "updateBlockLabel", {
          blockId,
          label: value,
        });
      } else {
        sendAction(model, "updateParameter", {
          blockId,
          parameterName,
          value,
        });
      }
    },
    [model]
  );

  // Handle theme change from UI
  const handleThemeChange = useCallback(
    (theme: string) => {
      if (model) {
        sendAction(model, "updateTheme", { theme });
      }
    },
    [model]
  );

  // Find selected block from diagram state
  const selectedBlock = diagramState?.blocks.find((b) => b.id === selectedBlockId) || null;

  return (
    <div ref={containerRef} className="lynx-widget" data-theme={currentTheme}>
      <BlockPalette />
      <ParameterPanel
        block={selectedBlock}
        onUpdate={handleParameterUpdate}
        onClose={() => setSelectedBlockId(null)}
      />
      {/* Context menu for blocks */}
      {contextMenu && (
        <BlockContextMenu
          x={contextMenu.x}
          y={contextMenu.y}
          blockId={contextMenu.blockId}
          blockType={contextMenu.blockType}
          labelVisible={contextMenu.labelVisible}
          onDelete={() => handleDeleteBlock(contextMenu.blockId)}
          onFlip={() => handleFlipBlock(contextMenu.blockId)}
          onToggleLabel={() => handleToggleLabelVisibility(contextMenu.blockId)}
          onClose={() => setContextMenu(null)}
        />
      )}
      {/* Context menu for edges/connections */}
      {edgeContextMenu && (
        <EdgeContextMenu
          x={edgeContextMenu.x}
          y={edgeContextMenu.y}
          connectionId={edgeContextMenu.connectionId}
          hasCustomRouting={edgeContextMenu.hasCustomRouting}
          labelVisible={edgeContextMenu.labelVisible}
          onToggleLabel={() => handleToggleConnectionLabelVisibility(edgeContextMenu.connectionId)}
          onResetRouting={() => handleResetRouting(edgeContextMenu.connectionId)}
          onDelete={() => handleDeleteConnection(edgeContextMenu.connectionId)}
          onClose={() => setEdgeContextMenu(null)}
        />
      )}
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onNodeClick={onNodeClick}
        onNodeDoubleClick={onNodeDoubleClick}
        onNodeDragStart={onNodeDragStart}
        onNodeDragStop={onNodeDragStop}
        onNodeContextMenu={onNodeContextMenu}
        onEdgeContextMenu={onEdgeContextMenu}
        onPaneClick={onPaneClick}
        onInit={(instance) => {
          reactFlowInstance.current = instance;
        }}
        nodeTypes={nodeTypes}
        edgeTypes={edgeTypes}
        nodeDragThreshold={5}
        fitView
        fitViewOptions={{ padding: 0.4, minZoom: 0.3, maxZoom: 1 }}
        defaultViewport={{ x: 0, y: 0, zoom: 0.5 }}
        minZoom={0.3}
        maxZoom={2}
        connectionMode="loose"
        isValidConnection={() => true}
        defaultEdgeOptions={{
          style: { stroke: markerColor, strokeWidth: 2.5 },
          type: "orthogonal",
          markerEnd: {
            type: "arrowclosed",
            width: 16,
            height: 16,
            color: markerColor,
          },
        }}
        style={{ backgroundColor: "var(--color-slate-50)" }}
        defaultMarkerColor={markerColor}
        proOptions={{ hideAttribution: true }}
      >
        <Background
          color="var(--color-slate-300)"
          gap={20}
          size={0.2}
          variant="lines"
          style={{ opacity: 0.1 }}
        />
        <Controls showInteractive={false} showZoom={false} showFitView={false}>
          {/* Custom zoom-to-fit button with padding: 0.4 */}
          <ControlButton
            onClick={() =>
              reactFlowInstance.current?.fitView({ padding: 0.4, minZoom: 0.3, maxZoom: 1 })
            }
            title="Zoom to Fit (Spacebar)"
          >
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">
              <path
                fill="currentColor"
                d="M3 3 L10 3 L10 5 L5 5 L5 10 L3 10 Z M22 3 L29 3 L29 10 L27 10 L27 5 L22 5 Z M3 22 L5 22 L5 27 L10 27 L10 29 L3 29 Z M22 27 L22 29 L29 29 L29 22 L27 22 L27 27 Z"
              />
            </svg>
          </ControlButton>
          {/* Validation status button - always visible, shows ✓/⚠/❌ */}
          <ValidationStatusIcon validationResult={validationResult} />
          <ControlButton onClick={() => setShowSettings(!showSettings)} title="Settings">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="var(--color-slate-700)"
              style={{
                width: "100%",
                height: "100%",
                transform: "scale(1.25)",
              }}
            >
              {/* Solid gear/cog icon - scaled 25% larger */}
              <path
                fillRule="evenodd"
                d="M11.078 2.25c-.917 0-1.699.663-1.85 1.567L9.05 4.889c-.02.12-.115.26-.297.348a7.493 7.493 0 0 0-.986.57c-.166.115-.334.126-.45.083L6.3 5.508a1.875 1.875 0 0 0-2.282.819l-.922 1.597a1.875 1.875 0 0 0 .432 2.385l.84.692c.095.078.17.229.154.43a7.598 7.598 0 0 0 0 1.139c.015.2-.059.352-.153.43l-.841.692a1.875 1.875 0 0 0-.432 2.385l.922 1.597a1.875 1.875 0 0 0 2.282.818l1.019-.382c.115-.043.283-.031.45.082.312.214.641.405.985.57.182.088.277.228.297.35l.178 1.071c.151.904.933 1.567 1.85 1.567h1.844c.916 0 1.699-.663 1.85-1.567l.178-1.072c.02-.12.114-.26.297-.349.344-.165.673-.356.985-.57.167-.114.335-.125.45-.082l1.02.382a1.875 1.875 0 0 0 2.28-.819l.923-1.597a1.875 1.875 0 0 0-.432-2.385l-.84-.692c-.095-.078-.17-.229-.154-.43a7.614 7.614 0 0 0 0-1.139c-.016-.2.059-.352.153-.43l.84-.692c.708-.582.891-1.59.433-2.385l-.922-1.597a1.875 1.875 0 0 0-2.282-.818l-1.02.382c-.114.043-.282.031-.449-.083a7.49 7.49 0 0 0-.985-.57c-.183-.087-.277-.227-.297-.348l-.179-1.072a1.875 1.875 0 0 0-1.85-1.567h-1.843zM12 15.75a3.75 3.75 0 1 0 0-7.5 3.75 3.75 0 0 0 0 7.5z"
                clipRule="evenodd"
              />
            </svg>
          </ControlButton>
        </Controls>
        {/* Settings menu - cascades to the right of controls */}
        {showSettings && (
          <div
            style={{
              ...MENU_CONTAINER,
              ...SETTINGS_MENU_POSITION,
            }}
          >
            {/* <div
              style={{
                padding: "8px 12px 4px 12px",
                fontSize: "14px",
                fontWeight: "bold",
                color: "var(--color-slate-700)",
                borderBottom: "1px solid var(--color-slate-200)",
                marginBottom: "4px",
              }}
            >
              Settings
            </div> */}
            <SettingsMenu
              activeTheme={currentTheme}
              onThemeChange={handleThemeChange}
              onClose={() => setShowSettings(false)}
            />
          </div>
        )}
        {/* MiniMap - Commented out to save space on small canvases, can restore later if needed
        <MiniMap
          nodeColor="var(--color-primary-400)"
          maskColor="var(--color-primary-400)"
          style={{ opacity: 0.6 }}
        />
        */}
        {/* Custom Lynx attribution panel */}
        <Panel position="bottom-right" style={{ margin: 0, padding: 0 }}>
          <a
            href="https://github.com/jcallaham/lynx-dev"
            target="_blank"
            rel="noopener noreferrer"
            style={{
              display: "flex",
              alignItems: "center",
              gap: "4px",
              padding: "2px 6px",
              backgroundColor: "var(--color-slate-100)",
              border: "1px solid var(--color-slate-200)",
              borderRadius: "3px",
              textDecoration: "none",
              fontSize: "12px",
              color: "var(--color-slate-500)",
              fontWeight: 500,
              transition: "all 0.2s ease",
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = "var(--color-slate-50)";
              e.currentTarget.style.color = "var(--color-slate-700)";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = "var(--color-slate-50)";
              e.currentTarget.style.color = "var(--color-slate-500)";
            }}
          >
            <img
              src={lynxLogo}
              alt="Lynx"
              style={{
                height: "14px",
                width: "auto",
                display: "block",
              }}
            />
            <span>Lynx</span>
          </a>
        </Panel>
      </ReactFlow>
    </div>
  );
}
