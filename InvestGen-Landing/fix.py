import glob
import re

for file in glob.glob('*.html'):
    try:
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        with open(file, 'r', encoding='utf-16') as f:
            content = f.read()
    
    # Remove the old AI Screener link (the one pointing to screener.html)
    content = re.sub(r'\s*<li><a href="screener\.html"[^>]*>.*?AI Screener</a></li>', '', content, flags=re.IGNORECASE)
    
    # Also rename "AI Screener (Demo)" to "AI Screener"
    content = content.replace('AI Screener (Demo)', 'AI Screener')
    
    with open(file, 'w', encoding='utf-8') as f:
        f.write(content)
