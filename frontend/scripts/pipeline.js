/*
  AI IMP NEWS OS
  Pipeline Journey Page Script
  Version: 2.0
*/

let currentJourneyData = [];

// ===== LOAD DATES =====
async function loadDates() {
    const data = await API.getJourneyDates();
    if (!data || !data.dates) return;

    const selector = document.getElementById("date-selector");
    if (!selector) return;

    selector.innerHTML = '<option value="latest">Latest Run</option>';
    data.dates.forEach(date => {
        const opt = document.createElement("option");
        opt.value = date;
        opt.textContent = date;
        selector.appendChild(opt);
    });
}

// ===== LOAD RAW NEWS =====
async function loadRawNews() {
    const data = await API.getRawNews();
    const grid = document.getElementById("raw-news-grid");
    const statRaw = document.getElementById("p-stat-raw");

    if (!data || !data.raw_news || data.raw_news.length === 0) {
        if (grid) grid.innerHTML = '<div class="empty-state"><div class="empty-state-icon">📡</div><div class="empty-state-text">No raw news collected yet</div></div>';
        if (statRaw) statRaw.textContent = "0";
        return;
    }

    if (statRaw) statRaw.textContent = data.total || data.raw_news.length;

    if (grid) {
        grid.innerHTML = data.raw_news.map(article => `
            <div class="news-card">
                <div class="news-card-image">📰</div>
                <div class="news-card-body">
                    <div class="news-card-source">${article.source || "Unknown"}</div>
                    <div class="news-card-title">${article.title || "No Title"}</div>
                    <div class="news-card-summary">${article.summary || "No summary available"}</div>
                    <div class="news-card-footer">
                        <span class="news-card-meta">${article.category || ""}</span>
                        <span class="news-card-score">${article.score || 0}</span>
                    </div>
                </div>
            </div>
        `).join("");
    }
}

// ===== LOAD JOURNEY =====
async function loadJourney(runDate) {
    const data = await API.getJourney(runDate);
    const grid = document.getElementById("journey-grid");

    if (!data || !data.journey || data.journey.length === 0) {
        if (grid) grid.innerHTML = '<div class="empty-state"><div class="empty-state-icon">🔄</div><div class="empty-state-text">No journey data. Run the pipeline first.</div></div>';
        updatePipelineStats(null);
        return;
    }

    currentJourneyData = data.journey;
    updatePipelineStats(data.journey);
    updateFlowNodes(data.journey);

    if (grid) {
        grid.innerHTML = data.journey.map((item, idx) => {
            const isPublished = item.publish_status === "published";
            const isRewrite = item.decision === "REWRITE_QUEUE";
            const topbarClass = isPublished ? "published" : (isRewrite ? "rewrite" : "");
            const indexLabel = isPublished ? "PUBLISHED" : (isRewrite ? "REWRITE" : `#${item.news_index}`);
            const indexClass = isPublished ? "pub" : (isRewrite ? "rew" : "");

            const stages = [
                item.imp_selected,
                item.verified,
                (item.hook && item.hook.length > 0) ? 1 : 0,
                (item.image_prompt && item.image_prompt.length > 0) ? 1 : 0,
                isPublished ? 1 : 0
            ];

            return `
                <div class="journey-card" data-index="${idx}">
                    <div class="journey-card-topbar ${topbarClass}"></div>
                    <div class="journey-card-body">
                        <span class="journey-card-index ${indexClass}">${indexLabel}</span>
                        <div class="journey-card-title">${item.title || "No Title"}</div>

                        <div class="mini-stepper">
                            ${stages.map((done, i) => {
                                const dotClass = done ? "done" : "";
                                let html = `<div class="stepper-dot ${dotClass}"></div>`;
                                if (i < stages.length - 1) html += `<div class="stepper-line ${done ? 'done' : ''}"></div>`;
                                return html;
                            }).join("")}
                        </div>

                        <div class="journey-metrics">
                            <div class="journey-metric">
                                🎯 <span class="journey-metric-value">${item.confidence || 0}%</span>
                            </div>
                            <div class="journey-metric">
                                ⭐ <span class="journey-metric-value">${item.quality_score || 0}</span>
                            </div>
                            <div class="journey-metric">
                                📊 <span class="journey-metric-value">${item.decision || "pending"}</span>
                            </div>
                        </div>

                        <div class="journey-detail-toggle" data-idx="${idx}">
                            ▶ View Full Details
                        </div>
                    </div>
                </div>
            `;
        }).join("");

        // Add click handlers for detail toggle → opens modal
        grid.querySelectorAll(".journey-detail-toggle").forEach(toggle => {
            toggle.addEventListener("click", function(e) {
                e.stopPropagation();
                const idx = parseInt(this.getAttribute("data-idx"));
                openDetailModal(currentJourneyData[idx]);
            });
        });

        // Also card click opens modal
        grid.querySelectorAll(".journey-card").forEach(card => {
            card.addEventListener("click", function() {
                const idx = parseInt(this.getAttribute("data-index"));
                openDetailModal(currentJourneyData[idx]);
            });
        });
    }
}

// ===== UPDATE STATS =====
function updatePipelineStats(journey) {
    const el = (id) => document.getElementById(id);

    if (!journey) {
        if (el("p-stat-selected")) el("p-stat-selected").textContent = "0";
        if (el("p-stat-verified")) el("p-stat-verified").textContent = "0";
        if (el("p-stat-published")) el("p-stat-published").textContent = "0";
        return;
    }

    if (el("p-stat-selected")) el("p-stat-selected").textContent = journey.length;
    if (el("p-stat-verified")) el("p-stat-verified").textContent = journey.filter(j => j.verified).length;
    if (el("p-stat-published")) el("p-stat-published").textContent = journey.filter(j => j.publish_status === "published").length;
}

