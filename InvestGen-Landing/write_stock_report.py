stock_html = '''<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>InvestOPak | Stock Report</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Outfit:wght@600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link rel="stylesheet" href="css/style.css">
    <script src="https://unpkg.com/lightweight-charts/dist/lightweight-charts.standalone.production.js"></script>
    <style>
        .report-toggle {
            display: inline-flex;
            background: var(--bg-primary);
            border: 1px solid var(--border-color);
            border-radius: 10px;
            padding: 4px;
            gap: 4px;
            margin-bottom: 1.5rem;
        }
        .report-tab {
            padding: 9px 22px;
            border-radius: 7px;
            border: none;
            background: transparent;
            color: var(--text-secondary);
            font-size: 0.9rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            gap: 7px;
        }
        .report-tab.active { background: var(--accent-color); color: #fff; box-shadow: 0 2px 8px rgba(59,130,246,0.3); }
        .report-tab:not(.active):hover { background: var(--border-color); color: var(--text-main); }
        .report-panel { display: none; }
        .report-panel.active { display: block; }
        .simple-verdict {
            display: flex;
            align-items: center;
            gap: 1.5rem;
            background: linear-gradient(135deg, rgba(16,185,129,0.08), rgba(16,185,129,0.02));
            border: 1px solid rgba(16,185,129,0.25);
            border-radius: 16px;
            padding: 2rem;
            margin-bottom: 1.5rem;
        }
        .verdict-icon {
            font-size: 2.5rem;
            width: 70px;
            height: 70px;
            border-radius: 50%;
            background: rgba(16,185,129,0.1);
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
        }
        .verdict-text h2 { font-family: "Outfit",sans-serif; font-size: 1.8rem; margin: 0 0 0.4rem 0; color: #10b981; }
        .verdict-text p { margin: 0; color: var(--text-secondary); font-size: 0.95rem; line-height: 1.6; }
        .confidence-pill {
            display: inline-flex; align-items: center; gap: 6px;
            background: rgba(16,185,129,0.1); color: #059669;
            border-radius: 20px; padding: 4px 14px;
            font-size: 0.85rem; font-weight: 600; margin-top: 0.75rem;
        }
        .simple-section {
            background: var(--bg-primary);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1rem;
        }
        .simple-section h4 { font-family: "Outfit",sans-serif; margin: 0 0 0.75rem 0; font-size: 1rem; display: flex; align-items: center; gap: 8px; }
        .simple-section p { margin: 0; color: var(--text-secondary); font-size: 0.92rem; line-height: 1.7; }
        .simple-bullets { list-style: none; padding: 0; margin: 0; }
        .simple-bullets li { display: flex; align-items: flex-start; gap: 10px; padding: 5px 0; color: var(--text-secondary); font-size: 0.92rem; }
        .simple-bullets li i { margin-top: 3px; flex-shrink: 0; }
        .actions-row { display: flex; gap: 1rem; margin-top: 1.5rem; flex-wrap: wrap; }
    </style>
</head>
<body class="dashboard-body">
    <aside class="sidebar">
        <div class="sidebar-header"><a href="index.html" class="logo">Invest<span>OPak</span></a></div>
        <ul class="sidebar-nav">
            <li><a href="dashboard.html"><i class="fas fa-home"></i> Dashboard</a></li>
            <li><a href="market-overview.html"><i class="fas fa-globe"></i> Market Overview</a></li>
            <li><a href="screener-demo.html"><i class="fas fa-robot"></i> AI Screener</a></li>
            <li><a href="portfolio.html"><i class="fas fa-briefcase"></i> Portfolio</a></li>
            <li><a href="all-stocks.html" class="active"><i class="fas fa-list"></i> All Stocks</a></li>
            <li><a href="calibration.html"><i class="fas fa-tachometer-alt"></i> Calibration</a></li>
            <li><a href="watchlist.html"><i class="fas fa-star"></i> Watchlist</a></li>
        </ul>
        <div class="sidebar-footer"><a href="settings.html"><i class="fas fa-cog"></i> Settings</a></div>
    </aside>

    <div class="main-wrapper">
        <header class="top-nav">
            <div class="search-bar"><i class="fas fa-search"></i><input type="text" placeholder="Search ticker or company..."></div>
            <div class="top-nav-actions">
                <button id="theme-toggle"><i class="fas fa-moon"></i></button>
                <a href="notifications.html" class="nav-icon-btn"><i class="fas fa-bell"></i><span class="badge">2</span></a>
                <a href="profile.html" class="user-profile" style="text-decoration:none;color:inherit;"><div class="avatar">IB</div><span>Immad Baber</span></a>
            </div>
        </header>

        <main class="dashboard-content">
            <!-- Header -->
            <div class="welcome-header" style="display:flex;justify-content:space-between;align-items:flex-end;margin-bottom:1rem;">
                <div>
                    <h1 id="stock-report-title" style="font-size:2.2rem;margin-bottom:0;">ENGRO <span style="font-size:1.1rem;color:var(--text-secondary);font-weight:normal;">Engro Corporation Limited</span></h1>
                    <p id="stock-price-header" class="market-status" style="font-size:1.6rem;font-weight:bold;margin:0.25rem 0 0;">Rs. 305.20 <span class="bullish" style="font-size:1rem;margin-left:0.5rem;">+2.4% Today</span></p>
                </div>
                <button class="btn btn-secondary"><i class="fas fa-star"></i> Add to Watchlist</button>
            </div>

            <!-- Report Toggle -->
            <div class="report-toggle">
                <button class="report-tab active" id="tab-simple" onclick="switchTab(\'simple\')">
                    <i class="fas fa-user"></i> Simple Report
                </button>
                <button class="report-tab" id="tab-technical" onclick="switchTab(\'technical\')">
                    <i class="fas fa-chart-line"></i> Technical Report
                </button>
            </div>

            <!-- SIMPLE PANEL -->
            <div class="report-panel active" id="panel-simple">
                <div class="simple-verdict">
                    <div class="verdict-icon"><i class="fas fa-arrow-up" style="color:#10b981;"></i></div>
                    <div class="verdict-text">
                        <h2>Bullish Outlook</h2>
                        <p>Based on current technical signals, market conditions, and historical patterns, ENGRO shows a <strong>positive short-term outlook</strong>. The market is in a Trending Bullish regime, which favours momentum strategies.</p>
                        <span class="confidence-pill"><i class="fas fa-circle-check"></i> 92% AI Confidence Score</span>
                    </div>
                </div>

                <div class="simple-section">
                    <h4><i class="fas fa-lightbulb" style="color:#f59e0b;"></i> What this means in plain language</h4>
                    <p>The AI analyzed ENGRO using the most relevant indicators for the current market environment. In simple terms: <strong>more signals are pointing up than down</strong>. The trend is strong, volume supports the move, and no major red flags were found in the fundamentals. This does not guarantee profit. It means conditions currently look favorable based on historical patterns.</p>
                </div>

                <div class="simple-section">
                    <h4><i class="fas fa-list-check" style="color:var(--accent-color);"></i> Key signals used</h4>
                    <ul class="simple-bullets">
                        <li><i class="fas fa-check" style="color:#10b981;"></i><span><strong>RSI (64.2):</strong> Healthy momentum. Not yet overbought. Good sign.</span></li>
                        <li><i class="fas fa-check" style="color:#10b981;"></i><span><strong>MACD:</strong> Bullish crossover confirmed. Trend is gaining strength.</span></li>
                        <li><i class="fas fa-check" style="color:#10b981;"></i><span><strong>HMM Market Regime:</strong> Detected as Trending Bullish. Momentum indicators are most reliable here.</span></li>
                        <li><i class="fas fa-check" style="color:#10b981;"></i><span><strong>P/E Ratio (6.8x):</strong> Reasonably valued vs. the sector. Not overpriced.</span></li>
                        <li><i class="fas fa-exclamation-triangle" style="color:#f59e0b;"></i><span><strong>Volume (1.54M):</strong> Above average. Confirms the move is genuine.</span></li>
                    </ul>
                </div>

                <div class="simple-section" style="border-color:rgba(59,130,246,0.25);background:rgba(59,130,246,0.03);">
                    <h4><i class="fas fa-shield-alt" style="color:var(--accent-color);"></i> Safety Check (Disconfirmation Agent)</h4>
                    <p>The system searched <strong>14 historical cases</strong> with a similar setup to today\'s ENGRO pattern. In <strong>85% of those cases</strong>, the stock continued upward. In 15% it pulled back. No major conflicting evidence found. This recommendation is considered relatively reliable given the historical base rate.</p>
                </div>

                <div class="actions-row">
                    <a href="screener-demo.html" class="btn btn-primary"><i class="fas fa-robot"></i> Analyze with AI Screener</a>
                    <button class="btn btn-secondary" onclick="switchTab(\'technical\')"><i class="fas fa-chart-line"></i> View Technical Detail</button>
                    <button class="btn btn-secondary"><i class="fas fa-star"></i> Add to Watchlist</button>
                </div>
            </div>

            <!-- TECHNICAL PANEL -->
            <div class="report-panel" id="panel-technical">
                <div class="widgets-grid" style="margin-bottom:2rem;">
                    <div class="widget-card">
                        <div class="widget-header">
                            <h3>GenAI Technical Report</h3>
                            <span id="stock-confidence" class="badge bullish-badge">92% Confidence</span>
                        </div>
                        <div class="widget-body">
                            <p style="color:var(--text-secondary);margin-bottom:1rem;line-height:1.8;"><strong>AI Summary:</strong> ENGRO is currently exhibiting strong bullish momentum within a low-volatility market regime. The Hidden Markov Model (HMM) confirms the trend is stable. The Genetic Algorithm has heavily weighted the MACD crossover and ADX/DMI indicators, which both align positively.</p>
                            <p style="color:var(--text-secondary);line-height:1.8;">Fundamental tailwinds, specifically robust P/E positioning relative to the sector, further support this view. Expected Calibration Error (ECE) for similar past predictions is low (4.1%), indicating high reliability.</p>
                        </div>
                    </div>
                    <div class="widget-card">
                        <div class="widget-header" style="background-color:rgba(37,99,235,0.05);">
                            <h3 style="color:var(--accent-color);"><i class="fas fa-shield-alt"></i> Disconfirmation Check</h3>
                        </div>
                        <div class="widget-body">
                            <div style="display:flex;gap:1rem;align-items:flex-start;">
                                <i class="fas fa-check-circle" style="color:#10b981;font-size:2rem;"></i>
                                <div>
                                    <h4 style="margin-bottom:0.5rem;">No Major Conflicts Found</h4>
                                    <p style="color:var(--text-secondary);font-size:0.95rem;">14 historical analogs analyzed. In 85% of cases the stock continued upward. No major macro contradictions detected.</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="widget-card" style="margin-bottom:2rem;">
                    <div class="widget-header">
                        <div style="display:flex;align-items:center;justify-content:space-between;width:100%;">
                            <h3 style="margin:0;">Technical Chart (OHLCV)</h3>
                            <div style="display:flex;gap:0.5rem;">
                                <button class="btn btn-primary filter-btn" data-period="ALL" style="padding:0.2rem 0.8rem;font-size:0.85rem;">All</button>
                                <button class="btn filter-btn" data-period="3M" style="padding:0.2rem 0.8rem;font-size:0.85rem;">3M</button>
                                <button class="btn filter-btn" data-period="1M" style="padding:0.2rem 0.8rem;font-size:0.85rem;">1M</button>
                                <button class="btn filter-btn" data-period="7D" style="padding:0.2rem 0.8rem;font-size:0.85rem;">7D</button>
                            </div>
                        </div>
                    </div>
                    <div id="lightweight-chart-container" class="widget-body" style="height:300px;display:flex;align-items:center;justify-content:center;border:1px dashed var(--border-color);border-radius:8px;">
                        <span style="color:var(--text-secondary);"><i class="fas fa-chart-bar"></i> Loading Interactive Chart...</span>
                    </div>
                </div>

                <div class="metrics-grid">
                    <div class="metric-card"><span class="metric-label">HMM Regime</span><div class="metric-value bullish-text">Trending Bullish</div></div>
                    <div class="metric-card"><span class="metric-label">RSI (14)</span><div class="metric-value">64.2</div></div>
                    <div class="metric-card"><span class="metric-label">P/E Ratio</span><div class="metric-value">6.8x</div></div>
                    <div class="metric-card"><span class="metric-label">Volume</span><div class="metric-value">1,542,300</div></div>
                    <div class="metric-card"><span class="metric-label">Market Cap</span><div class="metric-value">Rs 165.00B</div></div>
                    <div class="metric-card"><span class="metric-label">MACD</span><div class="metric-value bullish-text">Crossover UP</div></div>
                </div>

                <div class="actions-row">
                    <a href="screener-demo.html" class="btn btn-primary"><i class="fas fa-robot"></i> Deep Analyze with AI Screener</a>
                    <button class="btn btn-secondary" onclick="switchTab(\'simple\')"><i class="fas fa-user"></i> View Simple Report</button>
                </div>
            </div>
        </main>
    </div>

    <script src="js/main.js"></script>
    <script src="js/dashboard_data.js"></script>
    <script>
        function switchTab(tab) {
            document.querySelectorAll(\'.report-tab\').forEach(t => t.classList.remove(\'active\'));
            document.querySelectorAll(\'.report-panel\').forEach(p => p.classList.remove(\'active\'));
            document.getElementById(\'tab-\' + tab).classList.add(\'active\');
            document.getElementById(\'panel-\' + tab).classList.add(\'active\');
        }
        const ticker = new URLSearchParams(window.location.search).get(\'ticker\') || \'ENGRO\';
        document.getElementById(\'stock-report-title\').innerHTML = ticker + \' <span style="font-size:1.1rem;color:var(--text-secondary);font-weight:normal;">Stock Report</span>\';
    </script>
</body>
</html>'''

with open('stock-report.html', 'w', encoding='utf-8') as f:
    f.write(stock_html)
print('Done! Written', len(stock_html), 'bytes')
