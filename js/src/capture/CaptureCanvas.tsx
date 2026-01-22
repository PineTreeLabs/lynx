// SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
//
// SPDX-License-Identifier: GPL-3.0-or-later

/**
 * CaptureCanvas - Minimal canvas component for static diagram export
 *
 * Renders diagram without UI chrome (palette, controls, background dots, context menus).
 * Used by the capture system to generate PNG/SVG exports.
 */

import React, { useCallback, useMemo, useState, useEffect, useContext, useRef } from "react";
import { AnyWidgetModelContext } from "../index";
import ReactFlow, { Node, Edge, EdgeTypes, ReactFlowInstance, ReactFlowProvider } from "reactflow";
import "reactflow/dist/style.css";
import OrthogonalEditableEdge from "../connections/OrthogonalEditableEdge";

import { getDiagramState, onDiagramStateChange } from "../utils/traitletSync";
import type {
  DiagramState,
  Block as DiagramBlock,
  Connection as DiagramConnection,
} from "../utils/traitletSync";
import { nodeTypes } from "../blocks";
import type { CaptureRequest, CaptureResult } from "./types";
import { captureToPng, captureToSvg, calculateContentBounds } from "./captureUtils";

/**
 * Map edge types to custom edge components
 */
const edgeTypes: EdgeTypes = {
  orthogonal: OrthogonalEditableEdge,
};

/**
 * Default dimensions for each block type (must match BLOCK_DEFAULTS in blockDefaults.ts)
 */
const BLOCK_DEFAULTS: Record<string, { width: number; height: number }> = {
  gain: { width: 120, height: 80 },
  sum: { width: 56, height: 56 },
  transfer_function: { width: 100, height: 50 },
  state_space: { width: 100, height: 60 },
  io_marker: { width: 60, height: 48 },
};

/**
 * Convert backend block to React Flow node
 * Important: width/height must be on the node itself for getNodesBounds to work
 */
function blockToNode(block: DiagramBlock): Node {
  const defaults = BLOCK_DEFAULTS[block.type] || { width: 100, height: 60 };
  const width = block.width ?? defaults.width;
  const height = block.height ?? defaults.height;

  return {
    id: block.id,
    type: block.type,
    position: block.position,
    // Width/height on node for getNodesBounds calculation
    width,
    height,
    data: {
      parameters: block.parameters,
      ports: block.ports,
      label: block.label,
      flipped: block.flipped || false,
      custom_latex: block.custom_latex,
      label_visible: block.label_visible || false,
      width,
      height,
    },
  };
}

/**
 * Convert backend connection to React Flow edge
 */
function connectionToEdge(conn: DiagramConnection): Edge {
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
    markerEnd: {
      type: "arrowclosed",
      width: 14,
      height: 14,
    },
  };
}

interface CaptureCanvasInnerProps {
  nodes: Node[];
  edges: Edge[];
  captureRequest: CaptureRequest | null;
  onCaptureComplete: (result: CaptureResult) => void;
}

/**
 * Inner component that uses React Flow hooks (must be inside ReactFlowProvider)
 */
