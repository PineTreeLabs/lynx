// SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
//
// SPDX-License-Identifier: GPL-3.0-or-later

/**
 * Test data factories for frontend tests
 */

import type { Block, DiagramState } from "../utils/traitletSync";
import { BLOCK_TYPES } from "../config/constants";

export class BlockFactory {
  static gain(overrides: Partial<Block> = {}): Block {
    return {
      id: "g1",
      type: BLOCK_TYPES.GAIN,
      position: { x: 100, y: 100 },
      parameters: [{ name: "K", value: 1.0 }],
      ports: [
        { id: "in", type: "input" },
        { id: "out", type: "output" },
      ],
      label: "g1",
      flipped: false,
      label_visible: false,
      ...overrides,
    };
  }

  static sum(overrides: Partial<Block> = {}): Block {
    return {
      id: "s1",
      type: BLOCK_TYPES.SUM,
      position: { x: 100, y: 100 },
      parameters: [{ name: "signs", value: ["+", "+", "|"] }],
      ports: [
        { id: "in1", type: "input" },
        { id: "in2", type: "input" },
        { id: "out", type: "output" },
      ],
      label: "s1",
      flipped: false,
      label_visible: false,
      ...overrides,
    };
  }

  static transferFunction(overrides: Partial<Block> = {}): Block {
    return {
      id: "tf1",
      type: BLOCK_TYPES.TRANSFER_FUNCTION,
      position: { x: 100, y: 100 },
      parameters: [
        { name: "numerator", value: [1] },
        { name: "denominator", value: [1, 1] },
      ],
      ports: [
        { id: "in", type: "input" },
        { id: "out", type: "output" },
      ],
      label: "tf1",
      flipped: false,
      label_visible: false,
      ...overrides,
    };
  }

  static stateSpace(overrides: Partial<Block> = {}): Block {
    return {
      id: "ss1",
      type: BLOCK_TYPES.STATE_SPACE,
      position: { x: 100, y: 100 },
      parameters: [
        {
          name: "A",
          value: [
            [0, 1],
            [-1, -1],
          ],
        },
        { name: "B", value: [[0], [1]] },
        { name: "C", value: [[1, 0]] },
        { name: "D", value: [[0]] },
      ],
      ports: [
        { id: "in", type: "input" },
        { id: "out", type: "output" },
      ],
      label: "ss1",
      flipped: false,
      label_visible: false,
      ...overrides,
    };
  }

  static ioMarker(overrides: Partial<Block> = {}): Block {
    return {
      id: "io1",
      type: BLOCK_TYPES.IO_MARKER,
      position: { x: 100, y: 100 },
      parameters: [
        { name: "marker_type", value: "input" },
        { name: "label", value: "u" },
      ],
      ports: [{ id: "out", type: "output" }],
      label: "io1",
      flipped: false,
      label_visible: false,
      ...overrides,
    };
  }
}

export class DiagramFactory {
  static empty(): DiagramState {
    return { version: "1.0.0", blocks: [], connections: [] };
  }

  static withBlocks(blocks: Block[]): DiagramState {
    return { version: "1.0.0", blocks, connections: [] };
  }
}
