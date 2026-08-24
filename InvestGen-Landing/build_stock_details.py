from bs4 import BeautifulSoup
import re

with open('stock-details.html', 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

# Change title
title = soup.find('title')
if title:
    title.string = "InvestOPak | Stock Details"

# Remove "Export PDF" from the top since this isn't a report yet
# The div has: <button class="btn btn-primary" onclick="alert('Exporting Report as PDF...')">
export_btn = soup.find('button', string=re.compile('Export PDF'))
if export_btn:
    export_btn.decompose()

# Remove report toggle
toggle = soup.find('div', class_='report-toggle')
if toggle:
    toggle.decompose()

# Remove Simple Panel
simple_panel = soup.find('div', id='panel-simple')
if simple_panel:
    simple_panel.decompose()

# Process Technical Panel
tech_panel = soup.find('div', id='panel-technical')
main_content = soup.find('main', id='main-content')

if tech_panel and main_content:
    # Find chart widget
    chart_widget = tech_panel.find('div', id='lightweight-chart-container').parent
    
    # Find metrics grid
    metrics_grid = tech_panel.find('div', class_='metrics-grid')
    
    # Append them directly to main_content
    if chart_widget:
        main_content.append(chart_widget)
    if metrics_grid:
        main_content.append(metrics_grid)
        
    # Append CTA Button
    cta_html = """
    <div style="text-align:center; margin-top: 3rem; margin-bottom: 2rem;">
        <button id="btn-run-ai" class="btn btn-primary" style="font-size: 1.1rem; padding: 0.75rem 2rem; border-radius: 30px; box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4); transition: transform 0.2s ease;">
            <i class="fas fa-robot"></i> Run AI Analysis on this Stock
        </button>
    </div>
    """
    cta_soup = BeautifulSoup(cta_html, 'html.parser')
    main_content.append(cta_soup)
    
    # Remove the rest of the technical panel
    tech_panel.decompose()

# We need to update the Javascript to add the onclick handler for the new CTA button
# The JS is inside the <script> tag at the end. We'll just replace the string.

html_out = soup.encode(formatter='html').decode('utf-8')

# JS tweaks
html_out = html_out.replace("document.querySelectorAll('.report-tab')", "// removed tabs")
js_insert = """
                    document.getElementById('comp-range').innerText = `Rs ${low} - ${high}`;
                    
                    // Add CTA functionality
                    document.getElementById('btn-run-ai').onclick = function() {
                        window.location.href = 'screener-demo.html?ticker=' + stockData.ticker;
                    };
"""
html_out = html_out.replace("document.getElementById('comp-range').innerText = `Rs ${low} - ${high}`;", js_insert)

with open('stock-details.html', 'w', encoding='utf-8') as f:
    f.write(html_out)

print("stock-details.html built successfully.")
