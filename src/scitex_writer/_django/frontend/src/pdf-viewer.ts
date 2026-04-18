/**
 * PDF viewer built on pdfjs-dist. Renders every page into a scrollable
 * column with fit-width, zoom-in/out, and re-render on source change.
 * Minimal: no text-layer, no annotation-layer, no find. PR5/6 can add them.
 */

import * as pdfjs from "pdfjs-dist";
// Worker shim: same pattern as scitex-ui's Monaco fake-worker.
// pdfjs refuses to load a worker by default if workerSrc is unset, so we
// point it to the ESM worker bundled by Vite.
import PdfWorker from "pdfjs-dist/build/pdf.worker.min.mjs?url";

(pdfjs.GlobalWorkerOptions as { workerSrc: string }).workerSrc = PdfWorker;

import { API_BASE, PROJECT_DIR } from "./api";

interface PDFViewerOptions {
  container: HTMLElement;
}

export class PDFViewer {
  private container: HTMLElement;
  private pdfDoc: pdfjs.PDFDocumentProxy | null = null;
  private scale = 1.0;
  private fitMode: "width" | "none" = "width";
  private canvases: HTMLCanvasElement[] = [];

  constructor(options: PDFViewerOptions) {
    this.container = options.container;
    this.container.classList.add("pdf-viewer-host");
  }

  async load(docType: string): Promise<boolean> {
    const url =
      `${API_BASE}api/pdf?doc_type=${encodeURIComponent(docType)}` +
      `&working_dir=${encodeURIComponent(PROJECT_DIR)}` +
      `&t=${Date.now()}`;
    try {
      const task = pdfjs.getDocument({ url });
      this.pdfDoc = await task.promise;
      await this.render();
      return true;
    } catch (err) {
      console.warn("[pdf-viewer] load failed:", err);
      this.renderPlaceholder();
      return false;
    }
  }

  clear(): void {
    this.pdfDoc = null;
    this.canvases = [];
    this.container.innerHTML = "";
  }

  renderPlaceholder(message: string = "No PDF available."): void {
    this.clear();
    const placeholder = document.createElement("div");
    placeholder.className = "pdf-placeholder";
    placeholder.innerHTML = `<p>${message}</p><p class="hint">Click Compile to generate.</p>`;
    this.container.appendChild(placeholder);
  }

  async render(): Promise<void> {
    if (!this.pdfDoc) return;
    this.container.innerHTML = "";
    this.canvases = [];
    const renderScale =
      this.fitMode === "width" ? this.computeFitWidthScale() : this.scale;

    for (let pageNum = 1; pageNum <= this.pdfDoc.numPages; pageNum++) {
      const page = await this.pdfDoc.getPage(pageNum);
      const viewport = page.getViewport({ scale: renderScale });
      const canvas = document.createElement("canvas");
      const ctx = canvas.getContext("2d");
      if (!ctx) continue;
      canvas.width = viewport.width;
      canvas.height = viewport.height;
      canvas.className = "pdf-page-canvas";
      this.container.appendChild(canvas);
      this.canvases.push(canvas);
      await page.render({ canvasContext: ctx, viewport }).promise;
    }
  }

  private computeFitWidthScale(): number {
    if (!this.pdfDoc) return 1;
    const first = this.pdfDoc.numPages > 0 ? 1 : 0;
    if (!first) return 1;
    const width = this.container.clientWidth - 32; // padding
    return Math.max(0.4, width / 800); // 800px baseline
  }

  setZoom(delta: number): void {
    this.fitMode = "none";
    this.scale = Math.max(0.4, Math.min(3, this.scale + delta));
    void this.render();
  }

  setFitWidth(): void {
    this.fitMode = "width";
    this.scale = 1;
    void this.render();
  }

  get zoomPercent(): number {
    const effective =
      this.fitMode === "width" ? this.computeFitWidthScale() : this.scale;
    return Math.round(effective * 100);
  }
}
