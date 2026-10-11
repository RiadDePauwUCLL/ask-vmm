import requests, re
from bs4 import BeautifulSoup

url = 'https://www.vmm.be/'
r = requests.get(url, timeout=20)
print('status', r.status_code)
text = r.text
print('len', len(text))
# Output selected interesting fragments
for pat in ['publicaties', 'download', 'pdf', '/Plone/', 'milieurapport', 'water', 'lucht']:
    idx = text.lower().find(pat.lower())
    if idx != -1:
        print('\nPATTERN:', pat)
        start = max(0, idx - 300)
        end = min(len(text), idx + 600)
        snippet = text[start:end]
        print(snippet)
        print('\n--- END SNIPPET ---\n')

soup = BeautifulSoup(text, 'html.parser')
for tag in soup.find_all(['a', 'script', 'link']):
    text_attr = tag.get('href') or tag.get('src') or tag.get('content') or ''
    if 'publicaties' in text_attr or '.pdf' in text_attr or 'download' in text_attr or 'Plone' in text_attr:
        print('MATCH', tag.name, text_attr)
