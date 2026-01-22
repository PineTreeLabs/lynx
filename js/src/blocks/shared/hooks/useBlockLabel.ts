// SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
//
// SPDX-License-Identifier: GPL-3.0-or-later

/**
 * Custom hook for managing block labels with optimistic updates
 *
 * Encapsulates the common label handling logic used by all block types.
 * Updates React state immediately and syncs to Python in background.
 */

import { useCallback, useContext } from "react";
import { AnyWidgetModelContext } from "../../../index";
import { sendAction } from "../../../utils/traitletSync";

interface BlockData {
  label?: string;
  [key: string]: unknown;
}

/**
 * Hook for block label management
 *
 * @param id - Block ID
 * @param data - Block data containing label
 * @returns Object with blockLabel and handleLabelSave
 */
export function useBlockLabel(id: string, data: BlockData) {
  const model = useContext(AnyWidgetModelContext);

  // Get block label (use data.label if available, otherwise use node id)
  const blockLabel = data.label || id;

  // Handle label updates (send to Python, no optimistic update)
  const handleLabelSave = useCallback(
    (newLabel: string) => {
      // Send to Python - no optimistic update (prevents undo/redo rendering issues)
      if (model) {
        sendAction(model, "updateBlockLabel", {
          blockId: id,
          label: newLabel,
        });
      }
    },
    [model, id]
  );

  return { blockLabel, handleLabelSave };
}
