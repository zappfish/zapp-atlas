// Mobile nav toggle: plain client-side JS, since opening/closing the
// menu is pure UI state with no server round trip (and needs outside-click/Esc).
(function () {
  const burger = document.querySelector(".site-nav__burger");
  const nav = document.querySelector(".site-nav");
  const header = document.querySelector(".site-header");
  if (!burger || !nav || !header) return;

  function setOpen(open) {
    header.classList.toggle("is-nav-open", open);
    burger.setAttribute("aria-expanded", String(open));
  }

  burger.addEventListener("click", function (e) {
    e.stopPropagation();
    setOpen(!header.classList.contains("is-nav-open"));
  });

  nav.addEventListener("click", function (e) {
    if (e.target.closest("a")) setOpen(false);
  });
  document.addEventListener("click", function (e) {
    if (!header.contains(e.target)) setOpen(false);
  });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") setOpen(false);
  });
})();

// Signed-in user menu: same toggle / outside-click / Escape pattern.
(function () {
  const menu = document.querySelector(".user-menu");
  const chip = menu && menu.querySelector(".user-chip");
  if (!menu || !chip) return;

  function setOpen(open) {
    menu.classList.toggle("is-user-open", open);
    chip.setAttribute("aria-expanded", String(open));
  }

  chip.addEventListener("click", function (e) {
    e.stopPropagation();
    setOpen(!menu.classList.contains("is-user-open"));
  });

  document.addEventListener("click", function (e) {
    if (!menu.contains(e.target)) setOpen(false);
  });

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") setOpen(false);
  });
})();
