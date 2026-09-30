// Progressive enhancement only; the app works without JavaScript.
document.addEventListener("submit", function (e) {
  var f = e.target;
  if (f && f.dataset && f.dataset.confirm && !window.confirm(f.dataset.confirm)) { e.preventDefault(); }
});
document.addEventListener("click", function (e) {
  var b = e.target.closest ? e.target.closest("[data-copy]") : null;
  if (!b) return;
  var el = document.getElementById(b.dataset.copy);
  if (el && navigator.clipboard) { navigator.clipboard.writeText(el.textContent.trim()); b.textContent = "Copied"; }
});
