/**
 * CampusPlacements - Dashboard Charts (Chart.js)
 */

document.addEventListener('DOMContentLoaded', async () => {
    const monthlyCanvas = document.getElementById('chartApplicationsMonthly');
    const deptCanvas = document.getElementById('chartPlacementsDept');
    const companyCanvas = document.getElementById('chartCompanyPlacements');
    const statusCanvas = document.getElementById('chartStatusDist');

    if (!monthlyCanvas || !deptCanvas || !companyCanvas || !statusCanvas) {
        return;
    }

    try {
        const response = await fetch('/api/dashboard-charts');
        const data = await response.json();

        // 1. Applications by Month (Line / Area)
        new Chart(monthlyCanvas, {
            type: 'line',
            data: {
                labels: data.applications_by_month.labels,
                datasets: [{
                    label: 'Applications',
                    data: data.applications_by_month.data,
                    borderColor: '#4f46e5',
                    backgroundColor: 'rgba(79, 70, 229, 0.12)',
                    fill: true,
                    tension: 0.35,
                    pointBackgroundColor: '#4f46e5',
                    pointRadius: 4,
                    pointHoverRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: { stepSize: 5 }
                    }
                }
            }
        });

        // 2. Placements by Department (Bar)
        new Chart(deptCanvas, {
            type: 'bar',
            data: {
                labels: data.department_placements.labels,
                datasets: [
                    {
                        label: 'Placed Students',
                        data: data.department_placements.placed,
                        backgroundColor: '#10b981',
                        borderRadius: 6
                    },
                    {
                        label: 'Total Students',
                        data: data.department_placements.total,
                        backgroundColor: '#e2e8f0',
                        borderRadius: 6
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'top' }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: { stepSize: 5 }
                    }
                }
            }
        });

        // 3. Company-wise Placements (Bar)
        new Chart(companyCanvas, {
            type: 'bar',
            data: {
                labels: data.company_placements.labels,
                datasets: [{
                    label: 'Selected / Placed',
                    data: data.company_placements.data,
                    backgroundColor: '#0ea5e9',
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: { stepSize: 2 }
                    }
                }
            }
        });

        // 4. Application Status Distribution (Doughnut)
        new Chart(statusCanvas, {
            type: 'doughnut',
            data: {
                labels: data.application_status_dist.labels,
                datasets: [{
                    data: data.application_status_dist.data,
                    backgroundColor: [
                        '#64748b', // Applied
                        '#38bdf8', // Shortlisted
                        '#a855f7', // Assessment
                        '#f59e0b', // Interview
                        '#10b981', // Selected
                        '#ef4444', // Rejected
                        '#cbd5e1'  // Withdrawn
                    ],
                    borderWidth: 2,
                    borderColor: '#ffffff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'right' }
                },
                cutout: '65%'
            }
        });

    } catch (err) {
        console.error('Failed to load dashboard chart metrics:', err);
    }
});
