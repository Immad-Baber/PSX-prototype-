import re

with open('stock-report.html', 'r', encoding='utf-8') as f:
    html = f.read()

start_script = html.find('const urlParams = new URLSearchParams(window.location.search);')
if start_script != -1:
    end_script = html.find('</script>', start_script)
    html = html[:start_script] + html[end_script:]

html = html.replace(
    'ENGRO shows a <strong>positive short', 
    '<span class="dynamic-ticker">ENGRO</span> shows a <strong>positive short'
)
html = html.replace(
    'The AI analyzed ENGRO using the most',
    'The AI analyzed <span class="dynamic-ticker">ENGRO</span> using the most'
)
html = html.replace(
    'In the last year, ENGRO reported massive',
    'In the last year, <span class="dynamic-ticker">ENGRO</span> reported massive'
)
html = html.replace(
    "today's ENGRO pattern.",
    "today's <span class=\"dynamic-ticker\">ENGRO</span> pattern."
)
html = html.replace(
    '<p style="color:var(--text-secondary);margin-bottom:1rem;line-height:1.8;"><strong>AI Summary:</strong> ENGRO is currently exhibiting strong bullish momentum within a low-volatility market regime. The Hidden Markov Model (HMM) confirms the trend is stable. The Genetic Algorithm has heavily weighted the MACD crossover and ADX/DMI indicators, which both align positively.</p>',
    '<p id="stock-ai-summary-tech" style="color:var(--text-secondary);margin-bottom:1rem;line-height:1.8;"><strong>AI Summary:</strong> <span class="dynamic-ticker">ENGRO</span> is currently exhibiting strong bullish momentum...</p>'
)

with open('stock-report.html', 'w', encoding='utf-8') as f:
    f.write(html)
