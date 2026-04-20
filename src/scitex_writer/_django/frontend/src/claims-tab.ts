/**
 * Editor Claims tab — Living Paper (#133).
 *
 * Populates the `#claims-view` pane in the editor's preview column with the
 * same claim cards the viewer shows, plus:
 *   • click a card → reveal an inline detail pane + DAG render
 *   • click a card → scroll the editor to the corresponding `\vclaim{…}`
 *   • refresh button → re-fetch `api/claims-metadata` after compile
 *
 * Reuses `claims-list.ts` so editor + viewer stay consistent.
 */
import {
  type ClaimRow,
  loadClaims,
  renderClaimDetails,
  renderClaimsList,
  renderDagFor,
} from "./claims-list";

export interface ClaimsTabOptions {
  mount: HTMLElement;
  onJumpToClaim?: (claimId: string) => void;
}

export class ClaimsTab {
  private mount: HTMLElement;
  private onJumpToClaim: ClaimsTabOptions["onJumpToClaim"];
  private claims: ClaimRow[] = [];
  private detailPane: HTMLElement | null = null;
  private dagContainer: HTMLElement | null = null;

  constructor(opts: ClaimsTabOptions) {
    this.mount = opts.mount;
    this.onJumpToClaim = opts.onJumpToClaim;
  }

  async render(): Promise<void> {
    this.mount.innerHTML = this.shellHtml();
    const list = this.mount.querySelector<HTMLElement>(".claims-tab-list");
    this.detailPane =
      this.mount.querySelector<HTMLElement>(".claims-tab-detail");
    this.dagContainer =
      this.mount.querySelector<HTMLElement>(".claims-tab-dag");

    this.mount
      .querySelector<HTMLButtonElement>(".claims-tab-refresh")
      ?.addEventListener("click", () => void this.refresh());

    if (!list) return;
    list.innerHTML = `<p class="insert-panel-empty">Loading claims…</p>`;

    this.claims = await loadClaims();
    this.updateCountBadge();

    renderClaimsList(list, this.claims, (claim) => this.onClaimSelect(claim));
  }

  async refresh(): Promise<void> {
    const list = this.mount.querySelector<HTMLElement>(".claims-tab-list");
    if (!list) return;
    this.claims = await loadClaims();
    this.updateCountBadge();
    renderClaimsList(list, this.claims, (claim) => this.onClaimSelect(claim));
  }

  private updateCountBadge(): void {
    const badge = this.mount.querySelector<HTMLElement>(".claims-tab-count");
    if (badge) {
      badge.textContent =
        this.claims.length === 0
          ? "no claims"
          : `${this.claims.length} claim${this.claims.length === 1 ? "" : "s"}`;
    }
  }

  private async onClaimSelect(claim: ClaimRow): Promise<void> {
    if (this.detailPane) {
      this.detailPane.innerHTML = `
        <div class="claims-tab-detail-header">
          <code>${escapeHtml(claim.claim_id)}</code>
          ${
            this.onJumpToClaim
              ? `<button class="btn btn-secondary btn-sm claims-tab-jump"
                         title="Jump to \\vclaim in editor">
                    <i class="fas fa-arrow-right"></i> Find in source
                  </button>`
              : ""
          }
        </div>
        ${renderClaimDetails(claim)}
      `;
      this.detailPane.classList.remove("u-hidden");
      this.detailPane
        .querySelector<HTMLButtonElement>(".claims-tab-jump")
        ?.addEventListener("click", () => {
          this.onJumpToClaim?.(claim.claim_id);
        });
    }
    if (this.dagContainer) await renderDagFor(claim, this.dagContainer);
  }

  private shellHtml(): string {
    return `
      <div class="claims-tab">
        <div class="claims-tab-header">
          <span class="claims-tab-count">loading…</span>
          <button class="btn btn-icon btn-sm claims-tab-refresh"
                  title="Re-fetch claim metadata (run after a compile)">
            <i class="fas fa-sync"></i>
          </button>
        </div>
        <div class="claims-tab-list"></div>
        <div class="claims-tab-detail u-hidden"></div>
        <div class="claims-tab-dag"></div>
      </div>
    `;
  }
}

function escapeHtml(text: string): string {
  return String(text)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}
