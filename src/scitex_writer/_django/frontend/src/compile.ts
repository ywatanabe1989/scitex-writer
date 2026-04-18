/**
 * Compile workflow — POST /api/compile, poll /api/compile/status, load PDF.
 * Status lamp (green/yellow/red), log drawer, preview-full toggle.
 */

import { apiPost, apiGet } from "./api";
import type { PDFViewer } from "./pdf-viewer";

export type CompileMode = "preview" | "full";
export type LampStatus = "idle" | "compiling" | "ok" | "error";

interface CompileStatusResponse {
  compiling: boolean;
  result: { success?: boolean; error?: string; log?: string } | null;
  log: string;
}

interface CompileOptions {
  lamp: HTMLElement | null;
  logContent: HTMLElement | null;
  logPanel: HTMLElement | null;
  toggleLogBtn: HTMLElement | null;
  closeLogBtn: HTMLElement | null;
  compileBtn: HTMLElement | null;
  modeToggleBtn: HTMLElement | null;
  pdf: PDFViewer;
  getDocType: () => string;
}

export class CompileController {
  private opts: CompileOptions;
  private mode: CompileMode = "preview";
  private polling: number | null = null;
  private status: LampStatus = "idle";

  constructor(opts: CompileOptions) {
    this.opts = opts;
    this.wireEvents();
    this.updateLamp("idle");
    this.updateModeButton();
  }

  private wireEvents(): void {
    this.opts.compileBtn?.addEventListener("click", () => void this.compile());
    this.opts.toggleLogBtn?.addEventListener("click", () => this.toggleLog());
    this.opts.closeLogBtn?.addEventListener("click", () => this.setLogOpen(false));
    this.opts.modeToggleBtn?.addEventListener("click", () => this.toggleMode());
    window.addEventListener("keydown", (event) => {
      if ((event.ctrlKey || event.metaKey) && event.shiftKey && event.key === "B") {
        event.preventDefault();
        void this.compile();
      }
    });
  }

  async compile(): Promise<void> {
    if (this.status === "compiling") return;
    const docType = this.opts.getDocType();
    this.updateLamp("compiling");
    this.setLog("");
    try {
      await apiPost("api/compile", {
        doc_type: docType,
        draft: this.mode === "preview",
      });
      this.pollStatus(docType);
    } catch (err) {
      this.setLog(String(err));
      this.updateLamp("error");
    }
  }

  private pollStatus(docType: string): void {
    if (this.polling) window.clearTimeout(this.polling);
    const tick = async () => {
      try {
        const status = await apiGet<CompileStatusResponse>("api/compile/status");
        if (status.log) this.setLog(status.log);
        if (status.compiling) {
          this.polling = window.setTimeout(tick, 800);
          return;
        }
        const success = status.result?.success ?? false;
        this.updateLamp(success ? "ok" : "error");
        if (success) {
          await this.opts.pdf.load(docType);
        } else if (status.result?.error) {
          this.setLog(status.result.error);
          this.setLogOpen(true);
        }
      } catch (err) {
        this.setLog(String(err));
        this.updateLamp("error");
      }
    };
    this.polling = window.setTimeout(tick, 400);
  }

  private updateLamp(status: LampStatus): void {
    this.status = status;
    const lamp = this.opts.lamp;
    if (!lamp) return;
    lamp.className = `writer-lamp lamp-${status}`;
    const title =
      status === "compiling"
        ? "Compiling…"
        : status === "ok"
          ? "Last compile: success"
          : status === "error"
            ? "Last compile: error"
            : "Idle";
    lamp.title = title;
  }

  private setLog(text: string): void {
    if (this.opts.logContent) this.opts.logContent.textContent = text;
  }

  private setLogOpen(open: boolean): void {
    this.opts.logPanel?.classList.toggle("u-hidden", !open);
  }

  private toggleLog(): void {
    if (!this.opts.logPanel) return;
    const isHidden = this.opts.logPanel.classList.contains("u-hidden");
    this.setLogOpen(isHidden);
  }

  private toggleMode(): void {
    this.mode = this.mode === "preview" ? "full" : "preview";
    this.updateModeButton();
  }

  private updateModeButton(): void {
    const btn = this.opts.modeToggleBtn;
    if (!btn) return;
    btn.textContent = this.mode === "preview" ? "Preview" : "Full";
    btn.classList.toggle("active-full", this.mode === "full");
  }
}
