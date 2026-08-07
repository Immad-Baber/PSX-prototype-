import glob

html_files = glob.glob("*.html")

for filepath in html_files:
    if filepath == "all-stocks.html":
        continue
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Insert All Stocks link after Portfolio
    target = '<li><a href="portfolio.html"><i class="fas fa-briefcase"></i> Portfolio</a></li>'
    replacement = '<li><a href="portfolio.html"><i class="fas fa-briefcase"></i> Portfolio</a></li>\n            <li><a href="all-stocks.html"><i class="fas fa-list"></i> All Stocks</a></li>'
    
    if target in content and "all-stocks.html" not in content:
        content = content.replace(target, replacement)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated {filepath}")
