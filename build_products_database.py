import json
import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_IMG_DIR = os.path.join(BASE_DIR, 'static', 'images', 'products')
SCRAPED_FILE = os.path.join(BASE_DIR, 'products_scraped.json')
OUTPUT_FILE = os.path.join(BASE_DIR, 'data', 'products.json')

os.makedirs(os.path.join(BASE_DIR, 'data'), exist_ok=True)
os.makedirs(STATIC_IMG_DIR, exist_ok=True)

with open(SCRAPED_FILE, 'r', encoding='utf-8-sig') as f:
    scraped = json.load(f)

# Helper to find if an image exists locally
def get_existing_image(slug, ext):
    path = os.path.join(STATIC_IMG_DIR, f"{slug}{ext}")
    if os.path.exists(path):
        return f"/static/images/products/{slug}{ext}"
    for e in ['.png', '.jpg', '.jpeg', '.webp']:
        test_path = os.path.join(STATIC_IMG_DIR, f"{slug}{e}")
        if os.path.exists(test_path):
            return f"/static/images/products/{slug}{e}"
    return None

# Parse prices
def clean_price(price_str, default_price=15.00):
    if not price_str:
        return default_price
    # Format e.g. "3.10&nbsp;lei" or "24,07 lei"
    cleaned = price_str.replace('&nbsp;', ' ').replace('lei', '').replace('LEI', '').strip()
    # If range like "10.00 – 25.00"
    if '–' in cleaned or '-' in cleaned:
        cleaned = re.split(r'[–-]', cleaned)[0].strip()
    cleaned = cleaned.replace(',', '.')
    match = re.search(r'([0-9]+\.?[0-9]*)', cleaned)
    if match:
        try:
            val = float(match.group(1))
            return val if val > 0 else default_price
        except ValueError:
            return default_price
    return default_price

products = []
id_counter = 1