function CaptureCanvasInner({
  nodes,
  edges,
  captureRequest,
  onCaptureComplete,
}: CaptureCanvasInnerProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const reactFlowInstance = useRef<ReactFlowInstance | null>(null);
  const [isReady, setIsReady] = useState(false);

  // Perform capture when request changes and canvas is ready
  useEffect(() => {
    console.log("[CaptureCanvasInner] Capture effect check:", {
      hasCaptureRequest: !!captureRequest,
      isReady,
      hasContainer: !!containerRef.current,
      hasInstance: !!reactFlowInstance.current,
      nodeCount: nodes.length,
    });

    if (!captureRequest || !isReady || !containerRef.current || !reactFlowInstance.current) {
      return;
    }

    // Wait for nodes to be available
    if (nodes.length === 0) {
      console.log("[CaptureCanvasInner] Waiting for nodes...");
      return;
    }

    const performCapture = async () => {
      try {
        console.log("[CaptureCanvasInner] Starting capture with", nodes.length, "nodes");

        // Calculate natural content bounds (without target dimensions)
        const contentBounds = calculateContentBounds(nodes, null, null);
        console.log("[CaptureCanvasInner] Content bounds:", contentBounds);

        // Determine output dimensions
        const outputWidth = Math.ceil(captureRequest.width ?? contentBounds.width);
        const outputHeight = Math.ceil(captureRequest.height ?? contentBounds.height);

        // Calculate zoom to fit content within output dimensions
        let zoom = 1;
        if (captureRequest.width !== null || captureRequest.height !== null) {
          const scaleX = outputWidth / contentBounds.width;
          const scaleY = outputHeight / contentBounds.height;
          zoom = Math.min(scaleX, scaleY); // Fit while preserving aspect ratio
        }
        console.log("[CaptureCanvasInner] Calculated zoom:", zoom);

        // Resize container to match output dimensions
        if (containerRef.current) {
          containerRef.current.style.width = `${outputWidth}px`;
          containerRef.current.style.height = `${outputHeight}px`;
        }

        // Wait for resize to take effect
        await new Promise((resolve) => setTimeout(resolve, 100));

        // Calculate viewport position to center content within output
        // Content center in canvas coordinates
        const contentCenterX = contentBounds.x + contentBounds.width / 2;
        const contentCenterY = contentBounds.y + contentBounds.height / 2;

        // Viewport position to center scaled content
        const viewportX = outputWidth / 2 - contentCenterX * zoom;
        const viewportY = outputHeight / 2 - contentCenterY * zoom;

        reactFlowInstance.current?.setViewport({
          x: viewportX,
          y: viewportY,
          zoom,
        });

        // Wait for viewport adjustment and rendering to complete
        await new Promise((resolve) => setTimeout(resolve, 200));

        // Get the React Flow viewport element for capture
        const viewportElement = containerRef.current?.querySelector(
          ".react-flow__viewport"
        ) as HTMLElement;

        if (!viewportElement) {
          throw new Error("Could not find React Flow viewport element");
        }

        console.log(
          "[CaptureCanvasInner] Capturing",
          captureRequest.format,
          "at",
          outputWidth,
          "x",
          outputHeight
        );

        let data: string;
        if (captureRequest.format === "png") {
          data = await captureToPng(
            viewportElement,
            outputWidth,
            outputHeight,
            captureRequest.transparent
          );
        } else {
          data = await captureToSvg(viewportElement, outputWidth, outputHeight);
        }

        console.log("[CaptureCanvasInner] Capture successful, data length:", data.length);

        onCaptureComplete({
          success: true,
          data,
          format: captureRequest.format,
          width: outputWidth,
          height: outputHeight,
          timestamp: captureRequest.timestamp,
        });
      } catch (error) {
        console.error("[CaptureCanvasInner] Capture error:", error);
        onCaptureComplete({
          success: false,
          data: "",
          format: captureRequest.format,
          width: 0,
          height: 0,
          error: error instanceof Error ? error.message : "Unknown capture error",
          timestamp: captureRequest.timestamp,
        });
      }
    };

    performCapture();
  }, [captureRequest, isReady, nodes, onCaptureComplete]);

  // Calculate initial viewport to fit all nodes
  const defaultViewport = useMemo(() => {
    if (nodes.length === 0) {
      return { x: 0, y: 0, zoom: 1 };
    }
    // Will be set by fitView
    return { x: 0, y: 0, zoom: 1 };
  }, [nodes]);

  return (
    <div
      ref={containerRef}
      style={{
        width: "100%",
        height: "100%",
        backgroundColor: "transparent",
      }}
    >
      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        edgeTypes={edgeTypes}
        onInit={(instance) => {
          console.log("[CaptureCanvasInner] ReactFlow initialized");
          reactFlowInstance.current = instance;
          // Fit view after init
          instance.fitView({ padding: 0.1 });
          // Mark as ready after a short delay to ensure render is complete
          setTimeout(() => {
            console.log("[CaptureCanvasInner] Setting isReady=true");
            setIsReady(true);
          }, 100);
        }}
        fitView
        fitViewOptions={{ padding: 0.1, minZoom: 0.1, maxZoom: 4 }}
        defaultViewport={defaultViewport}
        minZoom={0.1}
        maxZoom={4}
        nodesDraggable={false}
        nodesConnectable={false}
        elementsSelectable={false}
        panOnDrag={false}
        zoomOnScroll={false}
        zoomOnPinch={false}
        zoomOnDoubleClick={false}
        preventScrolling={false}
        defaultEdgeOptions={{
          style: { stroke: "var(--color-primary-600)", strokeWidth: 2 },
          type: "orthogonal",
          markerEnd: {
            type: "arrowclosed",
          },
        }}
        style={{ backgroundColor: "transparent" }}
        defaultMarkerColor="var(--color-primary-600)"
        proOptions={{ hideAttribution: true }}
      >
        {/* No Background, Controls, MiniMap, or Panels - clean diagram only */}
      </ReactFlow>
    </div>
  );
}

/**
 * CaptureCanvas - Main export component
 *
 * Renders diagram in capture mode and handles capture requests from Python.
 */
