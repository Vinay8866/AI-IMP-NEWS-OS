/*
  AI IMP NEWS OS
  News Viewer Script
  Version: 2.1 (Fixed Image URL from Backend Server)
*/

let currentData = {
    raw: [],
    journey: []
};

// ===== TAB SWITCHING & INIT =====
document.addEventListener("DOMContentLoaded", function() {

    loadAllData();

    document.querySelectorAll(".stage-tab").forEach(tab => {
        tab.addEventListener("click", function() {
            const stage = this.getAttribute("data-stage");
            switchStage(stage);
        });
    });

    const refreshBtn = document.getElementById("btn-refresh");
    if (refreshBtn) {
        refreshBtn.addEventListener("click", function() {
            loadAllData();
            showToast("सारा Data Refresh हो गया", "success");
        });
    }

    const dateSelector = document.getElementById("date-selector");
    if (dateSelector) {
        dateSelector.addEventListener("change", function() {
            loadJourneyData(this.value);
        });
    }

    const modalClose = document.getElementById("am-close");
    const modalOverlay = document.getElementById("article-modal");
    if (modalClose) {
        modalClose.addEventListener("click", () => modalOverlay.classList.remove("open"));
    }
    if (modalOverlay) {
        modalOverlay.addEventListener("click", function(e) {
            if (e.target === modalOverlay) modalOverlay.classList.remove("open");
        });
    }

    loadDates();
    setInterval(loadAllData, 30000);
});

function switchStage(stage) {
    document.querySelectorAll(".stage-tab").forEach(t => t.classList.remove("active"));
    document.querySelectorAll(".stage-content").forEach(c => c.classList.remove("active"));

    document.querySelector(`.stage-tab[data-stage="${stage}"]`).classList.add("active");
    document.getElementById(`stage-${stage}`).classList.add("active");
}

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

async function loadAllData() {
    await Promise.all([
        loadRawData(),
        loadJourneyData("latest")
    ]);
}

async function loadRawData() {
    const data = await API.getRawNews();
    if (!data || !data.raw_news) return;

    currentData.raw = data.raw_news;
    document.getElementById("count-raw").textContent = data.total || 0;

    const grid = document.getElementById("raw-viewer-grid");
    if (!grid) return;

    if (data.raw_news.length === 0) {
        grid.innerHTML = `
            <div class="empty-state" style="grid-column: 1/-1;">
                <div class="empty-state-icon">📡</div>
                <div class="empty-state-text">अभी तक कोई Raw News नहीं मिली। पहले Pipeline Run करें।</div>
            </div>
        `;
        return;
    }

    grid.innerHTML = data.raw_news.map((article, idx) => `
        <div class="viewer-card" data-type="raw" data-idx="${idx}">
            ${article.image
                ? `<img class="viewer-card-image" src="${article.image}" alt="${article.title}" onerror="this.outerHTML='<div class=&quot;viewer-card-image-placeholder&quot;>📰</div>'">`
                : `<div class="viewer-card-image-placeholder">📰</div>`
            }
            <div class="viewer-card-body">
                <div class="viewer-card-source">${article.source || "Unknown"}</div>
                <div class="viewer-card-title">${article.title || "No Title"}</div>
                <div class="viewer-card-summary">${article.summary || "No summary available"}</div>
                <div class="viewer-card-footer">
                    <span class="viewer-card-meta">${article.category || "General"}</span>
                    <span class="viewer-card-badge badge-selected">Score: ${article.score || 0}</span>
                </div>
            </div>
        </div>
    `).join("");

    grid.querySelectorAll(".viewer-card").forEach(card => {
        card.addEventListener("click", function() {
            const idx = parseInt(this.getAttribute("data-idx"));
            openRawArticleModal(currentData.raw[idx]);
        });
    });
}

async function loadJourneyData(runDate) {
    const data = await API.getJourney(runDate);
    if (!data || !data.journey) {
        updateJourneyCounts(null);
        return;
    }

    currentData.journey = data.journey;
    updateJourneyCounts(data.journey);

    renderSelectedGrid(data.journey);
    renderVerifiedGrid(data.journey);
    renderHumanizedGrid(data.journey);
    renderImageGrid(data.journey);
    renderFinalGrid(data.journey);
}

