/*
  AI IMP NEWS OS
  Analytics Page Script
  Version: 2.0
*/

async function loadAnalytics() {
    try {
        const data = await API.getStats();
        if (!data) {
            console.log("Analytics: No data from API (backend may be offline)");
            return;
        }

        const el = function(id) {
            return document.getElementById(id);
        };

        if (el("a-total")) {
            el("a-total").textContent = data.todays_news || 0;
        }
        if (el("a-quality")) {
            el("a-quality").textContent = data.avg_quality || 0;
        }
        if (el("a-confidence")) {
            el("a-confidence").textContent = (data.avg_confidence || 0) + "%";
        }

        var total = data.todays_news || 0;
        var published = data.published_today || 0;
        var rate = total > 0 ? Math.round((published / total) * 100) : 0;
        if (el("a-rate")) {
            el("a-rate").textContent = rate + "%";
        }

        console.log("Analytics loaded successfully");
    } catch (err) {
        console.error("Analytics load error:", err);
    }
}

document.addEventListener("DOMContentLoaded", function() {
    console.log("Analytics page ready");

    // Load data
    loadAnalytics();

    // Refresh button
    var refreshBtn = document.getElementById("btn-refresh");
    if (refreshBtn) {
        refreshBtn.addEventListener("click", function() {
            loadAnalytics();
            if (typeof showToast === "function") {
                showToast("Analytics refreshed", "success");
            }
        });
    }

    // Auto refresh every 30 sec
    setInterval(loadAnalytics, 30000);
});