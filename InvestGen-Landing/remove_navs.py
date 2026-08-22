import glob
import re

for file in glob.glob('*.html'):
    try:
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        with open(file, 'r', encoding='utf-16') as f:
            content = f.read()
            
    # Remove Disconfirmation link
    content = re.sub(r'\s*<li><a href="disconfirmation\.html"[^>]*>.*?Disconfirmation</a></li>', '', content, flags=re.IGNORECASE)
    
    # Remove Recommendations link
    content = re.sub(r'\s*<li><a href="recommendations\.html"[^>]*>.*?Recommendations</a></li>', '', content, flags=re.IGNORECASE)
    
    with open(file, 'w', encoding='utf-8') as f:
        f.write(content)

print("Removed Disconfirmation and Recommendations from sidebar across all files.")
