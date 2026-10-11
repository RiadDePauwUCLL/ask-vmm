import requests
from bs4 import BeautifulSoup

for query in ['waterkwaliteit', 'luchtkwaliteit', 'milieurapport', 'klimaatadaptatie']:
    url = f'https://www.vmm.be/search?SearchableText={query}'
    print('\n=== QUERY:', query, '===')
    r = requests.get(url, timeout=20)
    print('status', r.status_code, 'final_url', r.url)
    soup = BeautifulSoup(r.text, 'html.parser')
    seen = set()
    matches = 0
    for a in soup.select('a[href]'):
        href = a.get('href')
        text = a.get_text(' ', strip=True)
        if href and (href.startswith('/') or 'vmm.be' in href):
            if text and href not in seen and len(text) > 2:
                seen.add(href)
                print(href, '::', text[:200])
                matches += 1
                if matches >= 20:
                    break
    if matches == 0:
        print('No results found in parsed HTML')
