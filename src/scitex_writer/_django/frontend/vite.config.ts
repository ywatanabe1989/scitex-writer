import { fileURLToPath } from "url";
import { resolve } from "path";
import { defineConfig } from "vite";

const __dirname = fileURLToPath(new URL(".", import.meta.url));

// `@scitex/ui/*` resolves through the package's own `exports` map via the npm
// `file:` link (node_modules/@scitex/ui → the sibling scitex-ui checkout), the
// same way tsc resolves it. The build therefore no longer depends on the
// installed `scitex_ui` Python package.
//
// A previous alias pointed `@scitex/ui` at the scitex-ui repo root and
// raw-appended subpaths. That broke once scitex-ui moved to exports subpaths at
// varying depths (e.g. `./monaco-editor` → `ts/app/monaco-editor/index.ts`):
// the alias produced `<root>/monaco-editor`, which does not exist. tsc resolves
// via exports, the alias did not — so the mismatch only surfaced at build time,
// never at typecheck.
export default defineConfig({
  base: "/static/writer/",
  resolve: {
    alias: {
      // Pin scitex-ui's `monaco-editor` peer import to writer's own copy.
      "monaco-editor": resolve(__dirname, "node_modules/monaco-editor"),
    },
    preserveSymlinks: true,
  },
  build: {
    outDir: "../static/writer",
    emptyOutDir: false,
    sourcemap: true,
    manifest: true,
    rollupOptions: {
      input: {
        index: "src/index.ts",
        viewer: "src/viewer.ts",
      },
      output: {
        entryFileNames: "assets/[name].js",
        chunkFileNames: "assets/[name].js",
        assetFileNames: "assets/[name][extname]",
      },
    },
  },
});
