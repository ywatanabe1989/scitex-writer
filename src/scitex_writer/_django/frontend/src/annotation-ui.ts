/**
 * App-level annotation UI for the interactive paper editor (ADR 0001, slice 2).
 *
 * The pen loop (L1 viewer → AnnotationStore) is the neutral core; THIS is the
 * writer-app-specific chrome that makes it a research-review tool, kept out of
 * `@scitex/ui` L1 on purpose (scitex-ui's #274 guidance — the domain categories
 * are paper-review semantics, not a generic PDF concern):
 *   - a mode switch (Read / Markup / Review),
 *   - domain-category buttons (Claim / Issue / Citation-needed / Figure-check …),
 *   - pen-tool buttons (highlight / box / circle / arrow / freehand),
 *   - a per-comment box with OS voice → text (loosely-coupled Web Speech),
 *   - Markdown export of the comment thread.
 *
 * It drives the viewer through a narrow structural interface (AnnotationController)
 * so the two stay decoupled — the UI never imports the PDF component.
 */

import {
  ANNOTATION_CATEGORIES,
  type Annotation,
  type AnnotationCategory,
  type AnnotationTool,
  CATEGORY_LABELS,
  type EditorMode,
} from "./annotations";
import { createVoiceInput } from "./voice-input";

/** The slice of PDFViewer the annotation UI drives (structural — keeps them decoupled). */
export interface AnnotationController {
  setCategory(category: AnnotationCategory): void;
  setTool(tool: AnnotationTool): void;
  setMode(mode: EditorMode): void;
  annotations(): Annotation[];
  setAnnotationText(id: string, text: string): void;
  removeAnnotation(id: string): void;
  exportMarkdown(title?: string): string;
}

export interface AnnotationUIOptions {
  toolbar: HTMLElement;
  panel: HTMLElement;
  controller: AnnotationController;
}

export interface AnnotationUIHandle {
  /** Wire to the viewer's onAnnotate — registers a freshly created mark. */
  onAnnotate(annotation: Annotation): void;
}

interface ModeSpec {
  mode: EditorMode;
  icon: string;
  label: string;
}
interface ToolSpec {
  tool: AnnotationTool;
  icon: string;
  label: string;
}

const MODES: readonly ModeSpec[] = [
  { mode: "read", icon: "fa-book-open", label: "Read" },
  { mode: "markup", icon: "fa-pen-nib", label: "Markup" },
  { mode: "review", icon: "fa-comments", label: "Review" },
];

const PEN_TOOLS: readonly ToolSpec[] = [
  { tool: "highlight", icon: "fa-highlighter", label: "Highlight" },
  { tool: "box", icon: "fa-vector-square", label: "Box" },
  { tool: "circle", icon: "fa-circle-notch", label: "Circle" },
  { tool: "arrow", icon: "fa-arrow-right", label: "Arrow" },
  { tool: "freehand", icon: "fa-pen", label: "Freehand" },
];

/** FontAwesome glyph per domain category (FA6 — the template already loads it). */
const CATEGORY_ICONS: Record<AnnotationCategory, string> = {
  highlight: "fa-highlighter",
  claim: "fa-flag",
  question: "fa-circle-question",
  issue: "fa-triangle-exclamation",
  "citation-needed": "fa-quote-left",
  "figure-check": "fa-image",
  "method-check": "fa-flask",
};

function iconButton(icon: string, title: string): HTMLButtonElement {
  const b = document.createElement("button");
  b.type = "button";
  b.className = "btn btn-icon btn-sm annot-btn";
  b.title = title;
  b.setAttribute("aria-label", title);
  b.innerHTML = `<i class="fas ${icon}"></i>`;
  return b;
}

