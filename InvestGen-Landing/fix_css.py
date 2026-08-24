import re

css_to_insert = """
.welcome-header h1 {
  font-size: 2rem;
  margin-bottom: 0.2rem;
}

.market-status {
  color: var(--text-secondary);
  font-size: 1.1rem;
}

.bullish { color: #10b981; font-weight: 600; }
.bearish { color: #ef4444; font-weight: 600; }
.sideways { color: #f59e0b; font-weight: 600; }

/* Brief Box */
.dashboard-brief {
  background: linear-gradient(135deg, rgba(37, 99, 235, 0.05) 0%, rgba(16, 185, 129, 0.05) 100%);
  border: 1px solid rgba(37, 99, 235, 0.2);
  border-radius: 12px;
  display: flex;
  align-items: center;
  padding: 1.5rem 2rem;
  margin-bottom: 2rem;
  box-shadow: 0 10px 30px -10px rgba(37, 99, 235, 0.15);
  position: relative;
  overflow: hidden;
  backdrop-filter: blur(8px);
}

.brief-accent {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
  background-color: var(--accent-color);
}

.brief-content {
  flex: 1;
}

.brief-label {
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: var(--accent-color);
  font-weight: 700;
}

.brief-content h2 {
  font-size: 1.3rem;
  margin: 0.5rem 0;
}

.brief-content p {
  color: var(--text-secondary);
  font-size: 0.95rem;
}

/* Metrics Grid */
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1.5rem;
  margin-bottom: 2.5rem;
}

.metric-card {
  background-color: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: var(--card-shadow);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.metric-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 24px -10px rgba(37, 99, 235, 0.2);
  border-color: rgba(37, 99, 235, 0.4);
}

.metric-label {
  color: var(--text-secondary);
  font-size: 0.9rem;
  font-weight: 500;
  display: block;
  margin-bottom: 0.5rem;
}

.metric-value {
  font-size: 1.8rem;
  font-family: 'Outfit', sans-serif;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

.bullish-text { color: #10b981; }

.metric-sub {
  font-size: 0.85rem;
  color: var(--text-secondary);
}

/* Complex Widgets */
.widgets-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
}

.widget-card {
  background-color: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  box-shadow: var(--card-shadow);
  overflow: hidden;
}

.widget-header {
  padding: 1.2rem 1.5rem;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.widget-header h3 {
  margin: 0;
  font-size: 1.1rem;
}

.live-status {
  font-size: 0.85rem;
  color: var(--text-secondary);
}
.live-status strong { color: #10b981; }

.widget-body {
  padding: 1.5rem;
}

/* Regime Bar Compass */
.regime-bar {
  display: flex;
  border-radius: 8px;
  overflow: hidden;
  height: 40px;
  margin-bottom: 1rem;
}

.regime-segment {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 0.85rem;
  color: white;
  opacity: 0.3;
}

.regime-segment.bearish { background-color: #ef4444; }
.regime-segment.sideways { background-color: #f59e0b; }
.regime-segment.bullish { background-color: #10b981; }
.regime-segment.active { opacity: 1; box-shadow: inset 0 0 10px rgba(0,0,0,0.2); }

.widget-desc {
  font-size: 0.9rem;
  color: var(--text-secondary);
}

/* Data Table */
.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th, .data-table td {
  padding: 1rem 1.5rem;
  text-align: left;
  border-bottom: 1px solid var(--border-color);
}
.data-table tbody tr {
  transition: all 0.2s ease;
}
.data-table tbody tr:hover {
  background-color: rgba(37, 99, 235, 0.03);
  transform: translateX(4px);
}

.data-table tr:last-child td {
  border-bottom: none;
}

.badge {
  padding: 0.2rem 0.6rem;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 700;
}
.bullish-badge { background-color: rgba(16, 185, 129, 0.1); color: #10b981; }
"""

with open('css/style.css', 'r', encoding='utf-8') as f:
    content = f.read()

# I will replace from .welcome-header h1 down to .bearish-badge
import re
new_content = re.sub(r'\.bearish-badge {', css_to_insert + '\n.bearish-badge {', content)

with open('css/style.css', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("CSS Fixed")
