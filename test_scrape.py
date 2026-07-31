import requests
from bs4 import BeautifulSoup

url = "https://sarmaaya.pk/psx/company/SYS"
headers = {'User-Agent': 'Mozilla/5.0'}
res = requests.get(url, headers=headers)
soup = BeautifulSoup(res.text, 'html.parser')

print("Looking for sector...")
sector_elem = soup.find('a', href=lambda href: href and '/psx/sector/' in href)
print(sector_elem.text if sector_elem else "Not found")

print("Looking for PE...")
# Try to find PE ratio
for div in soup.find_all('div'):
    text = div.get_text().upper()
    if 'P/E' in text or 'PE RATIO' in text:
        print(text.strip().replace('\n', ' '))
