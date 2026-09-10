import fitz
import sys
sys.path.insert(0, r'D:\Project\Rekap_SKU_PDF')
from app.bigseller_parser import parse_bigseller_full

doc = fitz.open(r'D:\Project\Rekap_SKU_PDF\file\shp fc today.pdf')
full_text = ''
for page in doc:
    full_text += page.get_text()

results = parse_bigseller_full(full_text)

print('=== HASIL PARSER ===')
for i, item in enumerate(results, 1):
    sku = item["sku"]
    qty = item["qty"]
    print(f'{i:2d}. {sku:25s} — {qty}')
print(f'\nTotal: {len(results)} SKU')
print(f'Grand total: {sum(r["qty"] for r in results)}')
