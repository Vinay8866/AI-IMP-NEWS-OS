/*
  AI IMP NEWS OS
  Central API Handler
  Version: 2.0
*/

const API_BASE = "http://127.0.0.1:8000";

const API = {

    // ===== DASHBOARD =====
    async getStats() {
        try {
            const res = await fetch(`${API_BASE}/api/stats`);
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            return await res.json();
        } catch (err) {
            console.error("API.getStats failed:", err);
            return null;
        }
    },

    async getQueue() {
        try {
            const res = await fetch(`${API_BASE}/api/queue`);
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            return await res.json();
        } catch (err) {
            console.error("API.getQueue failed:", err);
            return null;
        }
    },

    async getPipelineStatus() {
        try {
            const res = await fetch(`${API_BASE}/api/pipeline`);
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            return await res.json();
        } catch (err) {
            console.error("API.getPipelineStatus failed:", err);
            return null;
        }
    },

    // ===== PIPELINE JOURNEY =====
    async getRawNews() {
        try {
            const res = await fetch(`${API_BASE}/api/journey/raw-news`);
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            return await res.json();
        } catch (err) {
            console.error("API.getRawNews failed:", err);
            return null;
        }
    },

    async getJourneyDates() {
        try {
            const res = await fetch(`${API_BASE}/api/journey/dates`);
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            return await res.json();
        } catch (err) {
            console.error("API.getJourneyDates failed:", err);
            return null;
        }
    },

    async getJourney(runDate) {
        try {
            const url = (runDate && runDate !== "latest")
                ? `${API_BASE}/api/journey/${runDate}`
                : `${API_BASE}/api/journey/latest/full`;
            const res = await fetch(url);
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            return await res.json();
        } catch (err) {
            console.error("API.getJourney failed:", err);
            return null;
        }
    },

    // ===== ANALYTICS =====
    async getAnalytics(days) {
        try {
            const res = await fetch(`${API_BASE}/api/analytics/summary?days=${days || 7}`);
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            return await res.json();
        } catch (err) {
            console.error("API.getAnalytics failed:", err);
            return null;
        }
    },

    // ===== RUN PIPELINE =====
    async runPipeline() {
        try {
            const res = await fetch(`${API_BASE}/api/run-pipeline`, { method: "POST" });
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            return await res.json();
        } catch (err) {
            console.error("API.runPipeline failed:", err);
            return null;
        }
    }
};

























/*
  AI IMP NEWS OS
  Central API Handler
  Version: 3.0 Buffer Edition
*/

const API_BASE = "http://127.0.0.1:8000";

