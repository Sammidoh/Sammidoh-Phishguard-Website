// ============================================
// PhishGuard Dashboard Scripts
// Charts, statistics, recent logs, auto-refresh
// ============================================

let refreshInterval = null;

document.addEventListener('DOMContentLoaded', () => {
    // Load initial data
    loadStats();
    loadRecentLogs();
    loadCharts();
    
    // Auto-refresh every 30 seconds on dashboard page
    if (window.location.pathname === '/dashboard/' || window.location.pathname === '/dashboard') {
        startAutoRefresh(30000);
    }
});

function startAutoRefresh(ms) {
    if (refreshInterval) clearInterval(refreshInterval);
    refreshInterval = setInterval(() => {
        loadStats();
        loadRecentLogs();
        loadCharts();
    }, ms);
}

function stopAutoRefresh() {
    if (refreshInterval) clearInterval(refreshInterval);
}

async function loadStats() {
    try {
        const stats = await apiGet('/logs/stats');
        document.getElementById('totalBlocks').innerText = stats.total_blocks || 0;
        document.getElementById('totalBypass').innerText = stats.total_bypass || 0;
        
        // Blacklist count from blacklist endpoint (if on dashboard)
        const blacklistData = await apiGet('/blacklist/data');
        document.getElementById('blacklistCount').innerText = blacklistData.length || 0;
    } catch (err) {
        console.error('Failed to load stats:', err);
    }
}

async function loadRecentLogs() {
    try {
        const data = await apiGet('/logs/data?page=1');
        const logs = data.logs || [];
        const tbody = document.getElementById('recentLogs');
        if (!tbody) return;
        
        tbody.innerHTML = '';
        logs.slice(0, 10).forEach(log => {
            tbody.innerHTML += `
                <tr>
                    <td style="word-break:break-all;">${escapeHtml(log.url)}</td>
                    <td><span class="badge bg-danger">${escapeHtml(log.threat_category || '-')}</span></td>
                    <td>${new Date(log.timestamp).toLocaleString()}</td>
                </tr>
            `;
        });
        
        if (logs.length === 0) {
            tbody.innerHTML = '<tr><td colspan="3" class="text-center">No blocked attempts yet</td></tr>';
        }
    } catch (err) {
        console.error('Failed to load recent logs:', err);
    }
}

async function loadCharts() {
    // Fetch stats for daily activity
    const stats = await apiGet('/logs/stats');
    const daily = stats.daily || [];
    
    // Threat categories chart (pie) – need categories endpoint; fallback mock
    let categories = [];
    let categoryCounts = [];
    try {
        const catData = await apiGet('/logs/categories');
        categories = catData.map(c => c.name);
        categoryCounts = catData.map(c => c.count);
    } catch {
        // Fallback: extract from logs
        const logsData = await apiGet('/logs/data?per_page=500');
        const logs = logsData.logs || [];
        const catMap = new Map();
        logs.forEach(log => {
            const cat = log.threat_category || 'unknown';
            catMap.set(cat, (catMap.get(cat) || 0) + 1);
        });
        categories = Array.from(catMap.keys());
        categoryCounts = Array.from(catMap.values());
    }
    
    const categoryChartCtx = document.getElementById('categoryChart');
    if (categoryChartCtx) {
        new Chart(categoryChartCtx, {
            type: 'pie',
            data: {
                labels: categories,
                datasets: [{
                    data: categoryCounts,
                    backgroundColor: ['#ff6384', '#36a2eb', '#ffce56', '#4bc0c0', '#9966ff', '#ff9f40']
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { position: 'bottom', labels: { color: '#fff' } }
                }
            }
        });
    }
    
    // Daily activity line chart
    const dailyChartCtx = document.getElementById('dailyChart');
    if (dailyChartCtx) {
        new Chart(dailyChartCtx, {
            type: 'line',
            data: {
                labels: daily.map(d => d.date),
                datasets: [{
                    label: 'Blocked Attempts',
                    data: daily.map(d => d.count),
                    borderColor: '#ff6384',
                    backgroundColor: 'rgba(255,99,132,0.1)',
                    fill: true,
                    tension: 0.3
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: { beginAtZero: true, ticks: { color: '#fff' }, grid: { color: '#2c3e50' } },
                    x: { ticks: { color: '#fff' } }
                }
            }
        });
    }
}

// Export for global use
window.loadStats = loadStats;
window.loadRecentLogs = loadRecentLogs;
window.loadCharts = loadCharts;