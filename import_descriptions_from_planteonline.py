import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TORENT_PRODUCTS_FILE = os.path.join(BASE_DIR, 'data', 'products.json')
PLANTE_ONLINE_PRODUCTS_FILE = r"D:\Antigravity\Plante online\data\products.json"

with open(TORENT_PRODUCTS_FILE, 'r', encoding='utf-8') as f:
    torent_products = json.load(f)

with open(PLANTE_ONLINE_PRODUCTS_FILE, 'r', encoding='utf-8') as f:
    po_products = json.load(f)

po_by_id = {p['id']: p for p in po_products}

# Mapping: Torent Distribution product ID -> Plante Online product ID
mapping = {
    # Pamant de Flori
    1: 20,  # Pământ de flori universal Plantasol
    2: 4,   # Pământ de flori universal Florasol
    3: 7,   # Pământ de flori universal Humiflor
    4: 11,  # Substrat de orhidee Humiflor
    5: 18,  # Nutrisol pământ de flori pentru plante de cameră
    6: 19,  # Nutrisol pământ pentru plante de grădină și straturi înălțate
    7: 12,  # Nutrisol pământ de flori pentru mușcate și plante de balcon

    # Ingrasaminte - Vitaflora
    13: 30, # Vitaflora 1 Pt. plante cu flori
    14: 31, # Vitaflora 2 Pt. plante cu frunze
    15: 23, # Vitaflora 3 Universal
    16: 32, # Vitaflora 5 Pt. stimularea înfloririi
    17: 28, # Vitaflora 6 Pt. mușcate
    18: 27, # Vitaflora 7 Pt. gazon
    19: 24, # Vitaflora 8 Pt. cactuși
    20: 29, # Vitaflora Pt. orhidee
    23: 22, # Vitaflora Pt. Plante curgătoare
    24: 26, # Vitaflora Pt. conifere
    25: 25, # Vitaflora Pt. legume

    # Ingrasaminte - Florasol
    26: 6,  # Florasol Universal
    27: 5,  # Florasol Pt. mușcate

    # Ingrasaminte - Humiflor
    28: 8,  # Humiflor pentru plante de balcon 1L
    29: 10, # Humiflor pentru plante de gradina 1L
    30: 9,  # Humiflor pentru plante de camera 1L

    # Ingrasaminte - Solide (Batoane)
    31: 2,  # Vitaflora Pt. plante cu flori (Batoane)
    32: 3,  # Vitaflora Pt. plante cu frunze (Batoane)
    33: 1,  # Vitaflora Pt. orhidee (Batoane)

    # Produse de Ingrijire plante
    34: 33, # Florasol Solutie Ecologica Ingrijire plante 0.5L
    35: 16, # Nutrisol- solutie ecologica de ingrijire plante 500ml
    36: 17, # Nutrisol- solutie organica de ingrijire plante 500ml
}

updated_count = 0
for tp in torent_products:
    tid = tp.get('id')
    if tid in mapping:
        po_id = mapping[tid]
        po_prod = po_by_id.get(po_id)
        if po_prod and po_prod.get('description'):
            tp['description'] = po_prod['description'].strip()
            updated_count += 1
            print(f"Updated ID {tid} ({tp['name']}) <- PO ID {po_id} ({len(tp['description'])} chars)")

with open(TORENT_PRODUCTS_FILE, 'w', encoding='utf-8') as f:
    json.dump(torent_products, f, ensure_ascii=False, indent=2)

print(f"\nSUCCESS: Updated {updated_count} product descriptions from Plante online!")