// ===== UPDATE FLOW NODES =====
function updateFlowNodes(journey) {
    const hasSelected = journey.length > 0;
    const hasVerified = journey.some(j => j.verified);
    const hasWritten = journey.some(j => j.hook && j.hook.length > 0);
    const hasImage = journey.some(j => j.image_prompt && j.image_prompt.length > 0);
    const hasPublished = journey.some(j => j.publish_status === "published");

    const setActive = (id, active) => {
        const node = document.getElementById(id);
        if (node && active) node.classList.add("success");
    };
    const setConn = (id, active) => {
        const conn = document.getElementById(id);
        if (conn && active) conn.classList.add("done");
    };

    const flowRss = document.getElementById("flow-rss");
    if (flowRss) flowRss.classList.add("success");

    setActive("flow-select", hasSelected);
    setConn("fconn-1", hasSelected);
    setActive("flow-verify", hasVerified);
    setConn("fconn-2", hasVerified);
    setActive("flow-write", hasWritten);
    setConn("fconn-3", hasWritten);
    setActive("flow-image", hasImage);
    setConn("fconn-4", hasImage);
    setActive("flow-publish", hasPublished);
    setConn("fconn-5", hasPublished);
}

// ===== DETAIL MODAL =====
function openDetailModal(item) {
    if (!item) return;

    const modal = document.getElementById("detail-modal");
    if (!modal) return;

    // Fill data
    const set = (id, val) => {
        const el = document.getElementById(id);
        if (el) el.textContent = val || "-";
    };

    set("modal-title", item.title);
    set("md-source", item.source);
    set("md-category", item.category);
    set("md-link", item.link);
    set("md-summary", item.summary);
    set("md-score", item.imp_score || item.raw_score || 0);
    set("md-confidence", `${item.confidence || 0}%`);
    set("md-claims", item.claims_keywords);
    set("md-runid", item.verification_run_id);
    set("md-hook", item.hook);
    set("md-story", item.story);
    set("md-quality", `${item.quality_score || 0}/100`);
    set("md-decision", item.decision);
    set("md-imgprompt", item.image_prompt);
    set("md-imgstatus", item.image_status);
    set("md-slug", item.slug);
    set("md-metatitle", item.meta_title);
    set("md-stage", item.stage_reached);
    set("md-publishedat", item.published_at);

    // Reset tabs
    document.querySelectorAll("#modal-tabs .tab").forEach(t => t.classList.remove("active"));
    document.querySelectorAll(".tab-content").forEach(tc => tc.classList.remove("active"));
    document.querySelector('#modal-tabs .tab[data-tab="original"]').classList.add("active");
    document.getElementById("tab-original").classList.add("active");

    modal.classList.add("open");
}

// ===== INIT =====
document.addEventListener("DOMContentLoaded", function() {

    // Load initial data
    loadDates();
    loadRawNews();
    loadJourney("latest");

    // Date selector
    const dateSelector = document.getElementById("date-selector");
    if (dateSelector) {
        dateSelector.addEventListener("change", function() {
            loadJourney(this.value);
        });
    }

    // Refresh button
    const refreshBtn = document.getElementById("btn-refresh");
    if (refreshBtn) {
        refreshBtn.addEventListener("click", function() {
            loadRawNews();
            const selectedDate = dateSelector ? dateSelector.value : "latest";
            loadJourney(selectedDate);
            showToast("Pipeline data refreshed", "success");
        });
    }

    // Toggle raw news
    const toggleBtn = document.getElementById("btn-toggle-raw");
    const rawGrid = document.getElementById("raw-news-grid");
    if (toggleBtn && rawGrid) {
        toggleBtn.addEventListener("click", function() {
            rawGrid.classList.toggle("expanded");
            if (rawGrid.classList.contains("expanded")) {
                toggleBtn.textContent = "Hide Raw News ▲";
            } else {
                toggleBtn.textContent = "Show All Raw News ▼";
            }
        });
    }

    // Modal close
    const modalClose = document.getElementById("modal-close");
    const modalOverlay = document.getElementById("detail-modal");
    if (modalClose) {
        modalClose.addEventListener("click", function() {
            modalOverlay.classList.remove("open");
        });
    }
    if (modalOverlay) {
        modalOverlay.addEventListener("click", function(e) {
            if (e.target === modalOverlay) {
                modalOverlay.classList.remove("open");
            }
        });
    }

    // Modal tabs
    document.querySelectorAll("#modal-tabs .tab").forEach(tab => {
        tab.addEventListener("click", function() {
            const tabName = this.getAttribute("data-tab");

            document.querySelectorAll("#modal-tabs .tab").forEach(t => t.classList.remove("active"));
            document.querySelectorAll(".tab-content").forEach(tc => tc.classList.remove("active"));

            this.classList.add("active");
            const content = document.getElementById(`tab-${tabName}`);
            if (content) content.classList.add("active");
        });
    });

    // Auto-refresh every 30 seconds
    setInterval(function() {
        loadRawNews();
        const selectedDate = dateSelector ? dateSelector.value : "latest";
        loadJourney(selectedDate);
    }, 30000);
});