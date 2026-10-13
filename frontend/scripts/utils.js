/*
  AI IMP NEWS OS
  Utility Functions
  Version: 2.0
*/

// ===== CLOCK =====
function updateClock() {
    const el = document.getElementById("clock");
    if (!el) return;
    const now = new Date();
    const hours = String(now.getHours()).padStart(2, "0");
    const mins = String(now.getMinutes()).padStart(2, "0");
    el.textContent = `${hours}:${mins}`;
}

// Start clock
updateClock();
setInterval(updateClock, 1000);

// ===== TOAST NOTIFICATIONS =====
function showToast(message, type = "info") {
    const container = document.getElementById("toast-container");
    if (!container) return;

    const toast = document.createElement("div");
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <span>${type === "success" ? "✅" : type === "error" ? "❌" : type === "warning" ? "⚠️" : "ℹ️"}</span>
        <span>${message}</span>
    `;

    container.appendChild(toast);

    // Auto remove after 4 seconds
    setTimeout(() => {
        toast.style.opacity = "0";
        toast.style.transform = "translateX(100%)";
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// ===== TRUNCATE TEXT =====
function truncate(text, maxLength = 60) {
    if (!text) return "";
    return text.length > maxLength ? text.substring(0, maxLength) + "..." : text;
}

// ===== FORMAT DATE =====
function formatDate(dateStr) {
    if (!dateStr) return "N/A";
    try {
        const date = new Date(dateStr);
        return date.toLocaleDateString("en-US", {
            year: "numeric",
            month: "short",
            day: "numeric"
        });
    } catch {
        return dateStr;
    }
}

// ===== QUALITY CLASS =====
function getQualityClass(score) {
    if (score >= 85) return "quality-high";
    if (score >= 60) return "quality-medium";
    return "quality-low";
}

// ===== DECISION BADGE =====
function getDecisionBadge(decision) {
    if (decision === "PUBLISH_QUEUE") {
        return `<span class="decision-publish">PUBLISH</span>`;
    }
    if (decision === "REWRITE_QUEUE") {
        return `<span class="decision-rewrite">REWRITE</span>`;
    }
    return `<span class="badge badge-info">${decision || "PENDING"}</span>`;
}