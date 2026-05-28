// ============================================
// PhishGuard Chart Helpers
// Reusable chart creation functions
// ============================================

function createCategoryChart(ctx, categories, counts) {
    return new Chart(ctx, {
        type: 'pie',
        data: {
            labels: categories,
            datasets: [{ data: counts, backgroundColor: ['#ff6384', '#36a2eb', '#ffce56', '#4bc0c0', '#9966ff'] }]
        },
        options: { responsive: true, plugins: { legend: { position: 'bottom', labels: { color: '#fff' } } } }
    });
}

function createDailyChart(ctx, dates, counts) {
    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: dates,
            datasets: [{ label: 'Blocks', data: counts, borderColor: '#ff6384', fill: false }]
        },
        options: { responsive: true, scales: { y: { beginAtZero: true } } }
    });
}

function createTopDomainsChart(ctx, domains, counts) {
    return new Chart(ctx, {
        type: 'bar',
        data: {
            labels: domains.map(d => d.length > 25 ? d.substring(0,22)+'...' : d),
            datasets: [{ label: 'Block Count', data: counts, backgroundColor: '#36a2eb' }]
        },
        options: { responsive: true, maintainAspectRatio: true }
    });
}

window.createCategoryChart = createCategoryChart;
window.createDailyChart = createDailyChart;
window.createTopDomainsChart = createTopDomainsChart;