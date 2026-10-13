/*
  AI IMP NEWS OS
  Dashboard Page Script
  Version: 2.0
*/

// ===== LOAD STATS =====
async function loadStats() {
    const data = await API.getStats();
    if (!data) return;

    const el = (id) => document.getElementById(id);

    if (el("stat-news")) el("stat-news").textContent = data.todays_news || 0;
    if (el("stat-published")) el("stat-published").textContent = data.published_today || 0;
    if (el("stat-queue")) el("stat-queue").textContent = data.publish_queue || 0;
    if (el("stat-rewrite")) el("stat-rewrite").textContent = data.failed_jobs || 0;
    if (el("stat-quality")) el("stat-quality").textContent = data.avg_quality || 0;
    if (el("stat-confidence")) el("stat-confidence").textContent = `Confidence: ${data.avg_confidence || 0}%`;
    if (el("stat-news-change")) el("stat-news-change").textContent = `${data.todays_news || 0} articles processed`;
    if (el("badge-queue")) el("badge-queue").textContent = data.publish_queue || 0;
}

// ===== LOAD PIPELINE STATUS =====
async function loadPipelineStatus() {
    const data = await API.getPipelineStatus();
    if (!data) return;

    const stages = [
        { id: "node-rss", conn: null, status: data.rss },
        { id: "node-imp", conn: "conn-1", status: data.imp_news },
        { id: "node-verify", conn: "conn-2", status: data.verify },
        { id: "node-writer", conn: "conn-3", status: data.writer },
        { id: "node-image", conn: "conn-4", status: data.image },
        { id: "node-publish", conn: "conn-5", status: data.publish }
    ];

    stages.forEach(stage => {
        const node = document.getElementById(stage.id);
        if (node) {
            node.classList.remove("success", "processing", "failed");
            if (stage.status === "success") node.classList.add("success");
            else if (stage.status === "processing") node.classList.add("processing");
        }
        if (stage.conn) {
            const conn = document.getElementById(stage.conn);
            if (conn && stage.status === "success") conn.classList.add("done");
        }
    });
}

// ===== LOAD QUEUE TABLE =====
async function loadQueue() {
    const data = await API.getQueue();
    if (!data) return;

    const tbody = document.getElementById("queue-table-body");
    if (!tbody) return;

    const allItems = [
        ...(data.publish_queue || []),
        ...(data.rewrite_queue || [])
    ];

    if (allItems.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="5" class="empty-state">
                    <div class="empty-state-icon">📭</div>
                    <div class="empty-state-text">No articles in queue. Run the pipeline to generate content.</div>
                </td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = allItems.map(item => `
        <tr>
            <td style="max-width: 300px;">
                <strong>${truncate(item.title, 50)}</strong>
                <br><small style="color: var(--text-muted);">${item.source || ""}</small>
            </td>
            <td><span class="${getQualityClass(item.quality_score)}">${item.quality_score}/100</span></td>
            <td>${item.confidence}%</td>
            <td>${getDecisionBadge(item.decision)}</td>
            <td><span class="badge badge-${item.publish_status === 'published' ? 'success' : 'info'}">${item.publish_status}</span></td>
        </tr>
    `).join("");
}

// ===== RUN PIPELINE BUTTON =====
document.addEventListener("DOMContentLoaded", function() {
    const runBtn = document.getElementById("btn-run-pipeline");
    if (runBtn) {
        runBtn.addEventListener("click", async function() {
            showToast("Pipeline starting...", "info");
            runBtn.disabled = true;
            runBtn.textContent = "⏳ Running...";

            const result = await API.runPipeline();

            if (result) {
                showToast("Pipeline completed successfully!", "success");
            } else {
                showToast("Pipeline run failed. Check backend logs.", "error");
            }

            runBtn.disabled = false;
            runBtn.textContent = "▶ Run Pipeline";
            refreshDashboard();
        });
    }

    const refreshBtn = document.getElementById("btn-refresh");
    if (refreshBtn) {
        refreshBtn.addEventListener("click", function() {
            refreshDashboard();
            showToast("Dashboard refreshed", "success");
        });
    }

    // Initial load
    refreshDashboard();

    // Auto-refresh every 30 seconds
    setInterval(refreshDashboard, 30000);
});

function refreshDashboard() {
    loadStats();
    loadPipelineStatus();
    loadQueue();
}