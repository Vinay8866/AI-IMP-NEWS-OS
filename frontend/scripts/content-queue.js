document.addEventListener('DOMContentLoaded', () => {
    const tabs = document.querySelectorAll('.tab');
    const tabContents = document.querySelectorAll('.tab-content');
    const publishGrid = document.getElementById('publish-queue-grid');
    const bufferGrid = document.getElementById('buffer-queue-grid');
    const postedGrid = document.getElementById('posted-queue-grid');
    const rewriteGrid = document.getElementById('rewrite-queue-grid');

    let currentEditingId = null;

    // Tab switching
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));
            tab.classList.add('active');
            document.getElementById(`tab-${tab.dataset.queue}`).classList.add('active');
        });
    });

    // Refresh buttons
    document.getElementById('btn-refresh')?.addEventListener('click', loadAll);
    document.getElementById('btn-refresh-buffer')?.addEventListener('click', loadBufferQueue);
    document.getElementById('btn-auto-schedule')?.addEventListener('click', autoScheduleAll);

    // Modal
    const modal = document.getElementById('buffer-edit-modal');
    document.getElementById('modal-close')?.addEventListener('click', closeModal);
    document.getElementById('modal-cancel')?.addEventListener('click', closeModal);
    document.getElementById('modal-save')?.addEventListener('click', saveModal);

    function closeModal() {
        modal.style.display = 'none';
        currentEditingId = null;
    }

    async function saveModal() {
        if (!currentEditingId) return;
        const caption = document.getElementById('modal-caption').value;
        const scheduledAt = document.getElementById('modal-scheduled-at').value;
        const platforms = [];
        if (document.getElementById('plat-fb').checked) platforms.push('facebook');
        if (document.getElementById('plat-ig').checked) platforms.push('instagram');
        if (document.getElementById('plat-li').checked) platforms.push('linkedin');

        try {
            if (caption) {
                await API.updateSocialCaption(currentEditingId, caption, platforms);
            }
            if (scheduledAt) {
                // Convert datetime-local to "YYYY-MM-DD HH:MM:SS"
                const dt = scheduledAt.replace('T', ' ') + ':00';
                if (dt.length === 19) {
                    await API.rescheduleSocialPost(currentEditingId, dt);
                } else {
                    // if includes seconds already
                    await API.rescheduleSocialPost(currentEditingId, scheduledAt.replace('T', ' ') );
                }
            }
            showToast('✅ Buffer post updated!', 'success');
            closeModal();
            loadBufferQueue();
        } catch (e) {
            showToast('❌ Failed to update: ' + e.message, 'error');
        }
    }

    async function loadAll() {
        await Promise.all([loadPublishQueue(), loadBufferQueue(), loadPostedQueue(), loadStats()]);
    }

    async function loadStats() {
        const stats = await API.getStats();
        if (!stats) return;

        document.getElementById('cq-publish').textContent = stats.latest_run?.publish_count || 0;
        document.getElementById('cq-rewrite').textContent = stats.latest_run?.rewrite_count || 0;
        document.getElementById('tab-count-publish').textContent = stats.latest_run?.publish_count || 0;
        document.getElementById('tab-count-rewrite').textContent = stats.latest_run?.rewrite_count || 0;

        const social = stats.social || {};
        document.getElementById('buffer-scheduled').textContent = (social.scheduled || 0) + (social.queued || 0);
        document.getElementById('buffer-posted').textContent = social.posted || 0;
        document.getElementById('tab-count-buffer').textContent = (social.scheduled || 0) + (social.queued || 0);
        document.getElementById('tab-count-posted').textContent = social.posted || 0;
    }

    async function loadPublishQueue() {
        const data = await API.getQueue();
        if (!data) {
            publishGrid.innerHTML = `<div class="empty-state"><div class="empty-state-text">Failed to load</div></div>`;
            return;
        }

        const publish = data.publish || data.publish_queue || [];
        if (publish.length === 0) {
            publishGrid.innerHTML = `<div class="empty-state"><div class="empty-state-icon">📭</div><div class="empty-state-text">No articles - Run pipeline first</div></div>`;
            return;
        }

        publishGrid.innerHTML = publish.map(article => `
            <div class="publish-card">
                <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
                    <span class="badge badge-success">Q: ${article.quality_score || 0}/100</span>
                    <span style="font-size:11px; color: var(--text-secondary);">${article.category || 'General'}</span>
                </div>
                <div class="buffer-card-title">${escapeHtml(article.title)}</div>
                <div style="font-size:12px; color: var(--text-secondary); margin-bottom:8px; display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; overflow:hidden;">
                    ${escapeHtml(article.hook || '')}
                </div>
                <div class="publish-card-actions">
                    <button class="buffer-btn buffer-btn-primary" onclick="window.scheduleToBuffer(${article.id})">📱 Add to Buffer</button>
                    <button class="buffer-btn" onclick="window.viewArticle(${article.id})">👁 View</button>
                </div>
            </div>
        `).join('');
    }

    async function loadBufferQueue() {
        const data = await API.getSocialQueue('scheduled');
        const queuedData = await API.getSocialQueue('queued');
        
        let allScheduled = [];
        if (data?.queue) allScheduled = allScheduled.concat(data.queue);
        if (queuedData?.queue) allScheduled = allScheduled.concat(queuedData.queue);

        // Also get scheduled only via combined call
        if (allScheduled.length === 0) {
            const all = await API.getSocialQueue();
            allScheduled = (all?.queue || []).filter(p => p.status === 'scheduled' || p.status === 'queued');
        }

        if (allScheduled.length === 0) {
            bufferGrid.innerHTML = `<div class="empty-state"><div class="empty-state-icon">📱</div><div class="empty-state-text">Buffer queue empty - Click "Auto-Schedule All to Social"</div></div>`;
            return;
        }

        bufferGrid.innerHTML = allScheduled.map(post => {
            const platforms = post.platforms_list || [];
            const timeStr = formatDateTime(post.scheduled_at);
            return `
            <div class="buffer-card scheduled">
                <div class="buffer-card-header">
                    <div class="buffer-platforms">
                        ${platforms.map(p => `<span class="platform-badge ${p}">${p === 'facebook' ? '📘 FB' : p === 'instagram' ? '📸 IG' : p}</span>`).join('')}
                    </div>
                    <div class="buffer-time">📅 ${timeStr}</div>
                </div>
                <div class="buffer-card-title">${escapeHtml(post.title)}</div>
                <div class="buffer-card-caption">${escapeHtml(post.caption)}</div>
                ${post.image_path ? `<div style="font-size:10px; color: #888; margin-bottom:8px;">🖼 ${post.image_path.split('/').pop()}</div>` : ''}
                <div class="buffer-card-footer">
                    <button class="buffer-btn buffer-btn-success" onclick="window.postNow(${post.id})">🚀 Post Now</button>
                    <button class="buffer-btn" onclick="window.editBufferPost(${post.id})">✏ Edit</button>
                    <button class="buffer-btn buffer-btn-danger" onclick="window.deleteBufferPost(${post.id})">🗑 Delete</button>
                </div>
            </div>
        `}).join('');
    }

    async function loadPostedQueue() {
        const data = await API.getSocialQueue('posted');
        const posts = data?.queue || [];

        if (posts.length === 0) {
            postedGrid.innerHTML = `<div class="empty-state"><div class="empty-state-icon">✅</div><div class="empty-state-text">No posted items yet</div></div>`;
            return;
        }

        postedGrid.innerHTML = posts.map(post => {
            const platforms = post.platforms_list || [];
            return `
            <div class="buffer-card posted">
                <div class="buffer-card-header">
                    <div class="buffer-platforms">
                        ${platforms.map(p => `<span class="platform-badge ${p}">${p === 'facebook' ? '📘 FB' : '📸 IG'}</span>`).join('')}
                        <span class="badge badge-success">Posted</span>
                    </div>
                    <div class="buffer-time">✅ ${formatDateTime(post.posted_at)}</div>
                </div>
                <div class="buffer-card-title">${escapeHtml(post.title)}</div>
                <div class="buffer-card-caption">${escapeHtml(post.caption)}</div>
                <div style="font-size:10px; color: #4CAF50; margin-top:8px;">
                    ${post.fb_post_id ? `FB ID: ${post.fb_post_id.substring(0,20)}...` : ''} 
                    ${post.ig_post_id ? `IG ID: ${post.ig_post_id.substring(0,20)}...` : ''}
                </div>
            </div>
        `}).join('');
    }

    // Global functions for inline onclick
    window.scheduleToBuffer = async (articleId) => {
        try {
            const res = await API.scheduleArticle(articleId);
            showToast(`✅ Added to Buffer Queue! ID ${res.post_id}`, 'success');
            loadBufferQueue();
            loadStats();
        } catch (e) {
            showToast('❌ ' + e.message, 'error');
        }
    };

    window.postNow = async (postId) => {
        if (!confirm('Post this now to Facebook/Instagram?')) return;
        try {
            showToast('🚀 Posting...', 'info');
            const res = await API.postNow(postId);
            showToast(`✅ Posted! Mode: ${res.result?.mode || 'real'}`, 'success');
            loadAll();
        } catch (e) {
            showToast('❌ Failed: ' + e.message, 'error');
        }
    };

    window.deleteBufferPost = async (postId) => {
        if (!confirm('Delete this scheduled post?')) return;
        const res = await API.deleteSocialPost(postId);
        if (res) {
            showToast('🗑 Deleted', 'success');
            loadBufferQueue();
            loadStats();
        }
    };

    window.editBufferPost = async (postId) => {
        // Fetch post details
        const all = await API.getSocialQueue();
        const post = (all?.queue || []).find(p => p.id === postId);
        if (!post) {
            showToast('Post not found', 'error');
            return;
        }
        currentEditingId = postId;
        document.getElementById('modal-caption').value = post.caption || '';
        
        // Set scheduled_at to datetime-local format
        if (post.scheduled_at) {
            try {
                // "2025-01-20 13:00:00" -> "2025-01-20T13:00"
                const dtLocal = post.scheduled_at.replace(' ', 'T').substring(0,16);
                document.getElementById('modal-scheduled-at').value = dtLocal;
            } catch {}
        }

        // Platforms
        const plats = post.platforms_list || [];
        document.getElementById('plat-fb').checked = plats.includes('facebook');
        document.getElementById('plat-ig').checked = plats.includes('instagram');
        document.getElementById('plat-li').checked = plats.includes('linkedin');

        modal.style.display = 'flex';
    };

    window.viewArticle = (id) => {
        showToast(`Article ID ${id} - check docs/content folder`, 'info');
    };

    async function autoScheduleAll() {
        if (!confirm('Auto-schedule all Publish Queue articles to Buffer Queue?')) return;
        showToast('🚀 Auto-scheduling...', 'info');
        const res = await API.autoScheduleAll();
        if (res) {
            showToast(`✅ ${res.message}`, 'success');
            loadAll();
        } else {
            showToast('❌ Failed to auto-schedule', 'error');
        }
    }

    function formatDateTime(str) {
        if (!str) return 'Not scheduled';
        try {
            const d = new Date(str);
            return d.toLocaleString('en-IN', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit', hour12: true });
        } catch {
            return str;
        }
    }

    function escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    function showToast(msg, type = 'info') {
        const container = document.getElementById('toast-container');
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = msg;
        container.appendChild(toast);
        setTimeout(() => toast.remove(), 4000);
    }

    // Initial load
    loadAll();
    // Auto refresh every 30 sec
    setInterval(loadBufferQueue, 30000);
});

