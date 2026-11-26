import json
import csv
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PRODUCTS_FILE = os.path.join(BASE_DIR, 'data', 'products.json')
CSV_FILE = os.path.join(BASE_DIR, 'woocommerce_products_import.csv')

with open(PRODUCTS_FILE, 'r', encoding='utf-8') as f:
    products = json.load(f)

fields = [
    "ID", "Type", "SKU", "Name", "Published", "Is featured?",
    "Visibility in catalog", "Short description", "Description",
    "Tax status", "In stock?", "Stock", "Regular price", "Categories", "Images"
]

with open(CSV_FILE, 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(fields)
    
    for p in products:
        cat_hierarchy = f"{p['category']} > {p.get('subcategory', '')}" if p.get('subcategory') else p['category']
        
        # Build description including available package sizes
        desc = p.get('description', '')
        if p.get('variations') and len(p['variations']) > 1:
            sizes_str = ", ".join([f"{v['size']} ({v['price']:.2f} RON)" for v in p['variations']])
            desc += f"<br><br><strong>Kiszerelések / Ambalaje disponibile:</strong> {sizes_str}"
            
        writer.writerow([
            p['id'],
            "simple",
            f"TD-{p['id']}",
            p['name'],
            1, # Published
            1 if p.get('featured') else 0,
            "visible",
            p.get('description', '')[:120] + "...",
            desc,
            "taxable",
            1, # In stock
            sum(v.get('stock', 25) for v in p.get('variations', [{'stock': 25}])),
            f"{p.get('price', 0.0):.2f}",
            cat_hierarchy,
            p.get('image', '')
        ])

print(f"Generated WooCommerce CSV import with {len(products)} products at {CSV_FILE}!")
