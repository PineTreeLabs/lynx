// SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
//
// SPDX-License-Identifier: GPL-3.0-or-later

/**
 * Shared utilities used by multiple blocks
 */

export { BLOCK_DEFAULTS, getBlockDimensions, getBlockMinDimensions } from "./blockDefaults";
export {
  generateGainLatex,
  generateTransferFunctionLatex,
  generateStateSpaceLatex,
} from "./latexGeneration";
export { calculatePortMarkerPoints, isIsoscelesTriangle } from "./portMarkerGeometry";
