import { defineConfig } from 'vite';
import { fileURLToPath, URL } from 'node:url';
export default defineConfig({
  base: './',
  server: { cors: true },
  preview: { cors: true },
  resolve: { alias: [
    { find: '@designcodeio/threeui/style.css', replacement: fileURLToPath(new URL('./src/shaders/threeui.css', import.meta.url)) },
    { find: '@designcodeio/threeui', replacement: fileURLToPath(new URL('./src/threeui.js', import.meta.url)) },
  ] },
  esbuild: { jsx: 'automatic' },
});