export default function CaptureCanvas() {
  const model = useContext(AnyWidgetModelContext);
  const [nodes, setNodes] = useState<Node[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);
  const [captureRequest, setCaptureRequest] = useState<CaptureRequest | null>(null);
  const lastTimestamp = useRef<number>(0);

  // Subscribe to diagram state from Python (like DiagramCanvas does)
  useEffect(() => {
    if (!model) return;

    // Initial load
    const initialState = getDiagramState(model);
    console.log("[CaptureCanvas] Initial state:", initialState.blocks.length, "blocks");
    setNodes(initialState.blocks.map(blockToNode));
    setEdges(initialState.connections.map(connectionToEdge));

    // Subscribe to changes (in case state updates after mount)
    const unsubscribe = onDiagramStateChange(model, (state: DiagramState) => {
      console.log("[CaptureCanvas] State updated:", state.blocks.length, "blocks");
      setNodes(state.blocks.map(blockToNode));
      setEdges(state.connections.map(connectionToEdge));
    });

    return unsubscribe;
  }, [model]);

  // Listen for capture requests from Python
  useEffect(() => {
    if (!model) return;

    const handleCaptureRequest = () => {
      const request = model.get("_capture_request") as CaptureRequest | undefined;
      if (!request || !request.timestamp) return;

      // Skip duplicate requests
      if (request.timestamp <= lastTimestamp.current) return;
      lastTimestamp.current = request.timestamp;

      console.log("[CaptureCanvas] Received capture request:", request);
      setCaptureRequest(request);
    };

    // Listen for changes
    model.on("change:_capture_request", handleCaptureRequest);

    // Check for initial request
    handleCaptureRequest();

    return () => {
      model.off("change:_capture_request", handleCaptureRequest);
    };
  }, [model]);

  // Ref to find our container for DOM manipulation
  const outerRef = useRef<HTMLDivElement>(null);

  // Handle capture completion - display inline or download
  const handleCaptureComplete = useCallback(
    (result: CaptureResult) => {
      if (!model) return;

      console.log("[CaptureCanvas] Capture complete:", result.success ? "success" : result.error);

      if (result.success && result.data) {
        const displayInline = captureRequest?.displayInline ?? true;
        const mimeType = result.format === "png" ? "image/png" : "image/svg+xml";

        if (displayInline) {
          // Display inline - inject <img> into the widget container
          console.log("[CaptureCanvas] Displaying inline");
          console.log("[CaptureCanvas] outerRef.current:", outerRef.current);

          // Find the anywidget container (parent of our React root)
          // Navigate up from our ref to find the .lynx-widget container
          const lynxWidget = outerRef.current?.closest(".lynx-widget");
          console.log("[CaptureCanvas] Found .lynx-widget:", lynxWidget);

          if (lynxWidget) {
            // Create image element
            const img = document.createElement("img");
            img.src = `data:${mimeType};base64,${result.data}`;
            img.style.maxWidth = "100%";
            img.style.display = "block";

            // Replace widget content with the static image
            lynxWidget.innerHTML = "";
            lynxWidget.appendChild(img);

            // Reset the capture-mode styling so image is visible
            lynxWidget.classList.remove("capture-mode");
            (lynxWidget as HTMLElement).style.width = "auto";
            (lynxWidget as HTMLElement).style.height = "auto";
            (lynxWidget as HTMLElement).style.opacity = "1";

            // Also resize the parent containers (ipywidgets/anywidget wrappers)
            // These may have the 1px layout constraint from Python
            let parent = lynxWidget.parentElement;
            while (parent) {
              // Reset any height/width constraints
              const h = parent.style.height;
              const w = parent.style.width;
              if (h === "1px" || w === "1px") {
                parent.style.height = "auto";
                parent.style.width = "auto";
              }
              parent = parent.parentElement;
            }

            console.log("[CaptureCanvas] Image injected successfully");
          } else {
            console.error("[CaptureCanvas] Could not find .lynx-widget container");
            // Fallback: try to find any parent and log the DOM structure
            let parent = outerRef.current?.parentElement;
            console.log("[CaptureCanvas] Parent chain:");
            while (parent) {
              console.log("  -", parent.tagName, parent.className);
              parent = parent.parentElement;
            }
          }
        }
      }

      // Sync result to Python for programmatic access
      model.set("_capture_result", result);
      model.save_changes();

      // Clear request
      setCaptureRequest(null);
    },
    [model, captureRequest]
  );

  return (
    <div
      ref={outerRef}
      style={{
        // Position off-screen but still render at full size
        position: "fixed",
        left: "-10000px",
        top: "-10000px",
        // Initial size - will be resized during capture
        width: "800px",
        height: "600px",
      }}
    >
      <ReactFlowProvider>
        <CaptureCanvasInner
          nodes={nodes}
          edges={edges}
          captureRequest={captureRequest}
          onCaptureComplete={handleCaptureComplete}
        />
      </ReactFlowProvider>
    </div>
  );
}
