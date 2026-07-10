/**
 * Annotation model for the interactive paper editor (ADR 0001).
 *
 * Writer-owned NEUTRAL PORT: the pen / L1 PDF-viewer layer PRODUCES annotations
 * into this store; agents CONSUME them — claim/prose marks feed the writer/clew
 * hints loop, figure marks route to figrecipe as figure-requests/1. The model is
 * deliberately independent of the PDF-viewer component (@scitex/ui/pdf-viewer):
 * it is the stable data contract both sides bind to (ports-and-producers).
 *
 * Anchors are in ZOOM-INVARIANT PDF space (from PdfViewerApi.getCoords), so a
 * mark stays put across zoom/scroll — the "here, spatially" the operator wants
 * to tell the agent (ADR 0001 §2).
 */

/** Pen mark primitives the L1 overlay emits (ADR 0001 §2 — shape marks only). */
export type AnnotationTool =
  | "highlight"
  | "underline"
  | "circle"
  | "arrow"
  | "box"
  | "freehand";

/**
 * Research-review categories — the domain buttons that make this a research
 * environment, not a generic PDF tool (ADR 0001 §2, the "moat").
 */
export type AnnotationCategory =
  | "highlight"
  | "claim"
  | "question"
  | "issue"
  | "citation-needed"
  | "figure-check"
  | "method-check";

export const ANNOTATION_CATEGORIES: readonly AnnotationCategory[] = [
  "highlight",
  "claim",
  "question",
  "issue",
  "citation-needed",
  "figure-check",
  "method-check",
];

/** Human labels for the domain buttons. */
export const CATEGORY_LABELS: Record<AnnotationCategory, string> = {
  highlight: "Highlight",
  claim: "Claim",
  question: "Question",
  issue: "Issue",
  "citation-needed": "Citation needed",
  "figure-check": "Figure check",
  "method-check": "Method check",
};

/** FontAwesome glyph per domain category — shared by the toolbar buttons
 * (annotation-ui.ts) and the PDF-area/row right-click menus (context-menu.ts
 * call sites in pdf-viewer.ts + annotation-ui.ts) so every surface reads
 * identically. */
export const CATEGORY_ICONS: Record<AnnotationCategory, string> = {
  highlight: "fa-highlighter",
  claim: "fa-flag",
  question: "fa-circle-question",
  issue: "fa-triangle-exclamation",
  "citation-needed": "fa-quote-left",
  "figure-check": "fa-image",
  "method-check": "fa-flask",
};

/** Categories whose marks route to figrecipe (figure-requests/1) vs the hints loop. */
export const FIGURE_CATEGORIES: readonly AnnotationCategory[] = ["figure-check"];

/** Editor modes (ADR 0001 §2): Read (scroll/zoom), Markup (pen), Review (comment). */
export type EditorMode = "read" | "markup" | "review";

/** A point in zoom-invariant PDF space (PdfViewerApi.getCoords output). */
export interface PdfPoint {
  page: number;
  pdfX: number;
  pdfY: number;
}

/** A rectangular region in PDF space (from onRegionSelect / the box tool). */
export interface PdfRegion {
  page: number;
  x0: number;
  y0: number;
  x1: number;
  y1: number;
}

/** One coordinate-tied annotation. */
export interface Annotation {
  id: string;
  page: number;
  /** Primary spatial anchor — the "here". */
  anchor: PdfPoint;
  /** Rectangular region, for box/region marks. */
  region?: PdfRegion;
  /** Freehand stroke as a normalized-PDF-space polyline. */
  path?: Array<[number, number]>;
  tool: AnnotationTool;
  category: AnnotationCategory;
  /** Voice/typed note; may be empty for a pure spatial mark. */
  text: string;
  /** Sanitized figure save-path when this marks a figure (routes to figrecipe). */
  target?: string;
  status: "open" | "addressed";
  /** Producer stamp — always "writer" for author annotations. */
  source: string;
  /** ISO-8601 creation time. */
  ts: string;
}

