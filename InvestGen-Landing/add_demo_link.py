import glob

html_files = glob.glob("*.html")

for filepath in html_files:
    if filepath == "screener-demo.html":
        continue
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'screener-demo.html' in content:
        continue

    lines = content.split('\n')
    new_lines = []
    for line in lines:
        new_lines.append(line)
        if '<li><a href="screener.html' in line:
            # Add the demo link right after the AI Screener link
            indent = line.split('<')[0]
            new_lines.append(f'{indent}<li><a href="screener-demo.html"><i class="fas fa-robot"></i> AI Screener (Demo)</a></li>')
    
    new_content = '\n'.join(new_lines)
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated {filepath}")
