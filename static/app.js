const input = document.getElementById("animeInput");
const button = document.getElementById("recommendBtn");
const suggestions = document.getElementById("suggestions");
const resultsSection = document.getElementById("resultsSection");
const results = document.getElementById("results");
const queryTitle = document.getElementById("queryTitle");
const resultCount = document.getElementById("resultCount");
const loading = document.getElementById("loading");
const errorBox = document.getElementById("errorBox");

let timer;

input.addEventListener("input", () => {
  clearTimeout(timer);
  const q = input.value.trim();
  if (q.length < 2) {
    suggestions.classList.add("hidden");
    return;
  }
  timer = setTimeout(() => loadSuggestions(q), 180);
});

async function loadSuggestions(q) {
  try {
    const res = await fetch(`/api/anime?q=${encodeURIComponent(q)}&limit=8`);
    const data = await res.json();
    suggestions.innerHTML = data.map(a =>
      `<div class="suggestion" data-name="${escapeHtml(a.name)}">${escapeHtml(a.name)}</div>`
    ).join("");
    suggestions.classList.toggle("hidden", data.length === 0);
    document.querySelectorAll(".suggestion").forEach(el => {
      el.addEventListener("click", () => {
        input.value = el.dataset.name;
        suggestions.classList.add("hidden");
        getRecommendations();
      });
    });
  } catch (_) {}
}

button.addEventListener("click", getRecommendations);
input.addEventListener("keydown", e => {
  if (e.key === "Enter") getRecommendations();
});
document.querySelectorAll(".quick-picks button").forEach(btn => {
  btn.addEventListener("click", () => {
    input.value = btn.dataset.anime;
    getRecommendations();
  });
});

document.addEventListener("click", e => {
  if (!e.target.closest(".search-shell")) suggestions.classList.add("hidden");
});

async function getRecommendations() {
  const name = input.value.trim();
  if (!name) return showError("Please enter an anime name first.");

  suggestions.classList.add("hidden");
  errorBox.classList.add("hidden");
  resultsSection.classList.add("hidden");
  loading.classList.remove("hidden");

  try {
    const res = await fetch(`/api/recommend?name=${encodeURIComponent(name)}&top_n=10`);
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Could not generate recommendations.");

    queryTitle.textContent = name;
    resultCount.textContent = `${data.recommendations.length} recommendations`;
    results.innerHTML = data.recommendations.map((a, i) => card(a, i + 1)).join("");
    resultsSection.classList.remove("hidden");
    resultsSection.scrollIntoView({ behavior: "smooth", block: "start" });
  } catch (err) {
    showError(err.message);
  } finally {
    loading.classList.add("hidden");
  }
}

function card(a, rank) {
  return `
    <article class="card">
      <div class="card-top">
        <span class="rank">#${rank}</span>
        <span class="score">${a.similarity}% match</span>
      </div>
      <h3>${escapeHtml(a.name)}</h3>
      <div class="genre">${escapeHtml(a.genre)}</div>
      <div class="meta">
        <span>★ ${a.rating}</span>
        <span>${escapeHtml(a.type)}</span>
        <span>${escapeHtml(a.episodes)} eps</span>
        <span>${formatMembers(a.members)} members</span>
      </div>
    </article>
  `;
}

function showError(message) {
  loading.classList.add("hidden");
  errorBox.textContent = message;
  errorBox.classList.remove("hidden");
}

function formatMembers(n) {
  if (n >= 1000000) return (n / 1000000).toFixed(1) + "M";
  if (n >= 1000) return (n / 1000).toFixed(1) + "K";
  return n.toString();
}

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, c => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;"
  }[c]));
}
