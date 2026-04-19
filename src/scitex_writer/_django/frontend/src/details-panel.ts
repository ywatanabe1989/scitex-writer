/**
 * Details panel — collapsible right-hand column matching scitex.ai/apps/writer.
 * Sections: Compilation (Preview/Full status) · Overleaf (WIP) · Prism (WIP) ·
 * Project Info · Shortcuts. Collapsed/expanded state stored in localStorage.
 */

import { projectInfo } from "./api";
import type { ProjectInfo } from "./api";

type SectionId =
  | "compile-preview"
  | "compile-full"
  | "overleaf"
  | "prism"
  | "project"
  | "shortcuts";

interface SectionDef {
  id: SectionId;
  title: string;
  icon: string;
  wip?: boolean;
  render: () => string;
}

const STORAGE_KEY = "writer-details-open";

export class DetailsPanel {
  private container: HTMLElement;
  private open: Set<SectionId>;
  private project: ProjectInfo | null = null;
  private compileState: { preview: string; full: string } = {
    preview: "idle",
    full: "idle",
  };

  constructor(container: HTMLElement) {
    this.container = container;
    this.open = this.loadOpenState();
    this.render();
    void this.loadProject();
  }

  setCompileStatus(mode: "preview" | "full", status: string): void {
    this.compileState[mode] = status;
    this.render();
  }

  openSection(id: SectionId): void {
    this.open.add(id);
    this.saveOpenState();
    this.render();
    this.container
      .querySelector<HTMLElement>(`[data-id="${id}"]`)
      ?.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  private async loadProject(): Promise<void> {
    try {
      this.project = await projectInfo();
      this.render();
    } catch (err) {
      console.warn("[details] projectInfo failed", err);
    }
  }

  private sections(): SectionDef[] {
    const dot = (state: string) => {
      const colors: Record<string, string> = {
        idle: "#888",
        compiling: "var(--warning, #d97706)",
        ok: "var(--success, #16a34a)",
        error: "var(--danger, #dc2626)",
      };
      return `<span class="details-dot" style="background:${colors[state] || colors.idle}" title="${state}"></span>`;
    };

    return [
      {
        id: "compile-preview",
        title: "Compilation — Preview",
        icon: "fa-circle-dot",
        render: () => `
          <div class="details-row">
            <span>Status</span><span>${dot(this.compileState.preview)} ${this.compileState.preview}</span>
          </div>
          <p class="details-hint">Compiles the current section only. Fast iteration.</p>
        `,
      },
      {
        id: "compile-full",
        title: "Compilation — Full",
        icon: "fa-file-pdf",
        render: () => `
          <div class="details-row">
            <span>Status</span><span>${dot(this.compileState.full)} ${this.compileState.full}</span>
          </div>
          <p class="details-hint">Compiles the full manuscript (all sections + bibliography).</p>
        `,
      },
      {
        id: "overleaf",
        title: "↔ Overleaf",
        icon: "fa-cloud-arrow-up",
        wip: true,
        render: () => `
          <p class="details-hint">
            Overleaf ZIP import / export is on the roadmap.
            Meanwhile: compile locally and upload the PDF to Overleaf manually.
          </p>
        `,
      },
      {
        id: "prism",
        title: "↔ Prism (OpenAI)",
        icon: "fa-wand-magic-sparkles",
        wip: true,
        render: () => `
          <p class="details-hint">
            Inline AI drafting (GPT-based) will be wired in a later PR.
          </p>
        `,
      },
      {
        id: "project",
        title: "Project Info",
        icon: "fa-circle-info",
        render: () => {
          if (!this.project) return `<p class="details-hint">Loading…</p>`;
          return `
            <div class="details-row"><span>Name</span><span>${escapeHtml(this.project.project_name)}</span></div>
            <div class="details-row"><span>Path</span><span class="details-mono">${escapeHtml(this.project.project_dir)}</span></div>
            <div class="details-row"><span>Doc types</span><span>${escapeHtml(this.project.doc_types.join(", ") || "(none)")}</span></div>
            <div class="details-row"><span>Shared</span><span>${this.project.has_shared ? "yes" : "no"}</span></div>
          `;
        },
      },
      {
        id: "shortcuts",
        title: "Shortcuts",
        icon: "fa-keyboard",
        render: () => `
          <div class="details-row"><kbd>Ctrl</kbd>+<kbd>S</kbd><span>Save current section</span></div>
          <div class="details-row"><kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>B</kbd><span>Compile</span></div>
          <div class="details-row"><kbd>Esc</kbd><span>Close open panel</span></div>
        `,
      },
    ];
  }

  private render(): void {
    const sections = this.sections();
    this.container.innerHTML = `
      <div class="details-header">
        <i class="fas fa-sliders"></i> Details
      </div>
      <div class="details-body">
        ${sections
          .map(
            (s) => `
          <div class="details-section ${this.open.has(s.id) ? "open" : ""}" data-id="${s.id}">
            <button class="details-section-toggle" data-toggle="${s.id}">
              <i class="fas ${s.icon}"></i>
              <span class="details-section-title">${s.title}</span>
              ${s.wip ? `<span class="details-wip-badge">WIP</span>` : ""}
              <i class="fas fa-chevron-right details-chevron"></i>
            </button>
            ${this.open.has(s.id) ? `<div class="details-section-body">${s.render()}</div>` : ""}
          </div>`,
          )
          .join("")}
      </div>
    `;
    this.container
      .querySelectorAll<HTMLElement>("[data-toggle]")
      .forEach((el) => {
        el.addEventListener("click", () => {
          const id = el.dataset.toggle as SectionId;
          if (this.open.has(id)) this.open.delete(id);
          else this.open.add(id);
          this.saveOpenState();
          this.render();
        });
      });
  }

  private loadOpenState(): Set<SectionId> {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return new Set(["compile-preview", "project"]);
      return new Set(JSON.parse(raw));
    } catch {
      return new Set(["compile-preview", "project"]);
    }
  }

  private saveOpenState(): void {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(Array.from(this.open)));
    } catch {
      /* quota etc — ignore */
    }
  }
}

function escapeHtml(text: string): string {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}
