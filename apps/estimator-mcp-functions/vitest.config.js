import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    globals: true,
    environment: 'node',
    include: ['**/*.test.js', '**/*.spec.js'],
    exclude: ['node_modules/**', 'packages/**/node_modules/**']
  }
});
