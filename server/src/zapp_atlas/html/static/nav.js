// Mobile nav toggle.
//
// This is deliberately plain client-side JavaScript rather than htmx: opening
// and closing the menu is pure UI state with no server round trip, which is
// outside htmx's remit (htmx swaps server-rendered HTML). A CSS-only checkbox
// hack was the other option, but it can't close on outside-click or Escape, so
// a few lines of vanilla JS is the simplest correct tool here.
//
// The header ships with the full document (never htmx-swapped), so wiring up
// once on load is sufficient; there is no swapped-in copy to re-bind.
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
