/**
 * CampusPlacements - Big Data Analytics Lab Visualization Engine
 * Dynamic Chart.js management with real-time asynchronous multi-factor filtering.
 */

let charts = {};

document.addEventListener('DOMContentLoaded', () => {
    // Initial fetch and render
    loadAnalyticsData();

    // Event listeners for filter controls
    const filterForm = document.getElementById('analyticsFilterForm');
    if (filterForm) {
        filterForm.addEventListener('change', (e) => {
            loadAnalyticsData();
        });

        const resetBtn = document.getElementById('resetFiltersBtn');
        if (resetBtn) {
            resetBtn.addEventListener('click', () => {
                filterForm.reset();
                loadAnalyticsData();
            });
        }
    }
});

async function loadAnalyticsData() {
    const dept = document.getElementById('filterDept')?.value || '';
    const year = document.getElementById('filterYear')?.value || '';
    const company = document.getElementById('filterCompany')?.value || '';
    const job = document.getElementById('filterJob')?.value || '';

    const params = new URLSearchParams();
    if (dept) params.append('department', dept);
    if (year) params.append('graduation_year', year);
    if (company) params.append('company_id', company);
    if (job) params.append('job_id', job);

    try {
        const res = await fetch(`/analytics/api/data?${params.toString()}`);
        const data = await res.json();

        // Update KPI counter badges
        const rateEl = document.getElementById('kpiPlacementRate');
        if (rateEl) rateEl.innerText = `${data.placement_rate}%`;

        const totalEl = document.getElementById('kpiTotalStudents');
        if (totalEl) totalEl.innerText = data.total_students;

        const placedEl = document.getElementById('kpiPlacedStudents');
        if (placedEl) placedEl.innerText = data.placed_students;

        const unplacedEl = document.getElementById('kpiUnplacedStudents');
        if (unplacedEl) unplacedEl.innerText = data.unplaced_students;

        // Render all 10 Charts
        renderPlacedVsUnplaced(data.placed_vs_unplaced);
        renderDeptPlacements(data.department_placements);
        renderCompanyPlacements(data.company_placements);
        renderAppsByCompany(data.applications_by_company);
        renderAppsByMonth(data.applications_by_month);
        renderStatusDist(data.application_status_dist);
        renderAvgCtcDept(data.avg_ctc_by_dept);
        renderAvgCtcCompany(data.avg_ctc_by_company);
        renderOnCampusVsOff(data.on_campus_vs_off_campus);

    } catch (err) {
        console.error('Error fetching analytics metrics:', err);
    }
}

function updateOrCreateChart(canvasId, type, config) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;

    if (charts[canvasId]) {
        charts[canvasId].destroy();
    }
    charts[canvasId] = new Chart(canvas, {
        type: type,
        data: config.data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            ...config.options
        }
    });
}

// 1. Placed vs Not Placed (Doughnut)
function renderPlacedVsUnplaced(dataset) {
    updateOrCreateChart('chartPlacedVsUnplaced', 'doughnut', {
        data: {
            labels: dataset.labels,
            datasets: [{
                data: dataset.data,
                backgroundColor: ['#10b981', '#f59e0b', '#ef4444'],
                borderWidth: 2,
                borderColor: '#ffffff'
            }]
        },
        options: {
            cutout: '65%',
            plugins: { legend: { position: 'bottom' } }
        }
    });
}

// 2. Department-wise Placements
function renderDeptPlacements(dataset) {
    updateOrCreateChart('chartDeptPlacements', 'bar', {
        data: {
            labels: dataset.labels,
            datasets: [
                {
                    label: 'Placed Students',
                    data: dataset.placed,
                    backgroundColor: '#4f46e5',
                    borderRadius: 6
                },
                {
                    label: 'Total Students',
                    data: dataset.total,
                    backgroundColor: '#e2e8f0',
                    borderRadius: 6
                }
            ]
        },
        options: {
            scales: { y: { beginAtZero: true } },
            plugins: { legend: { position: 'top' } }
        }
    });
}