const API = {

    // ===== DASHBOARD =====
    async getStats() {
        try {
            const res = await fetch(`${API_BASE}/api/stats`);
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            return await res.json();
        } catch (err) {
            console.error("API.getStats failed:", err);
            return null;
        }
    },

    async getQueue() {
        try {
            const res = await fetch(`${API_BASE}/api/queue`);
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            return await res.json();
        } catch (err) {
            console.error("API.getQueue failed:", err);
            return null;
        }
    },

    async getPipelineStatus() {
        try {
            const res = await fetch(`${API_BASE}/api/pipeline`);
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            return await res.json();
        } catch (err) {
            console.error("API.getPipelineStatus failed:", err);
            return null;
        }
    },

    // ===== PIPELINE JOURNEY =====
    async getRawNews() {
        try {
            const res = await fetch(`${API_BASE}/api/journey/raw-news`);
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            return await res.json();
        } catch (err) {
            console.error("API.getRawNews failed:", err);
            return null;
        }
    },

    async getJourneyDates() {
        try {
            const res = await fetch(`${API_BASE}/api/journey/dates`);
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            return await res.json();
        } catch (err) {
            console.error("API.getJourneyDates failed:", err);
            return null;
        }
    },

    async getJourney(runDate) {
        try {
            const url = (runDate && runDate !== "latest")
                ? `${API_BASE}/api/journey/${runDate}`
                : `${API_BASE}/api/journey/latest/full`;
            const res = await fetch(url);
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            return await res.json();
        } catch (err) {
            console.error("API.getJourney failed:", err);
            return null;
        }
    },

    // ===== ANALYTICS =====
    async getAnalytics(days) {
        try {
            const res = await fetch(`${API_BASE}/api/analytics/summary?days=${days || 7}`);
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            return await res.json();
        } catch (err) {
            console.error("API.getAnalytics failed:", err);
            return null;
        }
    },

    // ===== RUN PIPELINE =====
    async runPipeline() {
        try {
            const res = await fetch(`${API_BASE}/api/run-pipeline`, { method: "POST" });
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            return await res.json();
        } catch (err) {
            console.error("API.runPipeline failed:", err);
            return null;
        }
    },

    // ===== BUFFER CLONE - SOCIAL QUEUE =====
    async getSocialQueue(status = null) {
        try {
            const url = status
                ? `${API_BASE}/api/social/queue?status=${status}`
                : `${API_BASE}/api/social/queue`;
            const res = await fetch(url);
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            return await res.json();
        } catch (err) {
            console.error("API.getSocialQueue failed:", err);
            return null;
        }
    },

    async getSocialCalendar(days = 7) {
        try {
            const res = await fetch(`${API_BASE}/api/social/calendar?days=${days}`);
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            return await res.json();
        } catch (err) {
            console.error("API.getSocialCalendar failed:", err);
            return null;
        }
    },

    async getSocialStats() {
        try {
            const res = await fetch(`${API_BASE}/api/social/stats`);
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            return await res.json();
        } catch (err) {
            console.error("API.getSocialStats failed:", err);
            return null;
        }
    },

    async scheduleArticle(articleId, caption = null, platforms = null, scheduledAt = null) {
        try {
            const body = { article_id: articleId };
            if (caption) body.caption = caption;
            if (platforms) body.platforms = platforms;
            if (scheduledAt) body.scheduled_at = scheduledAt;

            const res = await fetch(`${API_BASE}/api/social/schedule`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(body)
            });
            if (!res.ok) {
                const err = await res.json();
                throw new Error(err.detail || `HTTP ${res.status}`);
            }
            return await res.json();
        } catch (err) {
            console.error("API.scheduleArticle failed:", err);
            throw err;
        }
    },

    async autoScheduleAll() {
        try {
            const res = await fetch(`${API_BASE}/api/social/auto-schedule-all`, { method: "POST" });
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            return await res.json();
        } catch (err) {
            console.error("API.autoScheduleAll failed:", err);
            return null;
        }
    },

    async updateSocialCaption(postId, caption, platforms = null) {
        try {
            const body = { caption };
            if (platforms) body.platforms = platforms;
            const res = await fetch(`${API_BASE}/api/social/${postId}/caption`, {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(body)
            });
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            return await res.json();
        } catch (err) {
            console.error("API.updateSocialCaption failed:", err);
            return null;
        }
    },

    async rescheduleSocialPost(postId, scheduledAt) {
        try {
            const res = await fetch(`${API_BASE}/api/social/${postId}/reschedule`, {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ scheduled_at: scheduledAt })
            });
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            return await res.json();
        } catch (err) {
            console.error("API.rescheduleSocialPost failed:", err);
            return null;
        }
    },

    async postNow(postId) {
        try {
            const res = await fetch(`${API_BASE}/api/social/${postId}/post-now`, { method: "POST" });
            if (!res.ok) {
                const err = await res.json();
                throw new Error(err.detail || `HTTP ${res.status}`);
            }
            return await res.json();
        } catch (err) {
            console.error("API.postNow failed:", err);
            throw err;
        }
    },

    async deleteSocialPost(postId) {
        try {
            const res = await fetch(`${API_BASE}/api/social/${postId}`, { method: "DELETE" });
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            return await res.json();
        } catch (err) {
            console.error("API.deleteSocialPost failed:", err);
            return null;
        }
    }
};