function updateJourneyCounts(journey) {
    const el = (id) => document.getElementById(id);

    if (!journey) {
        if (el("count-selected")) el("count-selected").textContent = "0";
        if (el("count-verified")) el("count-verified").textContent = "0";
        if (el("count-humanized")) el("count-humanized").textContent = "0";
        if (el("count-image")) el("count-image").textContent = "0";
        if (el("count-final")) el("count-final").textContent = "0";
        return;
    }

    if (el("count-selected")) el("count-selected").textContent = journey.length;
    if (el("count-verified")) el("count-verified").textContent = journey.filter(j => j.verified).length;
    if (el("count-humanized")) el("count-humanized").textContent = journey.filter(j => j.hook && j.hook.length > 0).length;
    if (el("count-image")) el("count-image").textContent = journey.filter(j => j.image_prompt && j.image_prompt.length > 0).length;
    if (el("count-final")) el("count-final").textContent = journey.filter(j => j.publish_status === "published").length;
}

function renderSelectedGrid(journey) {
    const grid = document.getElementById("selected-viewer-grid");
    if (!grid) return;

    if (journey.length === 0) {
        grid.innerHTML = `<div class="empty-state" style="grid-column: 1/-1;">
            <div class="empty-state-icon">⭐</div>
            <div class="empty-state-text">अभी तक कोई News Selected नहीं हुई।</div>
        </div>`;
        return;
    }

    grid.innerHTML = journey.map((item, idx) => `
        <div class="viewer-card" data-type="selected" data-idx="${idx}">
            <div class="viewer-card-image-placeholder">⭐</div>
            <div class="viewer-card-body">
                <div class="viewer-card-source">${item.source || "Unknown"}</div>
                <div class="viewer-card-title">${item.title || "No Title"}</div>
                <div class="viewer-card-summary">${item.summary || "No summary"}</div>
                <div class="viewer-card-footer">
                    <span class="viewer-card-meta">#${item.news_index}</span>
                    <span class="viewer-card-badge badge-selected">IMP Score: ${item.imp_score || 0}</span>
                </div>
            </div>
        </div>
    `).join("");

    grid.querySelectorAll(".viewer-card").forEach(card => {
        card.addEventListener("click", function() {
            const idx = parseInt(this.getAttribute("data-idx"));
            openFullArticleModal(currentData.journey[idx]);
        });
    });
}

function renderVerifiedGrid(journey) {
    const grid = document.getElementById("verified-viewer-grid");
    if (!grid) return;

    const verified = journey.filter(j => j.verified);

    if (verified.length === 0) {
        grid.innerHTML = `<div class="empty-state" style="grid-column: 1/-1;">
            <div class="empty-state-icon">✅</div>
            <div class="empty-state-text">अभी तक कोई News Verify नहीं हुई।</div>
        </div>`;
        return;
    }

    grid.innerHTML = verified.map((item) => `
        <div class="verified-card">
            <div class="verified-card-header">
                <span class="verified-card-badge">✓ VERIFIED #${item.news_index}</span>
                <div class="verified-card-title">${item.title || "No Title"}</div>
            </div>
            <div class="verified-card-body">
                <div class="verified-card-section">
                    <div class="verified-card-section-title">📝 Full Summary</div>
                    <div class="verified-card-content">${item.summary || "No content"}</div>
                </div>
                <div class="verified-card-section">
                    <div class="verified-card-section-title">🔑 Key Claims / Keywords</div>
                    <div class="verified-card-content">${item.claims_keywords || "No claims"}</div>
                </div>
                <div class="verified-card-section">
                    <div class="verified-card-section-title">📰 Source</div>
                    <div class="verified-card-content">
                        <strong>${item.source}</strong> | ${item.category || "General"}
                        <br><a href="${item.link}" target="_blank" style="color: var(--brand-primary); font-size: 12px;">${item.link || ""}</a>
                    </div>
                </div>
                <div class="verified-card-stats">
                    <div class="verified-stat">
                        <div class="verified-stat-value">${item.confidence || 0}%</div>
                        <div class="verified-stat-label">Confidence</div>
                    </div>
                    <div class="verified-stat">
                        <div class="verified-stat-value">${item.imp_score || 0}</div>
                        <div class="verified-stat-label">IMP Score</div>
                    </div>
                    <div class="verified-stat">
                        <div class="verified-stat-value">${item.verified ? "✓" : "✗"}</div>
                        <div class="verified-stat-label">Status</div>
                    </div>
                </div>
            </div>
        </div>
    `).join("");
}

