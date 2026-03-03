// static/app.js

(function () {
  // Confirm delete
  document.addEventListener("click", (e) => {
    const a = e.target.closest("a[data-confirm]");
    if (!a) return;
    const msg = a.getAttribute("data-confirm") || "Are you sure?";
    if (!confirm(msg)) e.preventDefault();
  });

  // Search filter (client-side)
  const search = document.getElementById("taskSearch");
  const list = document.getElementById("taskList");
  if (search && list) {
    search.addEventListener("input", () => {
      const q = search.value.trim().toLowerCase();
      list.querySelectorAll(".item[data-title]").forEach((li) => {
        const title = li.getAttribute("data-title") || "";
        li.style.display = title.includes(q) ? "" : "none";
      });
    });
  }

  // Auto-hide flash messages
  const flashes = document.querySelectorAll(".flash");
  if (flashes.length) {
    setTimeout(() => {
      flashes.forEach((f) => f.classList.add("fade-out"));
      setTimeout(() => flashes.forEach((f) => f.remove()), 600);
    }, 2500);
  }
})();