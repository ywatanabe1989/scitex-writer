/**
 * PDF theme override — independent of the global editor theme.
 *
 * Authors sometimes want to preview the PDF in the opposite theme
 * (e.g. edit in dark mode but check that the final light PDF looks
 * right). This module tracks a three-state preference:
 *
 *   "auto"  — PDF compile dark_mode follows the UI theme (default).
 *   "light" — force light-mode PDF regardless of UI.
 *   "dark"  — force dark-mode PDF regardless of UI.
 *
 * Persisted in localStorage so the preference survives reloads.
 */

export type PdfThemeMode = "auto" | "light" | "dark";

const STORAGE_KEY = "writer.pdf-theme";

export function getPdfThemeMode(): PdfThemeMode {
  const v = localStorage.getItem(STORAGE_KEY);
  return v === "light" || v === "dark" || v === "auto" ? v : "auto";
}

export function setPdfThemeMode(mode: PdfThemeMode): void {
  localStorage.setItem(STORAGE_KEY, mode);
}

export function effectivePdfDarkMode(
  mode: PdfThemeMode = getPdfThemeMode(),
): boolean {
  if (mode === "light") return false;
  if (mode === "dark") return true;
  return document.documentElement.dataset.theme === "dark";
}

export function cyclePdfThemeMode(): PdfThemeMode {
  const current = getPdfThemeMode();
  const next: PdfThemeMode =
    current === "auto" ? "light" : current === "light" ? "dark" : "auto";
  setPdfThemeMode(next);
  return next;
}

export function pdfThemeIcon(mode: PdfThemeMode): string {
  if (mode === "light") return "fa-sun";
  if (mode === "dark") return "fa-moon";
  return "fa-circle-half-stroke";
}

export function pdfThemeLabel(mode: PdfThemeMode): string {
  if (mode === "light") return "PDF: light";
  if (mode === "dark") return "PDF: dark";
  return "PDF: follows editor";
}
