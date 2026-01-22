// SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
//
// SPDX-License-Identifier: GPL-3.0-or-later

/** @type {import('tailwindcss').Config} */
export default {
  content: ["./src/**/*.{js,ts,jsx,tsx}", "./index.html"],
  theme: {
    extend: {
      // Note: In Tailwind v4, colors are defined in styles.css using @theme
      // This config file is primarily for content paths and plugins
      fontFamily: {
        mono: ["SF Mono", "Monaco", "Inconsolata", "Fira Code", "Consolas", "monospace"],
      },
    },
  },
  plugins: [],
};