function renderHumanizedGrid(journey) {
    const grid = document.getElementById("humanized-viewer-grid");
    if (!grid) return;

    const humanized = journey.filter(j => j.hook && j.hook.length > 0);

    if (humanized.length === 0) {
        grid.innerHTML = `<div class="empty-state" style="grid-column: 1/-1;">
            <div class="empty-state-icon">✍️</div>
            <div class="empty-state-text">अभी तक कोई News Humanize नहीं हुई।</div>
        </div>`;
        return;
    }

    grid.innerHTML = humanized.map(item => `
        <div class="humanized-card">
            <div class="humanized-card-header">
                <span class="humanized-card-badge">✍️ HUMANIZED #${item.news_index}</span>
                <span class="humanized-quality">⭐ ${item.quality_score || 0}/100</span>
            </div>
            <div class="humanized-card-body">
                <div class="verified-card-section-title">🎯 Original Title</div>
                <h3 style="font-size: 16px; font-weight: 700; margin-bottom: 16px; color: var(--text-primary);">${item.title}</h3>

                <div class="verified-card-section-title">🎣 Hook (Opening Line)</div>
                <div class="humanized-hook">${item.hook || "No hook"}</div>

                <div class="verified-card-section-title">📖 Full Story</div>
                <div class="humanized-story">${item.story || "No story content"}</div>

                <div class="humanized-meta">
                    <div class="humanized-meta-item">
                        🎯 Confidence: <span class="humanized-meta-value">${item.confidence || 0}%</span>
                    </div>
                    <div class="humanized-meta-item">
                        📊 Decision: <span class="humanized-meta-value">${item.decision || "Pending"}</span>
                    </div>
                    <div class="humanized-meta-item">
                        📁 File: <span class="humanized-meta-value">${item.blog_file ? "✓ Saved" : "Not saved"}</span>
                    </div>
                </div>
            </div>
        </div>
    `).join("");
}

