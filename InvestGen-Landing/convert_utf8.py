import glob
import re
import os

for file in glob.glob('*.html'):
    # Try reading as utf-8, fallback to utf-16
    content = None
    try:
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        with open(file, 'r', encoding='utf-16') as f:
            content = f.read()
            
    if content:
        # Strip out the exact HTML string for the old screener link if it's there
        content = re.sub(r'\s*<li><a href="screener\.html"[^>]*>.*?AI Screener</a></li>', '', content, flags=re.IGNORECASE)
        content = re.sub(r'\s*<li><a href="screener\.html">.*?</a></li>', '', content, flags=re.IGNORECASE|re.DOTALL)
        
        # Look for EXACT strings just to be perfectly sure
        content = content.replace('<li><a href="screener.html"><i class="fas fa-filter"></i> AI Screener</a></li>', '')
        
        # Write back EXPLICITLY as utf-8
        with open(file, 'w', encoding='utf-8') as f:
            f.write(content)

print("Converted all HTML files to UTF-8 and stripped the old links.")
