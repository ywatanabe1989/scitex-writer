import { execSync } from "child_process";
import { fileURLToPath } from "url";
import { resolve } from "path";
import { defineConfig } from "vite";

const __dirname = fileURLToPath(new URL(".", import.meta.url));

function discoverScitexUiStatic(): string {
  if (process.env.SCITEX_UI_STATIC) return process.env.SCITEX_UI_STATIC;
  try {
    const path = execSync(
      'python3 -c "import scitex_ui; print(scitex_ui.get_static_dir())"',
      { encoding: "utf-8", timeout: 5000 },
    ).trim();
    if (path) return path;
  } catch {
    /* fall through */
  }
  throw new Error(
    "scitex-ui not found. Install it (pip install scitex-ui) or set SCITEX_UI_STATIC env var.",
  );
}

const SCITEX_UI_STATIC = discoverScitexUiStatic();

export default defineConfig({
  base: "/static/writer/",
  resolve: {
    alias: {
      "@scitex/ui": SCITEX_UI_STATIC.replace(
        /\/src\/scitex_ui\/static\/scitex_ui$/,
        "",
      ),
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
      },
      output: {
        entryFileNames: "assets/index.js",
        chunkFileNames: "assets/[name].js",
        assetFileNames: "assets/[name][extname]",
      },
    },
  },
});
