// SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
//
// SPDX-License-Identifier: GPL-3.0-or-later

/**
 * AnyWidgetModel Context
 *
 * Shared context for the anywidget model, extracted for easier testing.
 */

import { createContext } from "react";
import type { AnyModel } from "@anywidget/types";

// Create custom context for anywidget model
export const AnyWidgetModelContext = createContext<AnyModel | null>(null);
