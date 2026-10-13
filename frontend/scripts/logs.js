/*
  AI IMP NEWS OS
  Logs Page Script
*/

document.addEventListener("DOMContentLoaded", function() {

    loadLogs();

    const refreshBtn = document.getElementById("btn-refresh");
    if (refreshBtn) {
        refreshBtn.addEventListener("click", function() {
            loadLogs();
            showToast("Logs Refreshed", "success");
        });
    }

    const clearBtn = document.getElementById("btn-clear");
    if (clearBtn) {
        clearBtn.addEventListener("click", function() {
            document.getElementById("logs-console").innerHTML = `<div class="log-line log-info">[CLEARED] Logs cleared at ${new Date().toLocaleTimeString()}</div>`;
            showToast("Logs Cleared", "warning");
        });
    }

    setInterval(loadLogs, 10000);
});

async function loadLogs() {
    // Future: Fetch from /api/logs endpoint
    // For now, show sample logs
    const console = document.getElementById("logs-console");
    if (!console) return;

    const data = await API.getPipelineStatus();
    if (!data) return;

    const now = new Date().toLocaleTimeString();
    const existingLogs = console.innerHTML;

    const newLog = `<div class="log-line"><span class="log-timestamp">[${now}]</span><span class="log-info">Pipeline status checked</span></div>`;

    if (!existingLogs.includes(newLog)) {
        console.innerHTML += newLog;
        console.scrollTop = console.scrollHeight;
    }
}