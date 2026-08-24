import glob

for file in glob.glob("*.html"):
    with open(file, "r", encoding="utf-8") as f:
        html = f.read()
    
    html = html.replace('href="css/style.css"', 'href="css/style.css?v=3"')
    html = html.replace('href="css/style.css?v=2"', 'href="css/style.css?v=3"')
    
    with open(file, "w", encoding="utf-8") as f:
        f.write(html)
print("Updated cache busters in all HTML files.")
