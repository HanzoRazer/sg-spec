import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    include: ["agentic-ai/tests/**/*.test.ts"],
    globals: false,
  },
});