/** The on-disk feed shape (`.scitex/writer/comments.json`). */
export interface AnnotationFeed {
  annotations: Annotation[];
}

function makeId(): string {
  const c = (globalThis as { crypto?: Crypto }).crypto;
  if (c && typeof c.randomUUID === "function") {
    return `ann:${c.randomUUID()}`;
  }
  return `ann:${Date.now().toString(36)}-${Math.floor(
    (globalThis.performance?.now?.() ?? 0) % 1_000_000,
  ).toString(36)}`;
}

/** Fields a producer supplies; id/status/source/ts are stamped by the store. */
export type AnnotationDraft = Omit<Annotation, "id" | "status" | "source" | "ts"> &
  Partial<Pick<Annotation, "status" | "source" | "ts">>;

/**
 * In-memory annotation store — the controlled overlay's source of truth. The
 * viewer echoes committed marks back via `setMarks(store.list())`; producers
 * (pen layer, domain buttons) mutate it; consumers read `toFeed()` / `toMarkdown()`.
 */
export class AnnotationStore {
  private items = new Map<string, Annotation>();

  add(draft: AnnotationDraft, nowIso: string): Annotation {
    const ann: Annotation = {
      id: makeId(),
      status: draft.status ?? "open",
      source: draft.source ?? "writer",
      ts: draft.ts ?? nowIso,
      page: draft.page,
      anchor: draft.anchor,
      region: draft.region,
      path: draft.path,
      tool: draft.tool,
      category: draft.category,
      text: draft.text,
      target: draft.target,
    };
    this.items.set(ann.id, ann);
    return ann;
  }

  update(id: string, patch: Partial<Annotation>): Annotation | undefined {
    const cur = this.items.get(id);
    if (!cur) return undefined;
    const next = { ...cur, ...patch, id: cur.id };
    this.items.set(id, next);
    return next;
  }

  remove(id: string): boolean {
    return this.items.delete(id);
  }

  get(id: string): Annotation | undefined {
    return this.items.get(id);
  }

  /** All annotations, ordered by page then top-to-bottom (PDF y-down). */
  list(): Annotation[] {
    return [...this.items.values()].sort(
      (a, b) => a.page - b.page || a.anchor.pdfY - b.anchor.pdfY,
    );
  }

  forPage(page: number): Annotation[] {
    return this.list().filter((a) => a.page === page);
  }

  /** Figure-targeted marks, for routing to figrecipe (figure-requests/1). */
  figureRequests(): Annotation[] {
    return this.list().filter(
      (a) => a.target || FIGURE_CATEGORIES.includes(a.category),
    );
  }

  replaceAll(annotations: Annotation[]): void {
    this.items.clear();
    for (const a of annotations) this.items.set(a.id, a);
  }

  toFeed(): AnnotationFeed {
    return { annotations: this.list() };
  }

  loadFeed(feed: AnnotationFeed | null | undefined): void {
    this.replaceAll(feed?.annotations ?? []);
  }

  /** Markdown export of the review comments (ADR 0001 MVP: markdown export). */
  toMarkdown(title = "Review comments"): string {
    const lines: string[] = [`# ${title}`, ""];
    let lastPage = -1;
    for (const a of this.list()) {
      if (a.page !== lastPage) {
        lines.push(`## Page ${a.page}`, "");
        lastPage = a.page;
      }
      const label = CATEGORY_LABELS[a.category] ?? a.category;
      const at = `(${a.anchor.pdfX.toFixed(1)}, ${a.anchor.pdfY.toFixed(1)})`;
      const body = a.text.trim() ? ` — ${a.text.trim()}` : "";
      const tgt = a.target ? ` [figure: ${a.target}]` : "";
      lines.push(`- **${label}** ${at}${tgt}${body}`);
    }
    lines.push("");
    return lines.join("\n");
  }
}
