// SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
//
// SPDX-License-Identifier: GPL-3.0-or-later

/**
 * Structured logging for Lynx frontend
 *
 * Provides leveled logging with consistent formatting.
 */

export enum LogLevel {
  DEBUG,
  INFO,
  WARN,
  ERROR,
}

class Logger {
  constructor(
    private name: string,
    private level: LogLevel = LogLevel.INFO
  ) {}

  private log(level: LogLevel, message: string, context?: Record<string, unknown>): void {
    if (level < this.level) return;

    const timestamp = new Date().toISOString();
    const levelName = LogLevel[level];
    const prefix = `[${timestamp}] [${levelName}] [${this.name}]`;

    if (context) {
      console.log(`${prefix} ${message}`, context);
    } else {
      console.log(`${prefix} ${message}`);
    }
  }

  debug(msg: string, ctx?: Record<string, unknown>) {
    this.log(LogLevel.DEBUG, msg, ctx);
  }
  info(msg: string, ctx?: Record<string, unknown>) {
    this.log(LogLevel.INFO, msg, ctx);
  }
  warn(msg: string, ctx?: Record<string, unknown>) {
    this.log(LogLevel.WARN, msg, ctx);
  }
  error(msg: string, ctx?: Record<string, unknown>) {
    this.log(LogLevel.ERROR, msg, ctx);
  }
}

export const createLogger = (name: string) => new Logger(name);