// ===== FIX HERE: Serving Images from FastAPI Backend (Port 8000) =====
function renderImageGrid(journey) {
    const grid = document.getElementById("image-viewer-grid");
    if (!grid) return;

    const withImage = journey.filter(j => j.image_prompt && j.image_prompt.length > 0);

    if (withImage.length === 0) {
        grid.innerHTML = `<div class="empty-state" style="grid-column: 1/-1;">
            <div class="empty-state-icon">🎨</div>
            <div class="empty-state-text">अभी तक कोई Image Generate नहीं हुई।</div>
        </div>`;
        return;
    }

    grid.innerHTML = withImage.map(item => {
        // Backend Port 8000 static mount
        const imagePath = item.slug ? `${API_BASE}/media/images/${item.slug}.png` : null;

        return `
            <div class="image-card">
                <div class="image-card-image-section">
                    ${imagePath
                        ? `<img class="image-card-image" src="${imagePath}" alt="${item.title}" onerror="this.outerHTML='<div class=&quot;image-card-image-placeholder&quot;>🎨</div>'">`
                        : `<div class="image-card-image-placeholder">🎨</div>`
                    }
                </div>
                <div class="image-card-body">
                    <span class="verified-card-badge" style="background: var(--brand-primary);">🎨 WITH IMAGE #${item.news_index}</span>
                    <div class="image-card-title" style="margin-top: 8px;">${item.title}</div>

                    <div class="verified-card-section-title" style="margin-top: 16px;">🎨 AI Image Prompt</div>
                    <div class="image-card-prompt">${item.image_prompt || "No prompt"}</div>

                    <div class="verified-card-section-title" style="margin-top: 16px;">🎣 Hook</div>
                    <p style="font-size: 13px; color: var(--text-secondary); font-style: italic;">${item.hook || "No hook"}</p>

                    <div class="humanized-meta" style="margin-top: 16px;">
                        <div class="humanized-meta-item">
                            Status: <span class="humanized-meta-value">${item.image_status || "pending"}</span>
                        </div>
                        <div class="humanized-meta-item">
                            Slug: <span class="humanized-meta-value">${item.slug || "N/A"}</span>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }).join("");
}

// ===== FIX HERE TOO: Serving Images from FastAPI Backend (Port 8000) =====
function renderFinalGrid(journey) {
    const grid = document.getElementById("final-viewer-grid");
    if (!grid) return;

    const final = journey.filter(j => j.hook && j.hook.length > 0);

    if (final.length === 0) {
        grid.innerHTML = `<div class="empty-state">
            <div class="empty-state-icon">🏆</div>
            <div class="empty-state-text">अभी तक कोई Final Post तैयार नहीं है।</div>
        </div>`;
        return;
    }

    grid.innerHTML = final.map(item => {
        // Backend Port 8000 static mount
        const imagePath = item.slug ? `${API_BASE}/media/images/${item.slug}.png` : null;
        const isPublished = item.publish_status === "published";
        const ribbonText = isPublished ? "✓ PUBLISHED" : (item.decision === "PUBLISH_QUEUE" ? "📤 READY TO PUBLISH" : "⏳ IN QUEUE");

        return `
            <div class="final-card">
                <div class="final-card-image-section">
                    <div class="final-card-ribbon">${ribbonText}</div>
                    ${imagePath
                        ? `<img class="final-card-image" src="${imagePath}" alt="${item.title}" onerror="this.outerHTML='<div class=&quot;final-card-image-placeholder&quot;>🏆</div>'">`
                        : `<div class="final-card-image-placeholder">🏆</div>`
                    }
                </div>
                <div class="final-card-body">
                    <div class="final-card-source">#${item.news_index} • ${item.source || "Unknown"} • ${item.category || "General"}</div>
                    <div class="final-card-title">${item.title}</div>
                    <div class="final-card-hook">${item.hook || "No hook"}</div>
                    <div class="final-card-story">${item.story || "No story"}</div>

                    <div class="final-card-stats">
                        <div class="final-stat">
                            <div class="final-stat-label">Confidence</div>
                            <div class="final-stat-value">${item.confidence || 0}%</div>
                        </div>
                        <div class="final-stat">
                            <div class="final-stat-label">Quality</div>
                            <div class="final-stat-value">${item.quality_score || 0}/100</div>
                        </div>
                        <div class="final-stat">
                            <div class="final-stat-label">Decision</div>
                            <div class="final-stat-value" style="font-size: 12px;">${item.decision || "Pending"}</div>
                        </div>
                        <div class="final-stat">
                            <div class="final-stat-label">SEO Slug</div>
                            <div class="final-stat-value" style="font-size: 12px;">${item.slug || "N/A"}</div>
                        </div>
                    </div>

                    <div class="final-card-actions">
                        <button class="final-btn final-btn-primary" onclick="openFullArticleModal(currentData.journey.find(j => j.news_index === ${item.news_index}))">
                            👁️ View Full Details
                        </button>
                        <a href="${item.link}" target="_blank" class="final-btn final-btn-outline">
                            🔗 Original Source
                        </a>
                    </div>
                </div>
            </div>
        `;
    }).join("");
}

function openRawArticleModal(article) {
    if (!article) return;

    const set = (id, val) => {
        const el = document.getElementById(id);
        if (el) el.textContent = val || "-";
    };

    set("am-title", article.title);
    set("am-source", article.source);
    set("am-category", article.category);
    set("am-score", article.score || 0);
    set("am-hook", "N/A (Raw News)");
    set("am-story", article.summary || "No full content available");
    set("am-slug", "N/A");
    set("am-meta-title", "N/A");
    set("am-image-prompt", "N/A");
    set("am-confidence", "N/A");
    set("am-claims", "N/A");

    const linkEl = document.getElementById("am-link");
    if (linkEl) {
        linkEl.textContent = article.link || "-";
        linkEl.href = article.link || "#";
    }

    const imgEl = document.getElementById("am-image");
    const imgPh = document.getElementById("am-image-placeholder");
    if (article.image) {
        imgEl.src = article.image;
        imgEl.style.display = "block";
        imgPh.style.display = "none";
        imgEl.onerror = function() {
            this.style.display = "none";
            imgPh.style.display = "block";
        };
    } else {
        imgEl.style.display = "none";
        imgPh.style.display = "block";
    }

    document.getElementById("article-modal").classList.add("open");
}

function openFullArticleModal(item) {
    if (!item) return;

    const set = (id, val) => {
        const el = document.getElementById(id);
        if (el) el.textContent = val || "-";
    };

    set("am-title", item.title);
    set("am-source", item.source);
    set("am-category", item.category);
    set("am-score", item.imp_score || item.raw_score || 0);
    set("am-hook", item.hook);
    set("am-story", item.story);
    set("am-slug", item.slug);
    set("am-meta-title", item.meta_title);
    set("am-image-prompt", item.image_prompt);
    set("am-confidence", `${item.confidence || 0}%`);
    set("am-claims", item.claims_keywords);

    const linkEl = document.getElementById("am-link");
    if (linkEl) {
        linkEl.textContent = item.link || "-";
        linkEl.href = item.link || "#";
    }

    const imgEl = document.getElementById("am-image");
    const imgPh = document.getElementById("am-image-placeholder");
    const imagePath = item.slug ? `${API_BASE}/media/images/${item.slug}.png` : null;

    if (imagePath) {
        imgEl.src = imagePath;
        imgEl.style.display = "block";
        imgPh.style.display = "none";
        imgEl.onerror = function() {
            this.style.display = "none";
            imgPh.style.display = "block";
        };
    } else {
        imgEl.style.display = "none";
        imgPh.style.display = "block";
    }

    document.getElementById("article-modal").classList.add("open");
}