# Process scraped products
for item in scraped:
    raw_cat = item.get('Category', '')
    title = item.get('Title', '').strip()
    if not title:
        continue

    # Determine main category and subcategory
    cat = "Decoratiuni"
    subcat = "Accesorii"
    default_price = 19.99

    if "pamant" in raw_cat.lower() or "substrat" in title.lower() or "pamant" in title.lower() or "turba" in title.lower():
        cat = "Pamant de Flori"
        if "universal" in title.lower():
            subcat = "Substrat Universal"
            default_price = 14.50
        elif "orhide" in title.lower():
            subcat = "Substrat Orhidee"
            default_price = 22.00
        elif "conifer" in title.lower() or "acid" in title.lower():
            subcat = "Substrat Acidofil & Conifere"
            default_price = 18.00
        elif "balcon" in title.lower() or "muscat" in title.lower():
            subcat = "Substrat Mușcate & Balcon"
            default_price = 16.00
        elif "camera" in title.lower():
            subcat = "Substrat Plante de Cameră"
            default_price = 12.00
        else:
            subcat = "Turbă și Substraturi Speciale"
            default_price = 15.00

    elif "ingrasaminte" in raw_cat.lower() or "solutii" in raw_cat.lower() or "fertilizant" in title.lower() or "vitaflora" in title.lower() or "florasol" in title.lower() and "pamant" not in title.lower():
        cat = "Ingrasaminte"
        if "lichid" in raw_cat.lower() or "solutie" in title.lower() or "1l" in title.lower() or "500ml" in title.lower():
            subcat = "Lichide - Solutii Nutritive"
            default_price = 18.50
        else:
            subcat = "Solide"
            default_price = 15.00

    elif "ingrijire" in raw_cat.lower() or "protectie" in title.lower() or "insecticid" in title.lower():
        cat = "Produse de Ingrijire plante"
        subcat = "Protecție & Tratamente Plante"
        default_price = 24.50

    elif "ghivece" in raw_cat.lower() or "ghiveci" in title.lower() or "jardiniera" in title.lower():
        cat = "Ghivece"
        subcat = "Ghivece Decorative & Jardiniere"
        default_price = 28.00

    elif "decoratiun" in raw_cat.lower() or "diverse" in raw_cat.lower():
        cat = "Decoratiuni"
        if "toamna" in title.lower():
            subcat = "Decorațiuni de Toamnă"
            default_price = 14.00
        elif "figurina" in title.lower() or "miri" in title.lower() or "broasca" in title.lower() or "ciuperca" in title.lower():
            subcat = "Figurine de Grădină"
            default_price = 16.50
        else:
            subcat = "Decorațiuni Grădină & Casă"
            default_price = 18.00

    # Image resolution
    raw_img = item.get('Image', '')
    slug = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')[:40]
    ext = os.path.splitext(raw_img.split('?')[0])[1] if raw_img else '.jpg'
    if not ext:
        ext = '.jpg'

    local_img = get_existing_image(slug, ext)
    if not local_img:
        # Fallback to general category image or first available in folder
        local_img = "/static/images/products/pamant-de-flori-universal-plantasol-5l.png"

    price = clean_price(item.get('Price', ''), default_price)

    # Generate rich description in Romanian
    if cat == "Pamant de Flori":
        desc = f"{title} este un substrat profesional de calitate superioară, bogat în nutrienți esențiali, ideal pentru dezvoltarea armonioasă a sistemului radicular și stimularea unei creșteri viguroase a plantelor."
    elif cat == "Ingrasaminte":
        desc = f"{title} asigură o nutriție completă și echilibrată cu macro și microelemente chelatizate, favorizând o înflorire abundentă, un frunziș viguros și rezistență sporită împotriva factorilor de stres."
    elif cat == "Produse de Ingrijire plante":
        desc = f"{title} oferă o protecție eficientă și de lungă durată împotriva dăunătorilor și bolilor comune, menținând plantele sănătoase, revitalizate și pline de vitalitate."
    elif cat == "Ghivece":
        desc = f"{title} combină designul modern și elegant cu durabilitatea materialelor de înaltă calitate, asigurând un drenaj optim și un aspect estetic deosebit pentru interior sau terasă."
    else:
        desc = f"{title} aduce un plus de farmec și originalitate grădinii, balconului sau locuinței dumneavoastră, fiind realizat din materiale rezistente și finisat cu atenție la detalii."

    products.append({
        "id": id_counter,
        "name": title,
        "sku": f"TD-{cat[:2].upper()}-{100 + id_counter}",
        "category": cat,
        "subcategory": subcat,
        "price": round(price, 2),
        "currency": "RON",
        "stock": 35,
        "image": local_img,
        "description": desc,
        "featured": id_counter <= 8,
        "rating": round(4.5 + (id_counter % 5) * 0.1, 1),
        "reviews_count": 8 + (id_counter % 23)
    })
    id_counter += 1

# Also add special items from local images for Solid Fertilizers and Ghivece SK
solid_fertilizers = [
    {
        "id": id_counter,
        "name": "Batoane nutritive Vitaflora pentru plante cu flori",
        "sku": f"TD-IN-{100 + id_counter}",
        "category": "Ingrasaminte",
        "subcategory": "Solide",
        "price": 12.50,
        "currency": "RON",
        "stock": 50,
        "image": "/static/images/products/batoane-nutritive-plante-flori.png",
        "description": "Batoane nutritive solide cu eliberare lentă timp de 2 luni. Stimulează formarea bobocilor și o înflorire spectaculoasă și îndelungată.",
        "featured": True,
        "rating": 4.9,
        "reviews_count": 34
    },
    {
        "id": id_counter + 1,
        "name": "Batoane nutritive Vitaflora speciale pentru orhidee",
        "sku": f"TD-IN-{100 + id_counter + 1}",
        "category": "Ingrasaminte",
        "subcategory": "Solide",
        "price": 14.00,
        "currency": "RON",
        "stock": 45,
        "image": "/static/images/products/batoane-nutritive-orhidee.png",
        "description": "Formulă solidă special concepută pentru orhidee. Hrănește rădăcinile aeriene și stimulează reînflorirea periodică a orhideelor Phalaenopsis și Dendrobium.",
        "featured": True,
        "rating": 4.9,
        "reviews_count": 28
    },
    {
        "id": id_counter + 2,
        "name": "Batoane nutritive Vitaflora pentru plante decorative prin frunze",
        "sku": f"TD-IN-{100 + id_counter + 2}",
        "category": "Ingrasaminte",
        "subcategory": "Solide",
        "price": 12.50,
        "currency": "RON",
        "stock": 60,
        "image": "/static/images/products/batoane-nutritive-plante-verzi.png",
        "description": "Îngrășământ solid sub formă de batoane cu conținut ridicat de azot și magneziu, prevenind îngălbenirea frunzelor și intensificând culoarea verde a plantelor.",
        "featured": False,
        "rating": 4.8,
        "reviews_count": 19
    }
]
id_counter += 3
products.extend(solid_fertilizers)

