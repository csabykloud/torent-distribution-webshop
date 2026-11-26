import json
from collections import Counter

with open('data/products.json', 'r', encoding='utf-8') as f:
    products = json.load(f)

print(f"Total products: {len(products)}")
cats = Counter(p['category'] for p in products)
for c, count in cats.items():
    print(f"  {c}: {count}")

print("\n=== PĂMÂNT DE FLORI ===")
for p in products:
    if p['category'] == 'Pamant de Flori':
        print(f"ID {p['id']}: {p['name']} -> subcat: {p.get('subcategory')}, price: {p.get('price')}, img: {p.get('image')}")

print("\n=== ÎNGRĂȘĂMINTE ===")
for p in products:
    if p['category'] == 'Ingrasaminte':
        print(f"ID {p['id']}: {p['name']} -> subcat: {p.get('subcategory')}, price: {p.get('price')}, img: {p.get('image')}")