export function mountAnnotationUI(opts: AnnotationUIOptions): AnnotationUIHandle {
  const { toolbar, panel, controller } = opts;
  let activeField: HTMLTextAreaElement | null = null;
  let activeMic: HTMLElement | null = null;

  const voice = createVoiceInput({
    onResult: (text, isFinal) => {
      if (!activeField || !isFinal) return;
      const trimmed = text.trim();
      if (!trimmed) return;
      const sep =
        activeField.value && !activeField.value.endsWith(" ") ? " " : "";
      activeField.value = activeField.value + sep + trimmed;
      activeField.dispatchEvent(new Event("input", { bubbles: true }));
    },
    onStateChange: (listening) => {
      activeMic?.classList.toggle("listening", listening);
    },
  });

  // --- toolbar ---
  toolbar.classList.add("annot-toolbar");
  toolbar.replaceChildren();

  const modeGroup = document.createElement("div");
  modeGroup.className = "annot-group annot-modes";
  const modeButtons = new Map<EditorMode, HTMLButtonElement>();
  for (const spec of MODES) {
    const b = iconButton(spec.icon, `${spec.label} mode`);
    b.append(document.createTextNode(` ${spec.label}`));
    b.addEventListener("click", () => setMode(spec.mode));
    modeButtons.set(spec.mode, b);
    modeGroup.appendChild(b);
  }

  const catGroup = document.createElement("div");
  catGroup.className = "annot-group annot-cats";
  const catButtons = new Map<AnnotationCategory, HTMLButtonElement>();
  for (const category of ANNOTATION_CATEGORIES) {
    const b = iconButton(CATEGORY_ICONS[category], CATEGORY_LABELS[category]);
    b.dataset.category = category;
    b.addEventListener("click", () => setCategory(category));
    catButtons.set(category, b);
    catGroup.appendChild(b);
  }

  const toolGroup = document.createElement("div");
  toolGroup.className = "annot-group annot-tools";
  const toolButtons = new Map<AnnotationTool, HTMLButtonElement>();
  for (const spec of PEN_TOOLS) {
    const b = iconButton(spec.icon, spec.label);
    b.addEventListener("click", () => setTool(spec.tool));
    toolButtons.set(spec.tool, b);
    toolGroup.appendChild(b);
  }

  const exportBtn = iconButton("fa-file-arrow-down", "Export comments as Markdown");
  exportBtn.classList.add("annot-export");
  exportBtn.addEventListener("click", exportMarkdown);

  toolbar.append(modeGroup, catGroup, toolGroup, exportBtn);

  // --- panel ---
  panel.classList.add("annot-panel");

  function setMode(next: EditorMode): void {
    controller.setMode(next);
    for (const [mode, b] of modeButtons) b.classList.toggle("active", mode === next);
    toolbar.dataset.mode = next;
    panel.dataset.mode = next;
    if (next !== "markup") voice.stop();
  }

  function setCategory(next: AnnotationCategory): void {
    controller.setCategory(next);
    for (const [category, b] of catButtons)
      b.classList.toggle("active", category === next);
  }

  function setTool(next: AnnotationTool): void {
    controller.setTool(next);
    for (const [tool, b] of toolButtons) b.classList.toggle("active", tool === next);
  }

  function exportMarkdown(): void {
    const md = controller.exportMarkdown();
    const blob = new Blob([md], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "review-comments.md";
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  }

  function renderPanel(focusId?: string): void {
    const items = controller.annotations();
    panel.replaceChildren();
    if (items.length === 0) {
      const empty = document.createElement("p");
      empty.className = "annot-empty";
      empty.textContent =
        "No comments yet. Mark the PDF in Markup mode to start.";
      panel.appendChild(empty);
      return;
    }
    for (const annotation of items) {
      panel.appendChild(renderRow(annotation, annotation.id === focusId));
    }
  }

  function renderRow(annotation: Annotation, focus: boolean): HTMLElement {
    const row = document.createElement("div");
    row.className = "annot-row";
    row.dataset.category = annotation.category;

    const head = document.createElement("div");
    head.className = "annot-row-head";
    const badge = document.createElement("span");
    badge.className = "annot-badge";
    badge.innerHTML = `<i class="fas ${CATEGORY_ICONS[annotation.category]}"></i> ${
      CATEGORY_LABELS[annotation.category]
    }`;
    const page = document.createElement("span");
    page.className = "annot-page";
    page.textContent = `p.${annotation.page}`;
    const del = iconButton("fa-trash", "Delete comment");
    del.classList.add("annot-del");
    del.addEventListener("click", () => {
      controller.removeAnnotation(annotation.id);
      renderPanel();
    });
    head.append(badge, page, del);

    const body = document.createElement("div");
    body.className = "annot-row-body";
    const textarea = document.createElement("textarea");
    textarea.className = "annot-text";
    textarea.rows = 2;
    textarea.placeholder = "Comment… (dictate with OS voice input or the mic)";
    textarea.value = annotation.text;
    textarea.addEventListener("input", () =>
      controller.setAnnotationText(annotation.id, textarea.value),
    );
    textarea.addEventListener("focus", () => {
      activeField = textarea;
    });
    body.appendChild(textarea);

    if (voice.supported) {
      const mic = iconButton("fa-microphone", "Dictate this comment");
      mic.classList.add("annot-mic");
      mic.addEventListener("click", () => {
        activeField = textarea;
        activeMic = mic;
        textarea.focus();
        voice.toggle();
      });
      body.appendChild(mic);
    }

    row.append(head, body);
    if (focus) {
      queueMicrotask(() => textarea.focus());
    }
    return row;
  }

  setMode("markup");
  setCategory("highlight");
  setTool("highlight");
  renderPanel();

  return {
    onAnnotate(annotation) {
      renderPanel(annotation.id);
    },
  };
}
