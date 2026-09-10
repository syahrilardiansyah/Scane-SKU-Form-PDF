import fitz
import sys
sys.path.insert(0, r'D:\Project\Rekap_SKU_PDF')
from app.bigseller_parser import parse_bigseller

doc = fitz.open(r'D:\Project\Rekap_SKU_PDF\file\Shopee WF 10 Sept 2026.pdf')
full_text = ''
for page in doc:
    full_text += page.get_text()

raw = parse_bigseller(full_text)

print('=== RAW BUNDLES (before split) ===')
for item in raw:
    sku = item["sku"]
    if "+" in sku:
        print(f'  {sku:40s} — {item["qty"]}')

print()
print('=== ALL RAW SKUs ===')
for item in raw:
    print(f'  {item["sku"]:40s} — {item["qty"]}')
