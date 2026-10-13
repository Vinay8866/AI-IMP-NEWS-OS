/*
  AI IMP NEWS OS
  Dashboard Page Script
  Version: 2.0
*/

// ===== LOAD STATS =====
// async function loadStats() {
//     const data = await API.getStats();
//     if (!data) return;

//     const el = (id) => document.getElementById(id);

//     if (el("stat-news")) el("stat-news").textContent = data.todays_news || 0;
//     if (el("stat-published")) el("stat-published").textContent = data.published_today || 0;
//     if (el("stat-queue")) el("stat-queue").textContent = data.publish_queue || 0;
//     if (el("stat-rewrite")) el("stat-rewrite").textContent = data.failed_jobs || 0;
//     if (el("stat-quality")) el("stat-quality").textContent = data.avg_quality || 0;
//     if (el("stat-confidence")) el("stat-confidence").textContent = `Confidence: ${data.avg_confidence || 0}%`;
//     if (el("stat-news-change")) el("stat-news-change").textContent = `${data.todays_news || 0} articles processed`;
//     if (el("badge-queue")) el("badge-queue").textContent = data.publish_queue || 0;
// }

async function loadStats() {
    const [data, queue] = await Promise.all([
        API.getStats(),
        API.getQueue()
    ]);

    if (!data) return;

    const latest = data.latest_run || {};
    const setText = (id, value) => {
        const element = document.getElementById(id);
        if (element) element.textContent = value;
    };

    const setCardLabel = (id, label, detail) => {
        const card = document.getElementById(id)?.closest(".stat-card");
        if (!card) return;

        const labelElement = card.querySelector(".stat-card-label");
        const detailElement = card.querySelector(".stat-card-change");

        if (labelElement) labelElement.textContent = label;
        if (detailElement) detailElement.textContent = detail;
    };

    setText("stat-news", data.raw_news ?? 0);
    setCardLabel(
        "stat-news",
        "Collected News",
        "All articles stored in database"
    );

    setText("stat-published", data.published_total ?? 0);
    setCardLabel(
        "stat-published",
        "Locally Published",
        "All dates"
    );

    setText("stat-queue", queue?.publish_count ?? "--");
    setText("stat-rewrite", queue?.rewrite_count ?? "--");
    setText("badge-queue", queue?.publish_count ?? "--");

    const quality = latest.avg_quality;
    const confidence = latest.avg_confidence;

    setText(
        "stat-quality",
        quality == null ? "--" : Number(quality).toFixed(1)
    );

    setText(
        "stat-confidence",
        confidence == null
            ? "No run data"
            : `Confidence: ${Number(confidence).toFixed(1)}% | Run: ${latest.run_date}`
    );

    const qualityCard = document
        .getElementById("stat-quality")
        ?.closest(".stat-card");

    const qualityLabel = qualityCard?.querySelector(".stat-card-label");
    if (qualityLabel) qualityLabel.textContent = "Latest Run Avg Quality";
}

// ===== LOAD PIPELINE STATUS =====
// async function loadPipelineStatus() {
//     const data = await API.getPipelineStatus();
//     if (!data) return;

//     const stages = [
//         { id: "node-rss", conn: null, status: data.rss },
//         { id: "node-imp", conn: "conn-1", status: data.imp_news },
//         { id: "node-verify", conn: "conn-2", status: data.verify },
//         { id: "node-writer", conn: "conn-3", status: data.writer },
//         { id: "node-image", conn: "conn-4", status: data.image },
//         { id: "node-publish", conn: "conn-5", status: data.publish }
//     ];

//     stages.forEach(stage => {
//         const node = document.getElementById(stage.id);
//         if (node) {
//             node.classList.remove("success", "processing", "failed");
//             if (stage.status === "success") node.classList.add("success");
//             else if (stage.status === "processing") node.classList.add("processing");
//         }
//         if (stage.conn) {
//             const conn = document.getElementById(stage.conn);
//             if (conn && stage.status === "success") conn.classList.add("done");
//         }
//     });
// }



async function loadPipelineStatus() {
    const [pipeline, stats] = await Promise.all([
        API.getPipelineStatus(),
        API.getStats()
    ]);

    const journey = Array.isArray(pipeline?.journey)
        ? pipeline.journey
        : [];

    const stages = [
        {
            id: "node-imp",
            conn: "conn-1",
            check: item => Number(item.imp_selected) === 1
        },
        {
            id: "node-verify",
            conn: "conn-2",
            check: item => Number(item.verified) === 1
        },
        {
            id: "node-writer",
            conn: "conn-3",
            check: item => Boolean(item.hook && item.story)
        },
        {
            id: "node-image",
            conn: "conn-4",
            check: item => Boolean(
                item.image_path &&
                ["generated", "placeholder_ready"].includes(item.image_status)
            )
        },
        {
            id: "node-publish",
            conn: "conn-5",
            check: item => item.publish_status === "published"
        }
    ];

    const rssNode = document.getElementById("node-rss");
    if (rssNode) {
        rssNode.classList.remove("success", "processing", "failed");
        if (stats && Number(stats.raw_news) > 0) {
            rssNode.classList.add("success");
        }
        rssNode.title = stats
            ? `${stats.raw_news ?? 0} news articles stored`
            : "Collection status unavailable";
    }

    stages.forEach(stage => {
        const completed = journey.filter(stage.check).length;
        const allComplete = journey.length > 0 &&
            completed === journey.length;

        const node = document.getElementById(stage.id);
        if (node) {
            node.classList.remove("success", "processing", "failed");
            if (allComplete) node.classList.add("success");

            node.title = !pipeline
                ? "Pipeline status unavailable"
                : journey.length === 0
                    ? "No run records available"
                    : `${completed}/${journey.length} completed — run ${pipeline.run_date}`;
        }

        const connector = document.getElementById(stage.conn);
        if (connector) {
            connector.classList.toggle("done", allComplete);
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