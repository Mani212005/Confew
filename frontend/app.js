const urlInput = document.getElementById("youtube-url");
const button = document.getElementById("generate-btn");
const statusEl = document.getElementById("status");
const outputPanel = document.getElementById("output-panel");
const titleEl = document.getElementById("result-title");
const summaryEl = document.getElementById("result-summary");
const pointsEl = document.getElementById("result-points");
const infographicEl = document.getElementById("result-infographic");

function setStatus(text) {
  statusEl.textContent = text;
}

function renderResult(data) {
  titleEl.textContent = data.title || "Untitled";
  summaryEl.textContent = data.summary || "No summary returned.";
  pointsEl.innerHTML = "";

  const points = Array.isArray(data.key_points) ? data.key_points : [];
  points.forEach((point) => {
    const item = document.createElement("li");
    item.textContent = String(point);
    pointsEl.appendChild(item);
  });

  infographicEl.textContent = data.infographic_url || "N/A";
  outputPanel.hidden = false;
}

async function generate() {
  const url = urlInput.value.trim();
  if (!url) {
    setStatus("Please enter a valid YouTube URL.");
    return;
  }

  button.disabled = true;
  setStatus("Processing content...");

  try {
    const response = await fetch("/process/youtube", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url }),
    });

    if (!response.ok) {
      const errorBody = await response.json().catch(() => ({ detail: "Request failed" }));
      throw new Error(errorBody.detail || "Request failed");
    }

    const data = await response.json();
    renderResult(data);
    setStatus("Done.");
  } catch (error) {
    setStatus(`Error: ${error instanceof Error ? error.message : "Unknown error"}`);
  } finally {
    button.disabled = false;
  }
}

button.addEventListener("click", generate);
urlInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    event.preventDefault();
    generate();
  }
});
