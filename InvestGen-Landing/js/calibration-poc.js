// Quantitative Model Calibration & Real PSX POC Workbench Script
document.addEventListener('DOMContentLoaded', async () => {
    let pocData = window.POC_DATA || null;
    let activeCaseId = 'test_case_1';
    let activeModel = 'HMM'; // 'HMM' | 'GMM' | 'Rule-Based'

    if (!pocData) {
        try {
            const res = await fetch('poc_results.json');
            if (res.ok) {
                pocData = await res.json();
            }
        } catch (e) {
            console.warn('Could not load poc_results.json via fetch.', e);
        }
    }

    if (!pocData || !pocData.test_cases) {
        console.error('POC Results data not found.');
        return;
    }

    // Initialize UI Elements
    const tabButtons = document.querySelectorAll('.poc-case-tab');
    const modelButtons = document.querySelectorAll('.poc-model-btn');
    const chartCanvas = document.getElementById('poc-chart-canvas');
    const tooltipEl = document.getElementById('poc-chart-tooltip');

    function renderActiveTestCase() {
        const caseData = pocData.test_cases[activeCaseId];
        if (!caseData) return;

        // 1. Update Metadata Header
        const titleEl = document.getElementById('poc-case-title');
        if (titleEl) {
            titleEl.innerHTML = `<i class="fas fa-microscope" style="color: var(--accent-color);"></i> TEST CASE ${activeCaseId.replace('test_case_', '')}: ${caseData.name.toUpperCase()}`;
        }
        
        const badgeEl = document.getElementById('poc-ticker-badge');
        if (badgeEl) badgeEl.textContent = caseData.ticker;

        const compEl = document.getElementById('poc-company-name');
        if (compEl) compEl.textContent = caseData.company;

        const datesEl = document.getElementById('poc-dates-range');
        if (datesEl) datesEl.textContent = `${caseData.start_date} to ${caseData.end_date}`;

        const obsEl = document.getElementById('poc-obs-count');
        if (obsEl) obsEl.textContent = `${caseData.observations} Daily Bars`;

        const ratEl = document.getElementById('poc-case-rationale');
        if (ratEl) ratEl.textContent = caseData.rationale;

        const purpEl = document.getElementById('poc-test-purpose');
        if (purpEl) purpEl.textContent = caseData.test_purpose;

        // 2. Update Metrics for Active Model
        const metrics = caseData.metrics[activeModel];
        if (metrics) {
            const brierEl = document.getElementById('metric-brier-val');
            if (brierEl) brierEl.textContent = metrics.brier_score.toFixed(4);

            const flipEl = document.getElementById('metric-flip-val');
            if (flipEl) flipEl.textContent = `${metrics.flip_rate_pct}%`;

            const dirEl = document.getElementById('metric-dir-val');
            if (dirEl) dirEl.textContent = `${metrics.directional_acc_pct}%`;

            const brierSub = document.getElementById('metric-brier-sub');
            if (brierSub) {
                if (metrics.brier_score <= 0.25) {
                    brierSub.innerHTML = '<span class="bullish"><i class="fas fa-check-circle"></i> Beats Baseline (0.25)</span>';
                } else {
                    brierSub.innerHTML = '<span class="bearish"><i class="fas fa-triangle-exclamation"></i> Uncalibrated (> 0.25)</span>';
                }
            }

            const flipSub = document.getElementById('metric-flip-sub');
            if (flipSub) {
                if (metrics.flip_rate_pct < 10) {
                    flipSub.innerHTML = '<span class="bullish"><i class="fas fa-shield"></i> High Stability (< 10%)</span>';
                } else if (metrics.flip_rate_pct < 25) {
                    flipSub.innerHTML = '<span class="neutral"><i class="fas fa-wave-square"></i> Moderate Switching</span>';
                } else {
                    flipSub.innerHTML = '<span class="bearish"><i class="fas fa-bolt"></i> High Whipsaw Risk</span>';
                }
            }
        }

        // 3. Render Canvas Chart
        drawChart(caseData.chart_data, activeModel);
    }

    function drawChart(chartData, modelType) {
        if (!chartCanvas || !chartData || chartData.length === 0) return;
        const ctx = chartCanvas.getContext('2d');
        const dpr = window.devicePixelRatio || 1;

        const rect = chartCanvas.getBoundingClientRect();
        chartCanvas.width = rect.width * dpr;
        chartCanvas.height = rect.height * dpr;
        ctx.scale(dpr, dpr);

        const width = rect.width;
        const height = rect.height;
        const padding = { top: 30, right: 65, bottom: 40, left: 60 };

        ctx.clearRect(0, 0, width, height);

        const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
        const textColor = isDark ? '#94a3b8' : '#64748b';
        const gridColor = isDark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.06)';
        const lineColor = '#3b82f6';

        // Get Price Extremes
        const prices = chartData.map(d => d.close);
        const minPrice = Math.min(...prices) * 0.98;
        const maxPrice = Math.max(...prices) * 1.02;
        const priceRange = maxPrice - minPrice || 1;

        const chartWidth = width - padding.left - padding.right;
        const chartHeight = height - padding.top - padding.bottom;

        const getX = (index) => padding.left + (index / (chartData.length - 1)) * chartWidth;
        const getY = (price) => padding.top + chartHeight - ((price - minPrice) / priceRange) * chartHeight;

        // Draw Regime Background Shading Bands
        const bandWidth = chartWidth / (chartData.length - 1);
        chartData.forEach((d, i) => {
            const regimeKey = modelType === 'HMM' ? d.hmm_regime : (modelType === 'GMM' ? d.gmm_regime : d.rule_regime);
            let fillColor = 'transparent';
            if (regimeKey === 'Bullish') {
                fillColor = isDark ? 'rgba(16, 185, 129, 0.18)' : 'rgba(16, 185, 129, 0.12)';
            } else if (regimeKey === 'Bearish') {
                fillColor = isDark ? 'rgba(239, 68, 68, 0.18)' : 'rgba(239, 68, 68, 0.12)';
            } else {
                fillColor = isDark ? 'rgba(245, 158, 11, 0.15)' : 'rgba(245, 158, 11, 0.09)';
            }

            const xStart = i === 0 ? padding.left : getX(i) - bandWidth / 2;
            const bWidth = (i === 0 || i === chartData.length - 1) ? bandWidth / 2 : bandWidth;
            
            ctx.fillStyle = fillColor;
            ctx.fillRect(xStart, padding.top, bWidth, chartHeight);
        });

        // Draw Horizontal Grid Lines & Price Labels
        const gridSteps = 5;
        ctx.textAlign = 'right';
        ctx.textBaseline = 'middle';
        ctx.font = '11px "Plus Jakarta Sans", sans-serif';
        ctx.fillStyle = textColor;

        for (let i = 0; i <= gridSteps; i++) {
            const price = minPrice + (priceRange / gridSteps) * i;
            const y = getY(price);

            ctx.strokeStyle = gridColor;
            ctx.lineWidth = 1;
            ctx.beginPath();
            ctx.moveTo(padding.left, y);
            ctx.lineTo(width - padding.right, y);
            ctx.stroke();

            ctx.fillText(`PKR ${price.toFixed(1)}`, padding.left - 8, y);
        }

        // Draw Date Labels on X Axis
        ctx.textAlign = 'center';
        ctx.textBaseline = 'top';
        const dateStep = Math.ceil(chartData.length / 6);
        for (let i = 0; i < chartData.length; i += dateStep) {
            const x = getX(i);
            const dateStr = chartData[i].date;
            ctx.fillText(dateStr.slice(5), x, height - padding.bottom + 8);
        }

        // Draw Historical Price Line
        ctx.strokeStyle = lineColor;
        ctx.lineWidth = 2.5;
        ctx.beginPath();
        chartData.forEach((d, i) => {
            const x = getX(i);
            const y = getY(d.close);
            if (i === 0) ctx.moveTo(x, y);
            else ctx.lineTo(x, y);
        });
        ctx.stroke();

        // Draw Gradient Fill Under Price Line
        const gradient = ctx.createLinearGradient(0, padding.top, 0, height - padding.bottom);
        gradient.addColorStop(0, 'rgba(59, 130, 246, 0.25)');
        gradient.addColorStop(1, 'rgba(59, 130, 246, 0.0)');
        ctx.fillStyle = gradient;
        ctx.lineTo(getX(chartData.length - 1), height - padding.bottom);
        ctx.lineTo(getX(0), height - padding.bottom);
        ctx.closePath();
        ctx.fill();

        // Draw Regime Indicator Points on Price Line
        chartData.forEach((d, i) => {
            if (i % 2 === 0 || i === chartData.length - 1) {
                const x = getX(i);
                const y = getY(d.close);
                const regimeKey = modelType === 'HMM' ? d.hmm_regime : (modelType === 'GMM' ? d.gmm_regime : d.rule_regime);

                let dotColor = '#f59e0b';
                if (regimeKey === 'Bullish') dotColor = '#10b981';
                else if (regimeKey === 'Bearish') dotColor = '#ef4444';

                ctx.fillStyle = dotColor;
                ctx.beginPath();
                ctx.arc(x, y, 3.5, 0, Math.PI * 2);
                ctx.fill();
                ctx.strokeStyle = isDark ? '#1e293b' : '#ffffff';
                ctx.lineWidth = 1;
                ctx.stroke();
            }
        });
    }

    // Chart Tooltip Interaction
    if (chartCanvas) {
        chartCanvas.addEventListener('mousemove', (e) => {
            const caseData = pocData.test_cases[activeCaseId];
            if (!caseData || !caseData.chart_data) return;
            const chartData = caseData.chart_data;

            const rect = chartCanvas.getBoundingClientRect();
            const mouseX = e.clientX - rect.left;
            const padding = { top: 30, right: 65, bottom: 40, left: 60 };
            const chartWidth = rect.width - padding.left - padding.right;

            if (mouseX < padding.left || mouseX > rect.width - padding.right) {
                if (tooltipEl) tooltipEl.style.display = 'none';
                return;
            }

            const relativeX = (mouseX - padding.left) / chartWidth;
            const index = Math.round(relativeX * (chartData.length - 1));
            const point = chartData[Math.max(0, Math.min(chartData.length - 1, index))];

            if (point && tooltipEl) {
                const regime = activeModel === 'HMM' ? point.hmm_regime : (activeModel === 'GMM' ? point.gmm_regime : point.rule_regime);
                let badgeClass = 'sideways-badge';
                if (regime === 'Bullish') badgeClass = 'bullish-badge';
                if (regime === 'Bearish') badgeClass = 'bearish-badge';

                tooltipEl.innerHTML = `
                    <div style="font-weight: 700; color: var(--text-primary); margin-bottom: 4px;">${point.date}</div>
                    <div style="display: flex; justify-content: space-between; gap: 12px; font-size: 0.8rem; margin-bottom: 2px;">
                        <span style="color: var(--text-muted);">Close Price:</span>
                        <strong>PKR ${point.close.toFixed(2)}</strong>
                    </div>
                    <div style="display: flex; justify-content: space-between; gap: 12px; font-size: 0.8rem; margin-bottom: 4px;">
                        <span style="color: var(--text-muted);">Volume:</span>
                        <span>${Number(point.volume).toLocaleString()}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center; gap: 8px; margin-top: 6px; padding-top: 4px; border-top: 1px solid var(--border-subtle);">
                        <span style="font-size: 0.75rem; color: var(--text-muted);">${activeModel} State:</span>
                        <span class="badge ${badgeClass}" style="padding: 2px 6px; font-size: 0.75rem;">${regime}</span>
                    </div>
                `;

                tooltipEl.style.display = 'block';
                tooltipEl.style.left = `${e.clientX - rect.left + 15}px`;
                tooltipEl.style.top = `${e.clientY - rect.top - 20}px`;
            }
        });

        chartCanvas.addEventListener('mouseleave', () => {
            if (tooltipEl) tooltipEl.style.display = 'none';
        });
    }

    // Test Case Tab Switching
    tabButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            tabButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            activeCaseId = btn.getAttribute('data-case');
            renderActiveTestCase();
        });
    });

    // Model Selector Switching
    modelButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            modelButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            activeModel = btn.getAttribute('data-model');
            renderActiveTestCase();
        });
    });

    // Initial Render
    renderActiveTestCase();

    // Redraw on window resize
    window.addEventListener('resize', () => {
        renderActiveTestCase();
    });
});
