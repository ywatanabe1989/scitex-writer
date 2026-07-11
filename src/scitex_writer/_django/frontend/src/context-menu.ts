/**
 * Generic floating right-click menu — no annotation/PDF knowledge, so both
 * the PDF pane (pdf-viewer.ts, quick mark-with-category) and the comment
 * panel (annotation-ui.ts, change-category/delete) can reuse it (operator
 * request: "make effective use of right-click to enrich the menu").
 */

export interface ContextMenuAction {
  label: string;
  icon?: string;
  danger?: boolean;
  onSelect: () => void;
}

export type ContextMenuItem = ContextMenuAction | { separator: true };

let openMenu: HTMLElement | null = null;

function closeOpenMenu(): void {
  openMenu?.remove();
  openMenu = null;
  document.removeEventListener("mousedown", onOutsideClick, true);
  document.removeEventListener("keydown", onKeyDown, true);
}

function onOutsideClick(event: MouseEvent): void {
  if (openMenu && !openMenu.contains(event.target as Node)) closeOpenMenu();
}

function onKeyDown(event: KeyboardEvent): void {
  if (event.key === "Escape") closeOpenMenu();
}

/** Show a right-click menu at (clientX, clientY), clamped inside the viewport. */
export function showContextMenu(
  clientX: number,
  clientY: number,
  items: ContextMenuItem[],
): void {
  closeOpenMenu();
  const menu = document.createElement("div");
  menu.className = "ctx-menu";
  menu.setAttribute("role", "menu");

  for (const item of items) {
    if ("separator" in item) {
      const sep = document.createElement("div");
      sep.className = "ctx-menu-sep";
      menu.appendChild(sep);
      continue;
    }
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "ctx-menu-item";
    if (item.danger) btn.classList.add("ctx-menu-item--danger");
    btn.setAttribute("role", "menuitem");
    btn.innerHTML = item.icon
      ? `<i class="fas ${item.icon}"></i> ${item.label}`
      : item.label;
    btn.addEventListener("click", () => {
      closeOpenMenu();
      item.onSelect();
    });
    menu.appendChild(btn);
  }

  document.body.appendChild(menu);
  openMenu = menu;

  // Clamp inside the viewport now that the menu has real dimensions.
  const { offsetWidth: w, offsetHeight: h } = menu;
  const left = Math.min(clientX, window.innerWidth - w - 4);
  const top = Math.min(clientY, window.innerHeight - h - 4);
  menu.style.left = `${Math.max(4, left)}px`;
  menu.style.top = `${Math.max(4, top)}px`;

  document.addEventListener("mousedown", onOutsideClick, true);
  document.addEventListener("keydown", onKeyDown, true);
}
