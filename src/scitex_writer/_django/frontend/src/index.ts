/**
 * SciTeX Writer entry point — Monaco LaTeX editor with section navigation.
 * Bundled by Vite; output lands at `static/writer/assets/index.js` and is
 * loaded by `editor.html` as a module script.
 */

import {
  MonacoEditor,
  registerLatexLanguage,
  waitForMonaco,
} from "@scitex/ui/src/scitex_ui/static/scitex_ui/ts/app/monaco-editor";

import { getFile, saveFile, projectInfo } from "./api";
import type { SectionEntry } from "./api";
import { SectionTabs } from "./sections";
import { countWords, mountToolbar } from "./toolbar";
import { PDFViewer } from "./pdf-viewer";
import { CompileController } from "./compile";
import { InsertPanel } from "./insert-panel";
import { DetailsPanel } from "./details-panel";

const SAVE_DEBOUNCE_MS = 800;

async function bootstrap(): Promise<void> {
  const root = document.querySelector<HTMLElement>(".writer-app");
  if (!root) {
    console.warn("[writer] .writer-app container not found — aborting init");
    return;
  }

  // Monaco needs LaTeX registered before we create any editor
  const monaco = await waitForMonaco();
  registerLatexLanguage(monaco);

  const editorContainer = root.querySelector<HTMLElement>("#editor-container");
  if (!editorContainer) return;

  // Replace the welcome message with the Monaco host
  editorContainer.innerHTML =
    '<div id="monaco-host" class="monaco-host"></div>';
  const host = editorContainer.querySelector<HTMLElement>("#monaco-host")!;

  const editor = new MonacoEditor({
    container: host,
    language: "latex",
    value: "% Loading…",
    lineNumbers: "on",
    wordWrap: "on",
    minimap: true,
    fontSize: 14,
    tabSize: 2,
  });
  await editor.initialize();

  // Force layout once after the shell has stabilised — automaticLayout
  // via ResizeObserver misses the initial container-size flip when
  // shell panes are hidden via CSS after Monaco init. Without this,
  // line numbers render at the wrong Y offset.
  requestAnimationFrame(() => {
    editor.getEditor()?.layout();
  });

  // Toolbar wiring
  const tabsEl = root.querySelector<HTMLElement>("#section-tabs");
  const sections = tabsEl
    ? new SectionTabs(tabsEl, (section) => {
        void loadSection(section);
      })
    : null;

  // PDF viewer
  const pdfContainer = root.querySelector<HTMLElement>("#pdf-container");
  const pdf = pdfContainer ? new PDFViewer({ container: pdfContainer }) : null;
  pdf?.renderPlaceholder();

  // Compile controller
  const compile = pdf
    ? new CompileController({
        lamp: root.querySelector<HTMLElement>("#compile-lamp"),
        logContent: root.querySelector<HTMLElement>("#log-content"),
        logPanel: root.querySelector<HTMLElement>("#log-panel"),
        toggleLogBtn: root.querySelector<HTMLElement>("#btn-toggle-log"),
        closeLogBtn: root.querySelector<HTMLElement>("#btn-close-log"),
        compileBtn: root.querySelector<HTMLElement>("#btn-compile"),
        modeToggleBtn: root.querySelector<HTMLElement>("#btn-compile-mode"),
        pdf,
        getDocType: () =>
          root.querySelector<HTMLSelectElement>("#doc-type-select")?.value ||
          "manuscript",
      })
    : null;

  const toolbar = mountToolbar(root, {
    onDocType: async (docType) => {
      await sections?.load(docType);
      await pdf?.load(docType);
      insert?.invalidate(docType);
    },
    onFontSize: (size) => {
      editor.getEditor()?.updateOptions({ fontSize: size });
    },
    onTheme: () => {
      // scitex-ui's theme observer handles Monaco — nothing else needed
    },
  });

  root
    .querySelector<HTMLElement>("#btn-refresh-pdf")
    ?.addEventListener("click", async () => {
      const dt =
        root.querySelector<HTMLSelectElement>("#doc-type-select")?.value ||
        "manuscript";
      await pdf?.load(dt);
    });

  root
    .querySelector<HTMLElement>("#btn-pdf-zoom-in")
    ?.addEventListener("click", () => pdf?.setZoom(0.1));
  root
    .querySelector<HTMLElement>("#btn-pdf-zoom-out")
    ?.addEventListener("click", () => pdf?.setZoom(-0.1));
  root
    .querySelector<HTMLElement>("#btn-pdf-fit")
    ?.addEventListener("click", () => pdf?.setFitWidth());

  // silence unused warnings until richer use later
  void compile;

  // Details right panel (Compilation / Overleaf / Prism / Project / Shortcuts)
  const detailsEl = root.querySelector<HTMLElement>("#details-panel");
  const details = detailsEl ? new DetailsPanel(detailsEl) : null;
  void details;

  // Insert panel (cite/fig/table/history icon bar)
  const insertBar = root.querySelector<HTMLElement>("#insert-bar");
  const insertPanel = root.querySelector<HTMLElement>("#insert-panel");
  const insert =
    insertBar && insertPanel
      ? new InsertPanel({
          bar: insertBar,
          panel: insertPanel,
          getDocType: () =>
            root.querySelector<HTMLSelectElement>("#doc-type-select")?.value ||
            "manuscript",
          insertAtCursor: (snippet) => {
            const mEditor = editor.getEditor();
            if (!mEditor) return;
            const selection = mEditor.getSelection();
            mEditor.executeEdits("insert-panel", [
              {
                range: selection,
                text: snippet,
                forceMoveMarkers: true,
              },
            ]);
            mEditor.focus();
          },
        })
      : null;

  // Declare state BEFORE any loadSection trigger (TDZ guard).
  let currentPath: string | null = null;
  let saveTimer: number | null = null;

  // Initial load: discover doc types then load the first section of the first type
  let info: Awaited<ReturnType<typeof projectInfo>>;
  try {
    info = await projectInfo();
  } catch (err) {
    console.error("[writer] projectInfo failed", err);
    return;
  }
  const initialDocType = info.doc_types[0] || "manuscript";
  const docSelect = root.querySelector<HTMLSelectElement>("#doc-type-select");
  if (docSelect) docSelect.value = initialDocType;
  await sections?.load(initialDocType);
  await pdf?.load(initialDocType);

  async function loadSection(section: SectionEntry): Promise<void> {
    try {
      const file = await getFile(section.path);
      currentPath = section.path;
      editor.setValue(file.content);
      updateWordCount();
      const currentFileEl = root?.querySelector<HTMLElement>("#current-file");
      if (currentFileEl) currentFileEl.textContent = file.name;
      toolbar.setSavedStatus("saved");
    } catch (err) {
      console.error("[writer] loadSection failed", err);
      toolbar.setSavedStatus("error");
    }
  }

  function updateWordCount(): void {
    toolbar.setWordCount(countWords(editor.getValue()));
  }

  const mEditor = editor.getEditor();
  mEditor?.onDidChangeModelContent(() => {
    updateWordCount();
    toolbar.setSavedStatus("saving");
    if (saveTimer) window.clearTimeout(saveTimer);
    saveTimer = window.setTimeout(flushSave, SAVE_DEBOUNCE_MS);
  });

  async function flushSave(): Promise<void> {
    if (!currentPath) return;
    try {
      await saveFile(currentPath, editor.getValue());
      toolbar.setSavedStatus("saved");
    } catch (err) {
      console.error("[writer] save failed", err);
      toolbar.setSavedStatus("error");
    }
  }

  window.addEventListener("keydown", (event) => {
    if ((event.ctrlKey || event.metaKey) && event.key === "s") {
      event.preventDefault();
      if (saveTimer) window.clearTimeout(saveTimer);
      void flushSave();
    }
  });
}

void bootstrap();
