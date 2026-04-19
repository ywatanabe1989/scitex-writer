/**
 * Viewer entry point — read-only live-paper view.
 * Claims list + PDF preview + click-through DAG. No editing.
 * Bundled by Vite to `static/writer/assets/viewer.js`.
 */

import { PDFViewer } from "./pdf-viewer";
import { apiGet, API_BASE, PROJECT_DIR } from "./api";

declare global {
  interface Window {
    mermaid?: {
      initialize: (config: Record<string, unknown>) => void;
      render: (
        id: string,
        code: string,
      ) => Promise<{ svg: string; bindFunctions?: (el: Element) => void }>;
    };
  }
}

interface ClaimRow {
  claim_id: string;
  type: string;
  context?: string;
  preview_nature?: string;
  has_provenance: boolean;
  verification?: { state: string; error?: string };
}

interface ClaimsMetadataResponse {
  success: boolean;
  count: number;
  claims: ClaimRow[];
}

interface DagResponse {
  success: boolean;
  mermaid?: string;
  error?: string;
}

async function bootstrap(): Promise<void> {
  const root = document.querySelector<HTMLElement>(".writer-app--viewer");
  if (!root) return;

  window.mermaid?.initialize({ startOnLoad: false, theme: "dark" });

  const pdfContainer = root.querySelector<HTMLElement>("#pdf-container");
  const pdf = pdfContainer ? new PDFViewer({ container: pdfContainer }) : null;
  pdf?.renderPlaceholder("No PDF compiled yet.");

  const docSelect = root.querySelector<HTMLSelectElement>("#doc-type-select");
  const initialDocType = docSelect?.value || "manuscript";
  await pdf?.load(initialDocType);

  docSelect?.addEventListener("change", async () => {
    await pdf?.load(docSelect.value);
  });

  wirePdfControls(root, pdf);
  wireTabs(root);

  const claimsList = root.querySelector<HTMLElement>("#viewer-claims-list");
  const badge = root.querySelector<HTMLElement>("#claims-count-badge");
  const popup = root.querySelector<HTMLElement>("#viewer-popup");
  const popupBody = root.querySelector<HTMLElement>("#viewer-popup-body");
  const popupTitle = root.querySelector<HTMLElement>("#viewer-popup-title");
  const popupClose = root.querySelector<HTMLElement>("#viewer-popup-close");
  const dagContainer = root.querySelector<HTMLElement>("#dag-container");

  popupClose?.addEventListener("click", () => popup?.classList.add("u-hidden"));

  const claims = await loadClaims();
  if (badge)
    badge.textContent = `${claims.length} claim${claims.length === 1 ? "" : "s"}`;
  renderClaimsList(claimsList, claims, async (claim) => {
    if (popup && popupTitle && popupBody) {
      popupTitle.textContent = claim.claim_id;
      popupBody.innerHTML = renderClaimDetails(claim);
      popup.classList.remove("u-hidden");
    }
    if (dagContainer) await renderDagFor(claim, dagContainer);
  });
}

async function loadClaims(): Promise<ClaimRow[]> {
  try {
    const response = await apiGet<ClaimsMetadataResponse>(
      "api/claims-metadata",
    );
    return response.claims || [];
  } catch (err) {
    console.error("[viewer] loadClaims failed", err);
    return [];
  }
}

function renderClaimsList(
  container: HTMLElement | null,
  claims: ClaimRow[],
  onSelect: (claim: ClaimRow) => void,
): void {
  if (!container) return;
  if (claims.length === 0) {
    container.innerHTML = `<p class="insert-panel-empty">No claims registered.</p>`;
    return;
  }
  container.innerHTML = claims
    .map(
      (claim) => `
      <div class="viewer-claim-row" data-claim-id="${escapeAttr(claim.claim_id)}">
        <div class="viewer-claim-header">
          <span class="viewer-claim-id">${escapeHtml(claim.claim_id)}</span>
          ${verificationBadge(claim)}
        </div>
        <div class="viewer-claim-preview">${escapeHtml(claim.preview_nature || "")}</div>
        <div class="viewer-claim-context">${escapeHtml(claim.context || "")}</div>
      </div>`,
    )
    .join("");
  container
    .querySelectorAll<HTMLElement>(".viewer-claim-row")
    .forEach((row) => {
      row.addEventListener("click", () => {
        const id = row.dataset.claimId;
        const claim = claims.find((c) => c.claim_id === id);
        if (claim) onSelect(claim);
      });
    });
}

function verificationBadge(claim: ClaimRow): string {
  const state = claim.verification?.state || "UNKNOWN";
  return `<span class="viewer-claim-badge badge-${state.toLowerCase()}">${escapeHtml(state)}</span>`;
}

function renderClaimDetails(claim: ClaimRow): string {
  const rows = [
    ["Type", claim.type],
    ["Context", claim.context || "—"],
    ["Preview", claim.preview_nature || "—"],
    ["State", claim.verification?.state || "UNKNOWN"],
  ];
  return rows
    .map(
      ([label, value]) => `
      <div class="viewer-popup-row">
        <div class="viewer-popup-label">${escapeHtml(label)}</div>
        <div class="viewer-popup-value">${escapeHtml(value)}</div>
      </div>`,
    )
    .join("");
}

async function renderDagFor(
  claim: ClaimRow,
  container: HTMLElement,
): Promise<void> {
  container.innerHTML = `<p class="insert-panel-empty">Loading DAG…</p>`;
  const url =
    `api/dag?claim=${encodeURIComponent(claim.claim_id)}` +
    `&working_dir=${encodeURIComponent(PROJECT_DIR)}`;
  try {
    const response = await fetch(API_BASE + url);
    const data = (await response.json()) as DagResponse;
    if (!data.success || !data.mermaid) {
      container.innerHTML = `<p class="insert-panel-error">${escapeHtml(data.error || "No DAG available.")}</p>`;
      return;
    }
    const mermaid = window.mermaid;
    if (!mermaid) {
      container.innerHTML = `<pre>${escapeHtml(data.mermaid)}</pre>`;
      return;
    }
    const { svg } = await mermaid.render(`dag-${Date.now()}`, data.mermaid);
    container.innerHTML = svg;
  } catch (err) {
    container.innerHTML = `<p class="insert-panel-error">DAG load failed: ${escapeHtml(String(err))}</p>`;
  }
}

function wirePdfControls(root: HTMLElement, pdf: PDFViewer | null): void {
  root
    .querySelector<HTMLElement>("#btn-pdf-zoom-in")
    ?.addEventListener("click", () => pdf?.setZoom(0.1));
  root
    .querySelector<HTMLElement>("#btn-pdf-zoom-out")
    ?.addEventListener("click", () => pdf?.setZoom(-0.1));
  root
    .querySelector<HTMLElement>("#btn-pdf-fit")
    ?.addEventListener("click", () => pdf?.setFitWidth());
}

function wireTabs(root: HTMLElement): void {
  root.querySelectorAll<HTMLElement>(".preview-tab").forEach((tab) => {
    tab.addEventListener("click", () => {
      const view = tab.dataset.view;
      root
        .querySelectorAll<HTMLElement>(".preview-tab")
        .forEach((t) => t.classList.toggle("active", t === tab));
      root
        .querySelectorAll<HTMLElement>(".preview-view")
        .forEach((v) => v.classList.toggle("active", v.id === `${view}-view`));
    });
  });
}

function escapeHtml(text: string): string {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function escapeAttr(text: string): string {
  return escapeHtml(text).replace(/'/g, "&#39;");
}

void bootstrap();
