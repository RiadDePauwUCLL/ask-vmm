from pypdf import PdfReader
from pathlib import Path

for name in ['luchtkwaliteitsmeetcampagne_2021.pdf', 'gemeenschappelijke_maas_waterkwaliteit.pdf']:
    print('===', name)
    path = Path('data/reports') / name
    reader = PdfReader(str(path))
    for i, page in enumerate(reader.pages[:3], start=1):
        txt = (page.extract_text() or '')[:1500]
        print(f'--- PAGE {i} ---\n{txt}\n')
