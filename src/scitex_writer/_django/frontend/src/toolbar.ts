/**
 * Writer toolbar — doc-type picker, font-size, dark-mode, word count.
 * Mirrors the look of scitex.ai/apps/writer top bar.
 */

type DocTypeHandler = (docType: string) => void;
type FontSizeHandler = (size: number) => void;
type ThemeHandler = (mode: "dark" | "light") => void;

export interface ToolbarHandles {
  setWordCount: (count: number) => void;
  setSavedStatus: (status: "saved" | "saving" | "error" | "") => void;
}

export function mountToolbar(
  root: HTMLElement,
  callbacks: {
    onDocType: DocTypeHandler;
    onFontSize: FontSizeHandler;
    onTheme: ThemeHandler;
  },
): ToolbarHandles {
  const docSelect = root.querySelector<HTMLSelectElement>("#doc-type-select");
  docSelect?.addEventListener("change", () =>
    callbacks.onDocType(docSelect.value),
  );

  const fontSizeEl = root.querySelector<HTMLSelectElement>("#font-size-select");
  fontSizeEl?.addEventListener("change", () =>
    callbacks.onFontSize(Number.parseInt(fontSizeEl.value, 10)),
  );

  const themeBtn = root.querySelector<HTMLButtonElement>("#btn-toggle-theme");
  themeBtn?.addEventListener("click", () => {
    const html = document.documentElement;
    const next = html.dataset.theme === "dark" ? "light" : "dark";
    html.dataset.theme = next;
    localStorage.setItem("scitex-theme", next);
    callbacks.onTheme(next);
  });

  const saved = root.querySelector<HTMLElement>("#save-status");
  const wordCount = root.querySelector<HTMLElement>("#word-count");

  return {
    setWordCount(count: number) {
      if (wordCount) wordCount.textContent = `${count} words`;
    },
    setSavedStatus(status) {
      if (!saved) return;
      saved.className = "save-status";
      if (status === "saved") {
        saved.textContent = "Saved";
        saved.classList.add("saved");
      } else if (status === "saving") {
        saved.textContent = "Saving…";
        saved.classList.add("saving");
      } else if (status === "error") {
        saved.textContent = "Save failed";
        saved.classList.add("error");
      } else {
        saved.textContent = "";
      }
    },
  };
}

export function countWords(text: string): number {
  // Strip LaTeX commands + comments before counting
  const plain = text
    .replace(/%.*$/gm, "")
    .replace(/\\[a-zA-Z]+\*?(\[[^\]]*\])?(\{[^}]*\})?/g, " ")
    .replace(/[{}]/g, " ");
  const matches = plain.trim().match(/\S+/g);
  return matches ? matches.length : 0;
}
