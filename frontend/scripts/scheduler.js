/*
  AI IMP NEWS OS
  Scheduler Page Script
  Version: 2.0
*/

document.addEventListener("DOMContentLoaded", function() {

    // Run Now button
    const runNowBtn = document.getElementById("btn-run-now");
    if (runNowBtn) {
        runNowBtn.addEventListener("click", async function() {
            showToast("Starting pipeline...", "info");
            runNowBtn.disabled = true;
            runNowBtn.textContent = "⏳ Running...";

            const result = await API.runPipeline();

            if (result) {
                showToast("Pipeline completed!", "success");
            } else {
                showToast("Pipeline failed. Check backend.", "error");
            }

            runNowBtn.disabled = false;
            runNowBtn.textContent = "▶ Run Pipeline Now";
        });
    }

    // Save Schedule button (placeholder)
    const saveBtn = document.getElementById("btn-save-schedule");
    if (saveBtn) {
        saveBtn.addEventListener("click", function() {
            showToast("Schedule saved successfully!", "success");
        });
    }

    // Pause button (placeholder)
    const pauseBtn = document.getElementById("btn-pause");
    if (pauseBtn) {
        pauseBtn.addEventListener("click", function() {
            showToast("Scheduler paused", "warning");
        });
    }
});















document.addEventListener("DOMContentLoaded", function() {
    const timelineEl = document.getElementById('schedule-timeline');
    const bufferTodayList = document.getElementById('today-buffer-posts');
    const calendarEl = document.getElementById('buffer-calendar');
    const bufferStatusEl = document.getElementById('buffer-status');

    const runNowBtn = document.getElementById("btn-run-now");
    if (runNowBtn) {
        runNowBtn.addEventListener("click", async function() {
            if (typeof showToast !== 'undefined') showToast("Starting pipeline...", "info");
            runNowBtn.disabled = true;
            const oldText = runNowBtn.textContent;
            runNowBtn.textContent = "⏳ Running...";
            try {
                const result = await API.runPipeline();
                if (result) { if (typeof showToast !== 'undefined') showToast("✅ Pipeline completed!", "success"); }
                else { if (typeof showToast !== 'undefined') showToast("❌ Pipeline failed", "error"); }
            } catch (e) { if (typeof showToast !== 'undefined') showToast("❌ Error: "+e.message, "error"); }
            runNowBtn.disabled = false;
            runNowBtn.textContent = oldText;
            loadBufferCalendar(); loadBufferToday(); loadBufferStatus();
        });
    }

    const saveBtn = document.getElementById("btn-save-schedule");
    if (saveBtn) {
        saveBtn.addEventListener("click", function() {
            const pipelineSlots = [document.getElementById('slot-1')?.value, document.getElementById('slot-2')?.value, document.getElementById('slot-3')?.value];
            const bufferSlots = [document.getElementById('buffer-slot-1')?.value || '08:00', document.getElementById('buffer-slot-2')?.value || '13:00', document.getElementById('buffer-slot-3')?.value || '19:00'];
            localStorage.setItem('pipeline_schedule', JSON.stringify(pipelineSlots));
            localStorage.setItem('buffer_schedule', JSON.stringify(bufferSlots));
            if (typeof showToast !== 'undefined') showToast("✅ Schedule saved!", "success");
            loadPipelineTimeline();
        });
    }

    const pauseBtn = document.getElementById("btn-pause");
    if (pauseBtn) { pauseBtn.addEventListener("click", function() { if (typeof showToast !== 'undefined') showToast("⏸ Paused", "warning"); }); }

    document.getElementById('btn-run-buffer-check')?.addEventListener('click', async () => {
        if (typeof showToast !== 'undefined') showToast('📱 Checking Buffer...', 'info');
        const data = await API.getSocialQueue('scheduled');
        loadBufferCalendar(); loadBufferToday(); loadBufferStatus();
    });
    document.getElementById('btn-view-queue')?.addEventListener('click', () => { window.location.href = 'content-queue.html'; });

    async function loadPipelineTimeline() {
        if (!timelineEl) return;
        const now = new Date();
        const slots = [{ time: document.getElementById('slot-1')?.value || '08:00', label: 'Morning' }, { time: document.getElementById('slot-2')?.value || '16:00', label: 'Afternoon' }, { time: document.getElementById('slot-3')?.value || '00:00', label: 'Night' }];
        timelineEl.innerHTML = slots.map(s => {
            const [h,m]=s.time.split(':').map(Number); const slotTime=new Date(); slotTime.setHours(h,m,0,0);
            let status='upcoming'; let statusText='Upcoming'; if (slotTime<now){status='completed'; statusText='Completed Today';}
            return `<div class="timeline-item ${status}"><span class="timeline-dot"></span><div class="timeline-info"><span class="timeline-time">${s.time} - ${s.label}</span><span class="timeline-status">${statusText}</span></div></div>`;
        }).join('');
    }

    async function loadBufferToday() {
        if (!bufferTodayList) return;
        try {
            const data = await API.getSocialCalendar(1);
            const calendar = data?.calendar || [];
            const todayStr = new Date().toISOString().split('T')[0];
            const todayPosts = calendar.filter(p => p.scheduled_at && p.scheduled_at.startsWith(todayStr));
            if (todayPosts.length===0){ bufferTodayList.innerHTML=`<div style="font-size:11px; color:#888;">No posts today</div>`; return; }
            bufferTodayList.innerHTML = todayPosts.map(p=>`<div style="font-size:11px; padding:6px; background:white; border-radius:8px; margin-bottom:6px; border-left:3px solid #1877F2;">${p.title.substring(0,35)}... - ${p.status}</div>`).join('');
        } catch(e){ bufferTodayList.innerHTML=`Failed`; }
    }

    async function loadBufferCalendar() {
        if (!calendarEl) return;
        try {
            const data = await API.getSocialCalendar(7);
            const posts = data?.calendar || [];
            if (posts.length===0){ calendarEl.innerHTML=`<div style="grid-column:1/-1;"><div class="empty-state"><div class="empty-state-text">No posts for 7 days</div></div></div>`; return; }
            const grouped={}; posts.forEach(p=>{ const k=p.scheduled_at?p.scheduled_at.split(' ')[0]:'Unscheduled'; if(!grouped[k]) grouped[k]=[]; grouped[k].push(p); });
            const days=[]; for(let i=0;i<7;i++){ const d=new Date(); d.setDate(d.getDate()+i); const key=d.toISOString().split('T')[0]; days.push({date:d,key,posts:grouped[key]||[]}); }
            calendarEl.innerHTML = days.map(day=>`<div class="calendar-day"><div class="calendar-day-header"><span>${day.date.toLocaleDateString('en-US',{weekday:'short'})}</span><span>${day.date.getDate()}</span></div>${day.posts.map(p=>`<div class="calendar-post">${p.title.substring(0,40)}...</div>`).join('')}</div>`).join('');
        } catch(e){ calendarEl.innerHTML=`Failed: ${e.message}`; }
    }

    async function loadBufferStatus() {
        if (!bufferStatusEl) return;
        try { const stats=await API.getSocialStats(); bufferStatusEl.innerHTML=`Total: ${stats.total||0} | Sched: ${stats.scheduled||0} | Posted: ${stats.posted||0}`; } catch(e){ bufferStatusEl.innerHTML=`Error`; }
    }

    loadPipelineTimeline(); loadBufferCalendar(); loadBufferToday(); loadBufferStatus();
    setInterval(()=>{ loadBufferCalendar(); loadBufferToday(); loadBufferStatus(); },30000);
});
