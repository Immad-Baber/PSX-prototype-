import glob
import re
from bs4 import BeautifulSoup, NavigableString

glossary = {
    r'(?i)\bbullish\b': ('Bullish', 'A market state where prices are expected to rise.'),
    r'(?i)\bbearish\b': ('Bearish', 'A market state where prices are expected to fall.'),
    r'(?i)\bcalibration\b': ('Calibration', 'The process of adjusting AI parameters to match real-world historical data.'),
    r'(?i)\bindicators\b': ('Indicators', 'Mathematical calculations based on price/volume used to predict future trends.'),
    r'(?i)\bindicator\b': ('Indicator', 'A mathematical calculation based on price/volume used to predict future trends.'),
    r'(?i)\bvolatility\b': ('Volatility', 'The rate at which the price of a stock increases or decreases.'),
    r'(?i)\bmomentum\b': ('Momentum', 'The strength or speed of a price trend.'),
    r'(?i)\bfundamentals\b': ('Fundamentals', 'The underlying financial health of a company (revenue, earnings, debt).'),
    r'(?i)\bfundamental\b': ('Fundamental', 'The underlying financial health of a company (revenue, earnings, debt).'),
}

regexes = {re.compile(k): v for k, v in glossary.items()}

def is_inside_has_tip(node):
    p = node.parent
    while p:
        if p.name == 'span' and p.get('class') and 'has-tip' in p.get('class'):
            return True
        # Also skip anything inside links (a tags) or buttons to prevent breaking UI
        if p.name in ['a', 'button']:
            return True
        p = p.parent
    return False

def process_text_node(node, soup):
    text = str(node)
    if not text.strip():
        return False
        
    if is_inside_has_tip(node):
        return False

    nodes = [NavigableString(text)]
    modified = False
    
    for regex, (term, definition) in regexes.items():
        new_nodes = []
        for n in nodes:
            if isinstance(n, NavigableString):
                s = str(n)
                last_idx = 0
                for match in regex.finditer(s):
                    modified = True
                    if match.start() > last_idx:
                        new_nodes.append(NavigableString(s[last_idx:match.start()]))
                        
                    span = soup.new_tag("span", attrs={"class": "has-tip"})
                    span.string = match.group(0) # Preserve original casing
                    
                    tip_box = soup.new_tag("span", attrs={"class": "tip-box"})
                    tip_box.string = definition
                    span.append(tip_box)
                    
                    new_nodes.append(span)
                    last_idx = match.end()
                    
                if last_idx < len(s):
                    new_nodes.append(NavigableString(s[last_idx:]))
            else:
                new_nodes.append(n)
        nodes = new_nodes
        
    if modified:
        # replace the original node with multiple nodes
        parent = node.parent
        idx = parent.contents.index(node)
        node.extract()
        for i, new_node in enumerate(nodes):
            parent.insert(idx + i, new_node)
        return True
    return False

for file in glob.glob('*.html'):
    try:
        with open(file, 'r', encoding='utf-8') as f:
            html = f.read()
            
        soup = BeautifulSoup(html, 'html.parser')
        text_nodes = soup.find_all(string=True)
        
        changed = False
        for node in text_nodes:
            if node.parent and node.parent.name in ['script', 'style', 'head', 'title', 'meta']:
                continue
            if process_text_node(node, soup):
                changed = True
                
        if changed:
            with open(file, 'w', encoding='utf-8') as f:
                # Use formatter='html' to prevent bs4 from mangling some tags
                f.write(soup.encode(formatter='html').decode('utf-8'))
            print(f"Updated {file}")
    except Exception as e:
        print(f"Failed to process {file}: {e}")
