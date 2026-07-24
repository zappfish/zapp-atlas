// Mobile nav toggle: plain client-side JS, not htmx, since opening/closing the
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

  // Close when a nav link is tapped.
  nav.addEventListener("click", function (e) {
    if (e.target.closest("a")) setOpen(false);
  });

  // Close on click outside the header.
  document.addEventListener("click", function (e) {
    if (!header.contains(e.target)) setOpen(false);
  });

  // Close on Escape.
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") setOpen(false);
  });
})();
