// SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
//
// SPDX-License-Identifier: GPL-3.0-or-later

/**
 * Lynx Widget Entry Point
 *
 * anywidget render function that mounts the React app
 */

import React, { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import type { AnyModel } from "@anywidget/types";
import DiagramCanvas from "./DiagramCanvas";
import CaptureCanvas from "./capture/CaptureCanvas";
import "./styles.css";

// Import and re-export context from shared module
import { AnyWidgetModelContext } from "./context/AnyWidgetModel";
export { AnyWidgetModelContext };

/**
 * Root component that switches between DiagramCanvas and CaptureCanvas
 * based on capture mode
 */
function LynxWidget({ model }: { model: AnyModel }) {
  const [captureMode, setCaptureMode] = useState<boolean>(false);

  // Listen for capture mode changes
  useEffect(() => {
    if (!model) return;

    const handleCaptureModeChange = () => {
      const mode = model.get("_capture_mode") as boolean;
      setCaptureMode(mode || false);
    };

    // Initial value
    handleCaptureModeChange();

    // Subscribe to changes
    model.on("change:_capture_mode", handleCaptureModeChange);

    return () => {
      model.off("change:_capture_mode", handleCaptureModeChange);
    };
  }, [model]);

  // Apply capture mode class to container
  const containerClass = captureMode ? "lynx-widget capture-mode" : "lynx-widget";

  return (
    <div className={containerClass}>{captureMode ? <CaptureCanvas /> : <DiagramCanvas />}</div>
  );
}

function render({ model, el }: { model: AnyModel; el: HTMLElement }) {
  // Make the anywidget container background transparent
  el.style.background = "transparent";

  // Inject CSS override as the LAST style element to win over VSCode Jupyter's background styles
  // VSCode applies `background: white!important` to `.cell-output-ipywidget-background`
  // This ensures our transparent override is always last (higher specificity in cascade order)
  const styleId = "lynx-widget-bg-override";
  if (!document.getElementById(styleId)) {
    const style = document.createElement("style");
    style.id = styleId;
    style.textContent = `
      .cell-output-ipywidget-background {
        background: transparent !important;
      }
      .widget-subarea,
      .jupyter-widgets-view {
        background: transparent !important;
      }
    `;
    // Append at the end to ensure it's last
    document.head.appendChild(style);
  }

  const root = createRoot(el);
  root.render(
    <AnyWidgetModelContext.Provider value={model}>
      <LynxWidget model={model} />
    </AnyWidgetModelContext.Provider>
  );

  return () => root.unmount();
}

export default { render };
