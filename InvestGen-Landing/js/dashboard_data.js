window.onerror = function(msg, url, line) {
    const errDiv = document.createElement('div');
    errDiv.style.cssText = 'position:fixed;top:0;left:0;width:100%;background:red;color:white;z-index:9999;padding:10px;text-align:center;font-weight:bold;';
    errDiv.textContent = 'JS Error: ' + msg + ' (Line: ' + line + ')';
    document.body.appendChild(errDiv);
};

document.addEventListener('DOMContentLoaded', async () => {
    try {
        // Cache bust the JSON fetch to ensure fresh data
        const response = await fetch('data/market_data.json?t=' + new Date().getTime());
        const data = await response.json();
        
        // --- 1. Dashboard: Top 5 Table ---
        const dashboardTableBody = document.querySelector('#dashboard-top-5-body');
        if (dashboardTableBody) {
            dashboardTableBody.innerHTML = '';
            data.top_5.forEach(stock => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td><strong>${stock.ticker}</strong></td>
                    <td>${stock.name}</td>
                    <td>Rs. ${stock.price}</td>
                    <td class="${stock.change > 0 ? 'bullish' : 'bearish'}">${stock.change > 0 ? '+' : ''}${stock.change}%</td>
                    <td><span class="badge ${stock.change > 0 ? 'bullish-badge' : 'bearish-badge'}">${stock.regime}</span></td>
                    <td>${stock.confidence}%</td>
                `;
                dashboardTableBody.appendChild(tr);
            });
        }

        // --- 2. Dashboard: Watchlist Grid ---
        const watchlistGrid = document.querySelector('#dashboard-watchlist-grid');
        if (watchlistGrid) {
            watchlistGrid.innerHTML = '';
            // Only show 2 stocks in the watchlist as requested
            const watchlistStocks = Object.values(data.stocks).slice(0, 2);
            watchlistStocks.forEach(stock => {
                const card = document.createElement('div');
                card.style.border = "1px solid var(--border-color)";
                card.style.borderRadius = "8px";
                card.style.padding = "1rem";
                card.style.backgroundColor = "var(--bg-primary)";
                card.style.display = "flex";
                card.style.flexDirection = "column";
                card.style.justifyContent = "space-between";
                
                card.innerHTML = `
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                        <strong style="font-size: 1.1rem;">${stock.ticker}</strong>
                        <span style="font-size: 0.8rem; color: var(--text-secondary);">${stock.name.split(' ')[0]}</span>
                    </div>
                    <div style="display: flex; align-items: baseline; gap: 0.5rem;">
                        <span style="font-size: 1.4rem; font-weight: bold;">Rs ${stock.price}</span>
                        <span class="${stock.change > 0 ? 'bullish' : 'bearish'}" style="font-size: 0.9rem;">
                            ${stock.change > 0 ? '+' : ''}${stock.change}%
                        </span>
                    </div>
                `;
                watchlistGrid.appendChild(card);
            });
        }
        
        // --- 3. Market Overview: Text Description ---
        const marketDesc = document.querySelector('#market-regime-desc');
        if (marketDesc) {
            marketDesc.textContent = data.market_overview.regime;
            if(data.market_overview.regime.includes("Bearish")) {
                marketDesc.className = "badge bearish-badge";
            }
        }

        // --- 4. Market Overview: Index Chart ---
        const indexChartContainer = document.querySelector('#index-chart-container');
        if (indexChartContainer && data.market_overview.index_chart) {
            try {
                renderChart(data.market_overview.index_chart, 'index-chart-container');
            } catch(e) { 
                console.error("Index Chart Error:", e);
                indexChartContainer.innerHTML = '<div style="color:red;padding:20px;">Chart Error: ' + e.message + '</div>';
            }
        }

        // --- 5. Market Overview: Top Point Contributors ---
        const contributorsContainer = document.querySelector('#point-contributors-container');
        if (contributorsContainer && data.market_overview.contributors) {
            try {
                contributorsContainer.innerHTML = '';
            
            // Find max absolute value for scaling
            const maxVal = Math.max(...data.market_overview.contributors.map(c => Math.abs(c.points)));
            
            data.market_overview.contributors.forEach(contributor => {
                const isPositive = contributor.points > 0;
                const widthPercent = (Math.abs(contributor.points) / maxVal) * 100;
                
                const row = document.createElement('div');
                row.style.display = "flex";
                row.style.alignItems = "center";
                row.style.gap = "1rem";
                
                row.innerHTML = `
                    <div style="width: 50px; font-weight: 500;">${contributor.ticker}</div>
                    <div style="flex-grow: 1; display: flex; align-items: center;">
                        <div style="
                            width: ${widthPercent}%; 
                            height: 20px; 
                            background-color: ${isPositive ? '#10b981' : '#ef4444'}; 
                            border-radius: 4px;
                        "></div>
                    </div>
                    <div style="width: 60px; text-align: right; font-weight: bold; color: ${isPositive ? '#10b981' : '#ef4444'}">
                        ${isPositive ? '+' : ''}${contributor.points.toFixed(2)}
                    </div>
                `;
                contributorsContainer.appendChild(row);
            });
            } catch(e) { console.error("Contributors Error:", e); }
        }

        // --- 6. Market Overview: Commodities ---
        const commoditiesGrid = document.querySelector('#commodities-grid');
        if (commoditiesGrid && data.market_overview.commodities) {
            commoditiesGrid.innerHTML = '';
            const comms = data.market_overview.commodities;
            
            const renderCommodity = (name, dataObj) => {
                const isPositive = dataObj.change > 0;
                return `
                    <div style="padding: 1rem; border-radius: 8px; background: var(--bg-secondary); border: 1px solid var(--border-color); display: flex; justify-content: space-between; align-items: center; border-left: 4px solid ${isPositive ? '#10b981' : '#ef4444'};">
                        <span style="font-weight: 500;">${name}</span>
                        <div style="text-align: right;">
                            <div style="font-size: 1.2rem; font-weight: bold; color: var(--text-primary);">$${dataObj.price.toLocaleString()}</div>
                            <div class="${isPositive ? 'bullish' : 'bearish'}" style="font-size: 0.9rem;">${isPositive ? '+' : ''}${dataObj.change}%</div>
                        </div>
                    </div>
                `;
            };
            
            commoditiesGrid.innerHTML += renderCommodity('Gold (oz)', comms.gold);
            commoditiesGrid.innerHTML += renderCommodity('Silver', comms.silver);
            commoditiesGrid.innerHTML += renderCommodity('Crude Oil (WTI)', comms.crude_oil);
            commoditiesGrid.innerHTML += renderCommodity('Copper', comms.copper);
        }
        
        // --- 7. Stock Report Data ---
        const stockReportTitle = document.querySelector('#stock-report-title');
        if (stockReportTitle) {
            const urlParams = new URLSearchParams(window.location.search);
            const currentTicker = urlParams.get('ticker') || 'ENGRO';
            const stock = data.stocks[currentTicker];
            if(stock) {
                stockReportTitle.innerHTML = `${stock.ticker} <span style="font-size: 1.2rem; color: var(--text-secondary); font-weight: normal;">${stock.name}</span>`;
                
                document.querySelectorAll('.dynamic-ticker').forEach(el => {
                    el.textContent = stock.ticker;
                });
                
                const headerPrice = document.querySelector('#stock-price-header');
                if (headerPrice) headerPrice.innerHTML = `Rs. ${stock.price} <span class="${stock.change > 0 ? 'bullish' : 'bearish'}" style="font-size: 1.1rem; margin-left: 0.5rem;">${stock.change > 0 ? '+' : ''}${stock.change}% Today</span>`;
                
                const confidenceEl = document.querySelector('#stock-confidence');
                if(confidenceEl) confidenceEl.textContent = `${stock.confidence}% Confidence`;
                
                const summaryEl = document.querySelector('#stock-ai-summary');
                if (summaryEl) summaryEl.innerHTML = `<strong>AI Summary:</strong> ${stock.ai_summary}`;
                
                const disconfEl = document.querySelector('#stock-disconf-summary');
                if(disconfEl) disconfEl.textContent = stock.disconfirmation;
                
                const metricRegime = document.querySelector('#metric-regime');
                if(metricRegime) metricRegime.textContent = stock.regime;
                
                const metricRsi = document.querySelector('#metric-rsi');
                if(metricRsi) metricRsi.textContent = stock.rsi;
                
                const metricMacd = document.querySelector('#metric-macd');
                if(metricMacd) metricMacd.textContent = stock.macd;
                
                const metricPe = document.querySelector('#metric-pe');
                if(metricPe) metricPe.textContent = stock.pe + 'x';
                
                const metricVolume = document.querySelector('#metric-volume');
                if(metricVolume) metricVolume.textContent = stock.volume;

                const metricMarketCap = document.querySelector('#metric-market-cap');
                if(metricMarketCap) metricMarketCap.textContent = stock.market_cap;

                // Render Chart
                if (window.LightweightCharts && stock.chart_data) {
                    try {
                        renderChart(stock.chart_data, 'lightweight-chart-container');
                    } catch(e) { console.error("Stock Chart Error:", e); }
                }
            }
        }
        
    } catch (error) {
        console.error("Error loading market data:", error);
        
        // Show the error on screen so the user can see it!
        const errDiv = document.createElement('div');
        errDiv.style.cssText = 'position:fixed;top:0;left:0;width:100%;background:red;color:white;z-index:9999;padding:20px;text-align:center;font-weight:bold;font-size:1.2rem;';
        errDiv.innerHTML = 'Failed to load market_data.json!<br><br>Detailed Error: ' + error.message + '<br><br>Make sure your python web server is running and you generated the data.';
        document.body.appendChild(errDiv);
    }
});

function renderChart(chartData, containerId) {
    if (!window.LightweightCharts) {
        console.warn("LightweightCharts library not loaded.");
        return;
    }

    const chartContainer = document.getElementById(containerId);
    if (!chartContainer) return;
    
    chartContainer.innerHTML = ''; // Clear placeholder
    chartContainer.style.display = 'block';
    
    // Detect dark mode
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    const textColor = isDark ? '#94a3b8' : '#475569';
    
    // Measure exact container width upfront before creating chart
    const initialWidth = Math.floor(chartContainer.getBoundingClientRect().width || chartContainer.clientWidth || 800);
    const initialHeight = chartContainer.clientHeight || 380;
    
    const chart = LightweightCharts.createChart(chartContainer, {
        width: initialWidth,
        height: initialHeight,
        layout: {
            background: { type: 'solid', color: 'transparent' },
            textColor: textColor,
            fontFamily: "'Plus Jakarta Sans', sans-serif",
            fontSize: 11,
        },
        grid: {
            vertLines: { color: isDark ? 'rgba(255,255,255,0.04)' : 'rgba(0,0,0,0.04)' },
            horzLines: { color: isDark ? 'rgba(255,255,255,0.04)' : 'rgba(0,0,0,0.04)' },
        },
        timeScale: {
            borderColor: isDark ? 'rgba(255,255,255,0.08)' : 'rgba(0,0,0,0.08)',
            fixLeftEdge: true,
            fixRightEdge: true,
            rightOffset: 0,
            lockVisibleTimeRangeOnResize: true,
        },
        handleScroll: { mouseWheel: false, pressedMouseMove: true },
        handleScale: { mouseWheel: false, pinch: false },
    });

    const candlestickSeries = chart.addSeries(LightweightCharts.CandlestickSeries, {
        upColor: '#10b981',
        downColor: '#ef4444',
        borderVisible: false,
        wickUpColor: '#10b981',
        wickDownColor: '#ef4444',
    });

    // Ensure data is sorted chronologically
    const sortedData = [...chartData].sort((a, b) => new Date(a.time) - new Date(b.time));

    // Set data and fit synchronously immediately (no setTimeout or rAF delay that causes visual jump)
    candlestickSeries.setData(sortedData);
    chart.timeScale().fitContent();

    // Guarded ResizeObserver: only resize if dimensions genuinely change (e.g. window resize), not on initial mount
    let lastWidth = initialWidth;
    if (window.ResizeObserver) {
        const ro = new ResizeObserver(entries => {
            for (const entry of entries) {
                const newWidth = Math.floor(entry.contentRect.width);
                if (newWidth > 0 && Math.abs(newWidth - lastWidth) > 3) {
                    lastWidth = newWidth;
                    chart.applyOptions({ width: newWidth });
                    chart.timeScale().fitContent();
                }
            }
        });
        ro.observe(chartContainer);
    }

    // Add filter logic if buttons exist
    const filterBtns = document.querySelectorAll('.filter-btn');
    if (filterBtns.length > 0) {
        filterBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                // Reset styles
                filterBtns.forEach(b => {
                    b.classList.remove('btn-primary');
                });
                e.target.classList.add('btn-primary');
                
                const period = e.target.dataset.period;
                let filteredData = [...sortedData];
                
                if (period === '7D') filteredData = sortedData.slice(-7);
                if (period === '1M') filteredData = sortedData.slice(-30);
                if (period === '3M') filteredData = sortedData.slice(-90);
                
                candlestickSeries.setData(filteredData);
                chart.timeScale().fitContent();
            });
        });
    }
}
