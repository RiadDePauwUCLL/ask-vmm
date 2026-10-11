from pathlib import Path
from pypdf import PdfReader

root = Path('data/reports')
for path in sorted(root.glob('*.pdf')):
    print('\n===', path.name, '===')
    try:
        reader = PdfReader(str(path))
        for i, page in enumerate(reader.pages[:3], start=1):
            txt = (page.extract_text() or '')[:1800]
            print(f'--- PAGE {i} ---\n{txt[:1200]}\n')
    except Exception as exc:
        print('ERROR', exc)
