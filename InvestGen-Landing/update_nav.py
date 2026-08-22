import glob
import re

html_files = glob.glob('*.html')
for file in html_files:
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove the screener.html list item
    content = re.sub(r'\s*<li><a href="screener\.html"><i class="fas fa-filter"></i> AI Screener</a></li>', '', content)
    
    # Rename AI Screener (Demo) to AI Screener
    content = content.replace('AI Screener (Demo)', 'AI Screener')
    
    with open(file, 'w', encoding='utf-8') as f:
        f.write(content)
print('Sidebar updated across all HTML files.')
