// Shared client-side UI behaviors, loaded on every page: the mobile nav and
// user menu, the submission overflow menus, and the modals. Plain JS, no build
// step, since each is pure UI state with no server round trip.

// Toggle a menu open/closed with a button, closing on outside-click and Escape.
const wireToggle = (root, trigger, openClass) => {
  if (!root || !trigger) return;

  const setOpen = (open) => {
    root.classList.toggle(openClass, open);
    trigger.setAttribute("aria-expanded", String(open));
  };

  trigger.addEventListener("click", (e) => {
    e.stopPropagation();
    setOpen(!root.classList.contains(openClass));
  });
  document.addEventListener("click", (e) => {
    if (!root.contains(e.target)) setOpen(false);
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") setOpen(false);
  });

  return setOpen;
};

// Mobile nav: also close when a link inside it is tapped.
const closeNav = wireToggle(
  document.querySelector(".site-header"),
  document.querySelector(".site-nav__burger"),
  "is-nav-open",
);
const nav = document.querySelector(".site-nav");
if (nav && closeNav) {
  nav.addEventListener("click", (e) => {
    if (e.target.closest("a")) closeNav(false);
  });
}

// Signed-in user menu.
wireToggle(
  document.querySelector(".user-menu"),
  document.querySelector(".user-chip"),
  "is-user-open",
);

// Resources dropdown in the main nav.
wireToggle(
  document.querySelector(".nav-menu"),
  document.querySelector(".nav-menu__trigger"),
  "is-nav-menu-open",
);

// Overflow menus (<details.sub-menu>): close on outside-click and Escape.
// One open at a time; delegated so htmx-swapped rows are covered.
const closeMenus = (except) => {
  document.querySelectorAll("details.sub-menu[open]").forEach((d) => {
    if (d !== except) d.removeAttribute("open");
  });
};
document.addEventListener("click", (e) => {
  const open = e.target.closest("details.sub-menu[open]");
  closeMenus(open);
});
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") closeMenus(null);
});

// Modals (<dialog class="modal">): a button opens by id, and it closes on
// Cancel or a click on the backdrop. Escape is native to <dialog>.
document.addEventListener("click", (e) => {
  const opener = e.target.closest("[data-open-modal]");
  if (opener) {
    const modal = document.getElementById(opener.dataset.openModal);
    if (opener.dataset.deleteUrl && modal) {
      // Fill the shared confirm dialog from the row that opened it.
      modal.querySelector("[data-confirm-form]").action = opener.dataset.deleteUrl;
      modal.querySelector("[data-confirm-text]").textContent =
        `Remove ${opener.dataset.deleteName}? This cannot be undone.`;
    }
    if (opener.dataset.editUrl && modal) {
      // Fill the shared edit dialog with the row's current value.
      modal.querySelector("[data-edit-form]").action = opener.dataset.editUrl;
      modal.querySelector("[data-edit-input]").value = opener.dataset.editValue;
    }
    modal?.showModal();
    return;
  }
  if (e.target.closest("[data-close-modal]")) {
    e.target.closest("dialog")?.close();
    return;
  }
  // A click on the dialog element itself (not its panel) is the backdrop.
  if (e.target.matches("dialog.modal")) e.target.close();
});

// Toast: auto-dismiss the transient notice a few seconds after it appears.
const toast = document.querySelector("[data-toast]");
if (toast) {
  setTimeout(() => {
    toast.classList.add("toast--hiding");
    toast.addEventListener("transitionend", () => toast.remove());
  }, 4000);
}