// 3. Company-wise Placements
function renderCompanyPlacements(dataset) {
    updateOrCreateChart('chartCompanyPlacementsFull', 'bar', {
        data: {
            labels: dataset.labels,
            datasets: [{
                label: 'Placements Count',
                data: dataset.data,
                backgroundColor: '#0ea5e9',
                borderRadius: 6
            }]
        },
        options: {
            scales: { y: { beginAtZero: true } },
            plugins: { legend: { display: false } }
        }
    });
}

// 4. Applications by Company
function renderAppsByCompany(dataset) {
    updateOrCreateChart('chartAppsByCompany', 'bar', {
        data: {
            labels: dataset.labels,
            datasets: [{
                label: 'Applications',
                data: dataset.data,
                backgroundColor: '#6366f1',
                borderRadius: 6
            }]
        },
        options: {
            indexAxis: 'y',
            scales: { x: { beginAtZero: true } },
            plugins: { legend: { display: false } }
        }
    });
}

// 5. Applications by Month
function renderAppsByMonth(dataset) {
    updateOrCreateChart('chartAppsByMonthFull', 'line', {
        data: {
            labels: dataset.labels,
            datasets: [{
                label: 'Applications Trend',
                data: dataset.data,
                borderColor: '#4f46e5',
                backgroundColor: 'rgba(79, 70, 229, 0.15)',
                fill: true,
                tension: 0.35,
                pointBackgroundColor: '#4f46e5',
                pointRadius: 5
            }]
        },
        options: {
            scales: { y: { beginAtZero: true } },
            plugins: { legend: { display: false } }
        }
    });
}

// 6. Application Status Distribution
function renderStatusDist(dataset) {
    updateOrCreateChart('chartStatusDistFull', 'doughnut', {
        data: {
            labels: dataset.labels,
            datasets: [{
                data: dataset.data,
                backgroundColor: [
                    '#64748b', '#38bdf8', '#c084fc', 
                    '#f59e0b', '#10b981', '#ef4444', '#cbd5e1'
                ],
                borderWidth: 2,
                borderColor: '#ffffff'
            }]
        },
        options: {
            cutout: '60%',
            plugins: { legend: { position: 'right' } }
        }
    });
}

// 7. Average CTC by Department
function renderAvgCtcDept(dataset) {
    updateOrCreateChart('chartAvgCtcDept', 'bar', {
        data: {
            labels: dataset.labels,
            datasets: [{
                label: 'Average CTC (LPA)',
                data: dataset.data,
                backgroundColor: '#10b981',
                borderRadius: 6
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { callback: (val) => `₹${val} LPA` }
                }
            },
            plugins: {
                tooltip: {
                    callbacks: { label: (ctx) => `Avg CTC: ₹${ctx.parsed.y} LPA` }
                }
            }
        }
    });
}

// 8. Average CTC by Company
function renderAvgCtcCompany(dataset) {
    updateOrCreateChart('chartAvgCtcCompany', 'bar', {
        data: {
            labels: dataset.labels,
            datasets: [{
                label: 'Avg Package (LPA)',
                data: dataset.data,
                backgroundColor: '#8b5cf6',
                borderRadius: 6
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { callback: (val) => `₹${val} LPA` }
                }
            },
            plugins: {
                tooltip: {
                    callbacks: { label: (ctx) => `Avg CTC: ₹${ctx.parsed.y} LPA` }
                }
            }
        }
    });
}

// 10. On-Campus vs Off-Campus
function renderOnCampusVsOff(dataset) {
    updateOrCreateChart('chartOnCampusVsOff', 'pie', {
        data: {
            labels: dataset.labels,
            datasets: [{
                data: dataset.data,
                backgroundColor: ['#4f46e5', '#f59e0b'],
                borderWidth: 2,
                borderColor: '#ffffff'
            }]
        },
        options: {
            plugins: { legend: { position: 'bottom' } }
        }
    });
}