pots_sk = [
    {
        "id": id_counter,
        "name": "Ghiveci ceramic SK Premium Antracit Ø 22cm",
        "sku": f"TD-GH-{100 + id_counter}",
        "category": "Ghivece",
        "subcategory": "Ghivece Decorative & Jardiniere",
        "price": 38.00,
        "currency": "RON",
        "stock": 20,
        "image": "/static/images/products/ghiveci-ceramic-sk-premium-antracit.jpg",
        "description": "Ghiveci ceramic de calitate premium, finisaj mat antracit, rezistent la îngheț și raze UV. Ideal pentru plante de interior și terase moderne.",
        "featured": True,
        "rating": 4.9,
        "reviews_count": 15
    },
    {
        "id": id_counter + 1,
        "name": "Ghiveci decorativ SK Alb Marmurat Ø 18cm",
        "sku": f"TD-GH-{100 + id_counter + 1}",
        "category": "Ghivece",
        "subcategory": "Ghivece Decorative & Jardiniere",
        "price": 29.50,
        "currency": "RON",
        "stock": 25,
        "image": "/static/images/products/ghiveci-decorativ-sk-alb-marmurat.jpg",
        "description": "Ghiveci cu textură elegantă alb marmurat, adăugând o notă sofisticată oricărui living sau birou.",
        "featured": False,
        "rating": 4.7,
        "reviews_count": 12
    },
    {
        "id": id_counter + 2,
        "name": "Jardinieră balcon SK Teracotă Clasic 40cm",
        "sku": f"TD-GH-{100 + id_counter + 2}",
        "category": "Ghivece",
        "subcategory": "Ghivece Decorative & Jardiniere",
        "price": 34.00,
        "currency": "RON",
        "stock": 30,
        "image": "/static/images/products/jardiniera-balcon-sk-teracota.jpg",
        "description": "Jardinieră rezistentă cu suport pentru balcon și terasă, nuanță caldă de teracotă, prevăzută cu sistem integrat de colectare a apei.",
        "featured": False,
        "rating": 4.8,
        "reviews_count": 22
    },
    {
        "id": id_counter + 3,
        "name": "Ghiveci suspendat SK Modern cu agățătoare",
        "sku": f"TD-GH-{100 + id_counter + 3}",
        "category": "Ghivece",
        "subcategory": "Ghivece Decorative & Jardiniere",
        "price": 32.00,
        "currency": "RON",
        "stock": 18,
        "image": "/static/images/products/ghiveci-suspendat-sk-modern.jpg",
        "description": "Ghiveci suspendat ideal pentru petunii curgătoare, ferigi și plante de balcon, ușor și foarte rezistent.",
        "featured": True,
        "rating": 4.8,
        "reviews_count": 17
    },
    {
        "id": id_counter + 4,
        "name": "Ghiveci rotund SK Gri Satinat Ø 26cm",
        "sku": f"TD-GH-{100 + id_counter + 4}",
        "category": "Ghivece",
        "subcategory": "Ghivece Decorative & Jardiniere",
        "price": 42.00,
        "currency": "RON",
        "stock": 15,
        "image": "/static/images/products/ghiveci-rotund-sk-gri-satinat.jpg",
        "description": "Ghiveci generos pentru palmieri, ficuși și arbuști decorativi, cu farfurie detașabilă inclusă.",
        "featured": False,
        "rating": 4.9,
        "reviews_count": 24
    }
]
id_counter += 5
products.extend(pots_sk)

with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    json.dump(products, f, ensure_ascii=False, indent=2)

print(f"Successfully generated database with {len(products)} products in {OUTPUT_FILE}!")
