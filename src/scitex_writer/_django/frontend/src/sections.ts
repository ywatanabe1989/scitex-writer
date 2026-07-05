/**
 * Section dropdown — render the doc-type's .tex sections as a <select>,
 * matching the scitex.ai/apps/writer layout: two adjacent dropdowns, one
 * for doc type, one for section. Selecting loads the file into the editor.
 */

import type { SectionEntry } from "./api";
import { listSections } from "./api";

type SectionSelectHandler = (section: SectionEntry) => void;

export class SectionTabs {
  private container: HTMLElement;
  private onSelect: SectionSelectHandler;
  private select: HTMLSelectElement;
  private active: SectionEntry | null = null;
  private sections: SectionEntry[] = [];

  constructor(container: HTMLElement, onSelect: SectionSelectHandler) {
    this.container = container;
    this.onSelect = onSelect;

    this.select = document.createElement("select");
    this.select.className = "writer-select writer-section-select";
    this.select.title = "Section";
    this.select.addEventListener("change", () => this.handleChange());
    this.container.innerHTML = "";
    this.container.appendChild(this.select);
  }

  async load(docType: string): Promise<void> {
    try {
      const response = await listSections(docType);
      this.sections = response.sections;
    } catch (err) {
      console.error("[sections] failed to load", err);
      this.sections = [];
    }
    this.render();
    if (this.sections.length > 0) this.chooseSection(this.sections[0]);
  }

  private render(): void {
    this.select.innerHTML = "";
    this.sections.forEach((section, index) => {
      const option = document.createElement("option");
      option.value = section.path;
      option.textContent = `${index + 1}. ${humanize(section.name)}`;
      this.select.appendChild(option);
    });
    if (this.active) {
      this.select.value = this.active.path;
    }
  }

  private handleChange(): void {
    const section = this.sections.find((s) => s.path === this.select.value);
    if (section) this.chooseSection(section);
  }

  /** Locate a loaded section by a file reference (exact path, or basename of
   * the path / filename). Returns null when no section matches — used by the
   * hints "jump to source" path, where a hint's ``location.file`` may be a bare
   * name rather than the full section path. */
  findByFile(file: string): SectionEntry | null {
    if (!file) return null;
    const base = file.split("/").pop() || file;
    return (
      this.sections.find((s) => s.path === file) ||
      this.sections.find((s) => (s.path.split("/").pop() || s.path) === base) ||
      this.sections.find((s) => s.filename === base) ||
      null
    );
  }

  /** Reflect a section as active in the dropdown WITHOUT firing onSelect —
   * used after a programmatic load (the caller already loaded the file) so the
   * dropdown stays in sync without triggering a second load. */
  markActive(section: SectionEntry): void {
    this.active = section;
    this.select.value = section.path;
  }

  private chooseSection(section: SectionEntry): void {
    this.active = section;
    this.select.value = section.path;
    this.onSelect(section);
  }
}

/** "01_introduction" → "Introduction"; "abstract" → "Abstract". */
function humanize(raw: string): string {
  const stripped = raw.replace(/^\d+[_-]?/, "");
  return stripped
    .split(/[_-]/)
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1).toLowerCase())
    .join(" ");
}
