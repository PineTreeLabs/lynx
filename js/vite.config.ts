// SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import anywidget from "@anywidget/vite";
import tailwindcss from "@tailwindcss/vite";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss(), anywidget()],
  define: {
    // Fix "process is not defined" error in browser
    "process.env.NODE_ENV": JSON.stringify("production"),
  },
  build: {
    // Output to anywidget static directory
    outDir: "../src/lynx/static",
    // Generate source maps for debugging
    sourcemap: true,
    // Clear output directory before build
    emptyOutDir: true,
    // Library mode for anywidget
    lib: {
      entry: "./src/index.tsx",
      formats: ["es"],
      fileName: "index",
    },
  },
  resolve: {
    alias: {
      // Enable @ imports from src/
      "@": "/src",
    },
  },
  test: {
    globals: true,
    environment: "jsdom",
    setupFiles: "./src/test/setup.ts",
    // Run tests sequentially in CI for stability (trade speed for reliability)
    // Parallel execution can cause race conditions with timers and React rendering
    pool: process.env.CI ? "forks" : "threads",
    poolOptions: {
      forks: {
        singleFork: true, // Run all tests in a single process in CI
      },
    },
    // Isolate each test file
    isolate: true,
    coverage: {
      provider: "v8",
      reporter: ["text", "json", "html"],
      exclude: ["node_modules/", "src/test/", "**/*.d.ts", "**/*.config.*", "**/mockData"],
    },
  },
});
