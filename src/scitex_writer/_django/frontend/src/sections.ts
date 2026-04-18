/**
 * Section tabs — render the doc-type's .tex sections as clickable tabs.
 * Mirrors the cloud writer_app's section navigation: "1. Abstract",
 * "2. Introduction", etc. Selecting a tab loads that file into the editor.
 */

import type { SectionEntry } from "./api";
import { listSections } from "./api";

type SectionSelectHandler = (section: SectionEntry) => void;

export class SectionTabs {
  private container: HTMLElement;
  private onSelect: SectionSelectHandler;
  private active: SectionEntry | null = null;
  private sections: SectionEntry[] = [];

  constructor(container: HTMLElement, onSelect: SectionSelectHandler) {
    this.container = container;
    this.onSelect = onSelect;
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
    if (this.sections.length > 0) this.select(this.sections[0]);
  }

  private render(): void {
    this.container.innerHTML = "";
    this.sections.forEach((section, index) => {
      const btn = document.createElement("button");
      btn.className = "writer-section-tab";
      btn.dataset.path = section.path;
      btn.textContent = `${index + 1}. ${humanize(section.name)}`;
      btn.addEventListener("click", () => this.select(section));
      if (this.active && this.active.path === section.path) {
        btn.classList.add("active");
      }
      this.container.appendChild(btn);
    });
  }

  private select(section: SectionEntry): void {
    this.active = section;
    this.container
      .querySelectorAll<HTMLElement>(".writer-section-tab")
      .forEach((el) => {
        el.classList.toggle("active", el.dataset.path === section.path);
      });
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
