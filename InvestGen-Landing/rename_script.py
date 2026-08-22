import os
import glob
import re

html_files = glob.glob("*.html")
css_files = glob.glob("css/*.css")
js_files = glob.glob("js/*.js")

all_files = html_files + css_files + js_files

for filepath in all_files:
    if not os.path.exists(filepath):
        continue
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Simple replaces
    content = content.replace("InvestGen", "InvestOPak")
    content = content.replace("Invest Gen", "InvestOPak")
    content = content.replace("investGen", "investOPak")
    content = content.replace("invest Gen", "InvestOPak")
    
    # Specific logo replace
    content = content.replace("Invest<span>Gen</span>", "Invest<span>OPak</span>")
    
    # Also handle lowercase variants or others just in case, though python .replace is case-sensitive.
    # regex for case-insensitive replace of InvestGen without modifying HTML tags? Let's just use exact string matches first, as they cover 99% of cases.
    
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated {filepath}")
