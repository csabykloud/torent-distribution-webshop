import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OLD_PRODUCTS_FILE = os.path.join(BASE_DIR, 'data', 'products.json')
OUTPUT_FILE = os.path.join(BASE_DIR, 'data', 'products.json')

with open(OLD_PRODUCTS_FILE, 'r', encoding='utf-8') as f:
    old_products = json.load(f)

unified_products = []
new_id = 1

# 1. PĂMÂNT DE FLORI (Subcategories: Florasol, Humiflor, Nutrisol, Plantasol, Florimo)
soils = [
    # PLANTASOL
    {
        "id": new_id,
        "name": "Pământ de flori universal Plantasol",
        "category": "Pamant de Flori",
        "subcategory": "Plantasol",
        "image": "/static/images/products/pamant-de-flori-universal-plantasol-5l.png",
        "description": "Substrat profesional universal Plantasol pe bază de turbă de calitate superioară, îmbogățit cu nutrienți esențiali pentru toate tipurile de plante decorative, de grădină sau de balcon. Asigură o structură aerată a solului, o dezvoltare viguroasă a rădăcinilor și o retenție optimă a apei.",
        "featured": True,
        "rating": 4.9,
        "reviews_count": 48,
        "variations": [
            {"size": "5L", "price": 3.10, "stock": 60, "sku": "PL-UNI-5L"},
            {"size": "10L", "price": 5.80, "stock": 50, "sku": "PL-UNI-10L"},
            {"size": "20L", "price": 11.00, "stock": 45, "sku": "PL-UNI-20L"},
            {"size": "50L", "price": 24.50, "stock": 30, "sku": "PL-UNI-50L"}
        ],
        "default_size": "5L",
        "price": 3.10
    },
    # FLORASOL
    {
        "id": new_id + 1,
        "name": "Pământ de flori universal Florasol",
        "category": "Pamant de Flori",
        "subcategory": "Florasol",
        "image": "/static/images/products/florasol-pamant-de-flori-universal.png",
        "description": "Substrat nutritiv complet Florasol îmbogățit cu humus activ și microelemente chelatizate. Ideal pentru replantarea și întreținerea plantelor de interior și a florilor de balcon, stimulând o înflorire abundentă și culori intense.",
        "featured": True,
        "rating": 4.8,
        "reviews_count": 36,
        "variations": [
            {"size": "5L", "price": 3.50, "stock": 40, "sku": "FL-UNI-5L"},
            {"size": "10L", "price": 6.50, "stock": 35, "sku": "FL-UNI-10L"},
            {"size": "20L", "price": 12.00, "stock": 30, "sku": "FL-UNI-20L"},
            {"size": "50L", "price": 26.00, "stock": 25, "sku": "FL-UNI-50L"}
        ],
        "default_size": "5L",
        "price": 3.50
    },
    # HUMIFLOR
    {
        "id": new_id + 2,
        "name": "Pământ de flori universal Humiflor",
        "category": "Pamant de Flori",
        "subcategory": "Humiflor",
        "image": "/static/images/products/pamant-de-flori-universal-humiflor.jpg",
        "description": "Pământ de flori nutritiv Humiflor cu adaos de humus natural de râmă și turbă fină selecționată. Recomandat pentru flori de apartament, jardiniere și ronduri de grădină, favorizând dezvoltarea rapidă a noilor lăstari.",
        "featured": True,
        "rating": 4.8,
        "reviews_count": 42,
        "variations": [
            {"size": "5L", "price": 3.30, "stock": 50, "sku": "HU-UNI-5L"},
            {"size": "10L", "price": 6.20, "stock": 45, "sku": "HU-UNI-10L"},
            {"size": "20L", "price": 11.80, "stock": 40, "sku": "HU-UNI-20L"},
            {"size": "50L", "price": 25.00, "stock": 20, "sku": "HU-UNI-50L"}
        ],
        "default_size": "5L",
        "price": 3.30
    },
    {
        "id": new_id + 3,
        "name": "Substrat special pentru orhidee Humiflor",
        "category": "Pamant de Flori",
        "subcategory": "Humiflor",
        "image": "/static/images/products/substrat-de-orhidee-humiflor-5l.jpg",
        "description": "Substrat profesional aerat conceput special pentru orhidee epifite (Phalaenopsis, Vanda, Dendrobium). Conține bucăți selecționate de scoarță de pin mediteranean și turbă fibroasă pentru a asigura oxigenarea rădăcinilor aeriene.",
        "featured": False,
        "rating": 4.9,
        "reviews_count": 27,
        "variations": [
            {"size": "3L", "price": 9.50, "stock": 35, "sku": "HU-ORH-3L"},
            {"size": "5L", "price": 13.50, "stock": 40, "sku": "HU-ORH-5L"}
        ],
        "default_size": "5L",
        "price": 13.50
    },
    # NUTRISOL
    {
        "id": new_id + 4,
        "name": "Pământ de flori pentru plante de cameră Nutrisol",
        "category": "Pamant de Flori",
        "subcategory": "Nutrisol",
        "image": "/static/images/products/nutrisol-substrat-plante-de-camera-10l.jpg",
        "description": "Substrat echilibrat Nutrisol pentru plante verzi și cu flori de interior (ficus, monstera, dracaena, violete africane). Are o permeabilitate excelentă și previne compactarea sau putrezirea rădăcinilor.",
        "featured": True,
        "rating": 4.9,
        "reviews_count": 31,
        "variations": [
            {"size": "5L", "price": 4.80, "stock": 40, "sku": "NU-CAM-5L"},
            {"size": "10L", "price": 8.00, "stock": 50, "sku": "NU-CAM-10L"},
            {"size": "20L", "price": 14.50, "stock": 30, "sku": "NU-CAM-20L"}
        ],
        "default_size": "10L",
        "price": 8.00
    },
    {
        "id": new_id + 5,
        "name": "Pământ de flori pentru mușcate și plante de balcon Nutrisol",
        "category": "Pamant de Flori",
        "subcategory": "Nutrisol",
        "image": "/static/images/products/nutrisol-pamant-de-flori-plante-de-balco.jpg",
        "description": "Formulă specializată cu eliberare prelungită de nutrienți, ideală pentru mușcate zonale și curgătoare, petunii, surfinia și begonia. Garantează o înflorire spectaculoasă până toamna târziu.",
        "featured": False,
        "rating": 4.8,
        "reviews_count": 29,
        "variations": [
            {"size": "10L", "price": 7.50, "stock": 45, "sku": "NU-BAL-10L"},
            {"size": "20L", "price": 13.00, "stock": 40, "sku": "NU-BAL-20L"},
            {"size": "50L", "price": 27.50, "stock": 25, "sku": "NU-BAL-50L"}
        ],
        "default_size": "20L",
        "price": 13.00
    },
    {
        "id": new_id + 6,
        "name": "Substrat nutritiv pentru straturi înălțate Nutrisol",
        "category": "Pamant de Flori",
        "subcategory": "Nutrisol",
        "image": "/static/images/products/nutrisol-substrat-straturi-inaltate-20l.jpg",
        "description": "Substrat profesional bogat în compost organic și materie organică humică, special adaptat pentru cutii de cultivare, legume de grădină, căpșuni și plante aromatice.",
        "featured": False,
        "rating": 4.8,
        "reviews_count": 22,
        "variations": [
            {"size": "20L", "price": 13.00, "stock": 35, "sku": "NU-INA-20L"},
            {"size": "50L", "price": 28.00, "stock": 30, "sku": "NU-INA-50L"}
        ],
        "default_size": "20L",
        "price": 13.00
    },
    # FLORIMO
    {
        "id": new_id + 7,
        "name": "Pământ de flori universal Florimo",
        "category": "Pamant de Flori",
        "subcategory": "Florimo",
        "image": "/static/images/products/florimo-pamant-de-flori-universal.png",
        "description": "Substrat premium Florimo recunoscut internațional, compus din amestec de turbă albă și neagră de sphagnum, perlit și îngrășământ starter PG-Mix cu oligoelemente.",
        "featured": True,
        "rating": 5.0,
        "reviews_count": 55,
        "variations": [
            {"size": "3L", "price": 4.20, "stock": 40, "sku": "FO-UNI-3L"},
            {"size": "10L", "price": 8.50, "stock": 45, "sku": "FO-UNI-10L"},
            {"size": "20L", "price": 15.50, "stock": 40, "sku": "FO-UNI-20L"},
            {"size": "50L", "price": 32.00, "stock": 35, "sku": "FO-UNI-50L"}
        ],
        "default_size": "10L",
        "price": 8.50
    },
    {
        "id": new_id + 8,
        "name": "Pământ de flori acidofil Florimo (pH 4.0 - 5.0)",
        "category": "Pamant de Flori",
        "subcategory": "Florimo",
        "image": "/static/images/products/florimo-pamant-de-flori-acidulos.png",
        "description": "Substrat acidofil special creat pentru plante care necesită aciditate pronunțată: rododendroni, azalee, hortensii albastre, magnolii, erica și afini de cultură.",
        "featured": False,
        "rating": 4.9,
        "reviews_count": 33,
        "variations": [
            {"size": "10L", "price": 9.80, "stock": 35, "sku": "FO-ACI-10L"},
            {"size": "20L", "price": 18.00, "stock": 30, "sku": "FO-ACI-20L"},
            {"size": "50L", "price": 36.00, "stock": 20, "sku": "FO-ACI-50L"}
        ],
        "default_size": "20L",
        "price": 18.00
    },
    {
        "id": new_id + 9,
        "name": "Pământ de flori pentru mușcate Florimo",
        "category": "Pamant de Flori",
        "subcategory": "Florimo",
        "image": "/static/images/products/florimo-pamant-de-flori-de-muscate.png",
        "description": "Substrat structurat cu argilă minerală și conținut ridicat de potasiu, care stochează apa și nutrienții, reducând frecvența udărilor în perioadele caniculare.",
        "featured": False,
        "rating": 4.9,
        "reviews_count": 38,
        "variations": [
            {"size": "10L", "price": 9.00, "stock": 40, "sku": "FO-MUS-10L"},
            {"size": "20L", "price": 16.00, "stock": 35, "sku": "FO-MUS-20L"},
            {"size": "50L", "price": 34.00, "stock": 25, "sku": "FO-MUS-50L"}
        ],
        "default_size": "20L",
        "price": 16.00
    },
    {
        "id": new_id + 10,
        "name": "Substrat special pentru conifere Florimo",
        "category": "Pamant de Flori",
        "subcategory": "Florimo",
        "image": "/static/images/products/florimo-substrat-de-conifere.png",
        "description": "Amestec cu pH mediu-acid îmbogățit cu magneziu și fier, prevenind brunificarea și căderea acelor la tuia, molid, brad argintiu, ienupăr și chiparos.",
        "featured": False,
        "rating": 4.8,
        "reviews_count": 29,
        "variations": [
            {"size": "20L", "price": 18.00, "stock": 35, "sku": "FO-CON-20L"},
            {"size": "50L", "price": 36.00, "stock": 30, "sku": "FO-CON-50L"}
        ],
        "default_size": "20L",
        "price": 18.00
    },
    {
        "id": new_id + 11,
        "name": "Substrat special pentru orhidee Florimo",
        "category": "Pamant de Flori",
        "subcategory": "Florimo",
        "image": "/static/images/products/substrat-de-orhidee-florimo-3l.png",
        "description": "Scoarță nobilă calibrată și cărbune vegetal pentru prevenirea mucegaiului și stimularea reînfloririi spectaculoase a orhideelor.",
        "featured": False,
        "rating": 4.9,
        "reviews_count": 41,
        "variations": [
            {"size": "3L", "price": 24.07, "stock": 40, "sku": "FO-ORH-3L"}
        ],
        "default_size": "3L",
        "price": 24.07
    }
]

unified_products.extend(soils)
new_id += len(soils)

# 2. ÎNGRĂȘĂMINTE (Subcategories: Vitaflora, Florasol, Humiflor, Solide)
fertilizers = [
    # VITAFLORA LICHIDE
    {
        "id": new_id,
        "name": "Soluție nutritivă Vitaflora Universală",
        "category": "Ingrasaminte",
        "subcategory": "Vitaflora",
        "image": "/static/images/products/vitaflora-solutie-nutritiva-universala.png",
        "description": "Îngrășământ lichid complet cu raport NPK echilibrat și microelemente chelatizate EDTA. Asigură o nutriție armonioasă pentru toate tipurile de plante de interior și exterior.",
        "featured": True,
        "rating": 4.9,
        "reviews_count": 47,
        "variations": [
            {"size": "500ml", "price": 11.50, "stock": 50, "sku": "VF-UNI-500"},
            {"size": "1L", "price": 18.50, "stock": 60, "sku": "VF-UNI-1L"}
        ],
        "default_size": "500ml",
        "price": 11.50
    },
    {
        "id": new_id + 1,
        "name": "Soluție nutritivă Vitaflora Plante cu Flori",
        "category": "Ingrasaminte",
        "subcategory": "Vitaflora",
        "image": "/static/images/products/vitaflora-solutie-nutritiva-plante-cu-fl.png",
        "description": "Formulă specializată cu conținut mărit de fosfor și potasiu pentru stimularea apariției bobocilor florali și prelungirea duratei de înflorire a plantelor.",
        "featured": True,
        "rating": 4.9,
        "reviews_count": 52,
        "variations": [
            {"size": "500ml", "price": 11.50, "stock": 45, "sku": "VF-FLO-500"},
            {"size": "1L", "price": 18.50, "stock": 55, "sku": "VF-FLO-1L"}
        ],
        "default_size": "500ml",
        "price": 11.50
    },
    {
        "id": new_id + 2,
        "name": "Soluție nutritivă Vitaflora Plante cu Frunze Decorative",
        "category": "Ingrasaminte",
        "subcategory": "Vitaflora",
        "image": "/static/images/products/vitaflora-solutie-nutritiva-plante-cu-fr.png",
        "description": "Concentrat nutritiv bogat în azot organic și magneziu pentru stimularea fotosintezei, frunziș viguros și un verde proaspăt și strălucitor.",
        "featured": False,
        "rating": 4.8,
        "reviews_count": 34,
        "variations": [
            {"size": "500ml", "price": 11.50, "stock": 40, "sku": "VF-FRU-500"},
            {"size": "1L", "price": 18.50, "stock": 45, "sku": "VF-FRU-1L"}
        ],
        "default_size": "500ml",
        "price": 11.50
    },
    {
        "id": new_id + 3,
        "name": "Soluție nutritivă Vitaflora Mușcate și Plante de Balcon",
        "category": "Ingrasaminte",
        "subcategory": "Vitaflora",
        "image": "/static/images/products/vitaflora-solutie-nutritiva-muscate-si-p.png",
        "description": "Destinat mușcatelor curgătoare și drepte, petuniilor, verbenelor și altor flori de balcon expuse la soare intens. Asigură flori dense și rezistență la vânt și căldură.",
        "featured": True,
        "rating": 4.9,
        "reviews_count": 61,
        "variations": [
            {"size": "500ml", "price": 11.50, "stock": 50, "sku": "VF-MUS-500"},
            {"size": "1L", "price": 18.50, "stock": 65, "sku": "VF-MUS-1L"}
        ],
        "default_size": "500ml",
        "price": 11.50
    },
    {
        "id": new_id + 4,
        "name": "Soluție nutritivă Vitaflora Stimularea Înfloririi",
        "category": "Ingrasaminte",
        "subcategory": "Vitaflora",
        "image": "/static/images/products/vitaflora-solutie-nutritiva-stimularea-i.png",
        "description": "Tratament activator cu biostimulatori naturali care grăbește pornirea mugurilor florali la plantele reticente la înflorire.",
        "featured": False,
        "rating": 4.8,
        "reviews_count": 28,
        "variations": [
            {"size": "500ml", "price": 12.00, "stock": 35, "sku": "VF-STI-500"},
            {"size": "1L", "price": 19.50, "stock": 40, "sku": "VF-STI-1L"}
        ],
        "default_size": "500ml",
        "price": 12.00
    },
    {
        "id": new_id + 5,
        "name": "Soluție nutritivă Vitaflora Special Orhidee",
        "category": "Ingrasaminte",
        "subcategory": "Vitaflora",
        "image": "/static/images/products/vitaflora-solutie-nutritiva-orhidee.png",
        "description": "Formulă blândă cu salinitate redusă, protejând rădăcinile sensibile ale orhideelor și încurajând apariția tijelor florale noi.",
        "featured": True,
        "rating": 5.0,
        "reviews_count": 58,
        "variations": [
            {"size": "500ml", "price": 12.50, "stock": 45, "sku": "VF-ORH-500"},
            {"size": "1L", "price": 20.00, "stock": 35, "sku": "VF-ORH-1L"}
        ],
        "default_size": "500ml",
        "price": 12.50
    },
    {
        "id": new_id + 6,
        "name": "Soluție nutritivă Vitaflora Cactuși și Suculente",
        "category": "Ingrasaminte",
        "subcategory": "Vitaflora",
        "image": "/static/images/products/vitaflora-solutie-nutritiva-cactusi.png",
        "description": "Conținut scăzut de azot și optimizat în potasiu pentru a preveni crăparea țesuturilor suculente la cactuși, aloe și crassula.",
        "featured": False,
        "rating": 4.7,
        "reviews_count": 21,
        "variations": [
            {"size": "500ml", "price": 11.50, "stock": 30, "sku": "VF-CAC-500"}
        ],
        "default_size": "500ml",
        "price": 11.50
    },
    {
        "id": new_id + 7,
        "name": "Soluție nutritivă Vitaflora Plante Curgătoare",
        "category": "Ingrasaminte",
        "subcategory": "Vitaflora",
        "image": "/static/images/products/vitaflora-solutie-nutritiva-plante-curga.png",
        "description": "Nutriție intensivă pentru plante suspendate (iedere, surfinia, begonia pendula, fuchsia), menținând lăstarii lungi și viguroși.",
        "featured": False,
        "rating": 4.8,
        "reviews_count": 25,
        "variations": [
            {"size": "500ml", "price": 11.50, "stock": 35, "sku": "VF-CUR-500"},
            {"size": "1L", "price": 18.50, "stock": 40, "sku": "VF-CUR-1L"}
        ],
        "default_size": "500ml",
        "price": 11.50
    },
    {
        "id": new_id + 8,
        "name": "Soluție nutritivă Vitaflora Citrice și Plante Mediteraneene",
        "category": "Ingrasaminte",
        "subcategory": "Vitaflora",
        "image": "/static/images/products/vitaflora-solu-ie-nutritiv-pt-citrice-0-.png",
        "description": "Special pentru lămâi, portocali, mandarini, măslini și leandri, prevenind cloroza frunzelor prin conținutul generos de fier chelatizat.",
        "featured": False,
        "rating": 4.9,
        "reviews_count": 31,
        "variations": [
            {"size": "500ml", "price": 12.00, "stock": 30, "sku": "VF-CIT-500"}
        ],
        "default_size": "500ml",
        "price": 12.00
    },
    {
        "id": new_id + 9,
        "name": "Soluție nutritivă Vitaflora Gazon și Peluze 1L",
        "category": "Ingrasaminte",
        "subcategory": "Vitaflora",
        "image": "/static/images/products/vitaflora-solu-ie-nutritiv-pt-gazon-1l.png",
        "description": "Efect rapid de înverzire și îndesire a gazonului rezidențial, sporind rezistența la secetă și călcare.",
        "featured": False,
        "rating": 4.8,
        "reviews_count": 27,
        "variations": [
            {"size": "1L", "price": 17.00, "stock": 40, "sku": "VF-GAZ-1L"}
        ],
        "default_size": "1L",
        "price": 17.00
    },
    {
        "id": new_id + 10,
        "name": "Soluție nutritivă Vitaflora Conifere și Tuia 1L",
        "category": "Ingrasaminte",
        "subcategory": "Vitaflora",
        "image": "/static/images/products/vitaflora-solu-ie-nutritiv-pt-conifere-1.png",
        "description": "Asigură un frunziș persistent, dens și de un verde smarald, prevenind îngălbenirea acelor datorată carenței de magneziu.",
        "featured": False,
        "rating": 4.8,
        "reviews_count": 29,
        "variations": [
            {"size": "1L", "price": 17.00, "stock": 40, "sku": "VF-CON-1L"}
        ],
        "default_size": "1L",
        "price": 17.00
    },
    {
        "id": new_id + 11,
        "name": "Soluție nutritivă Vitaflora Legume și Căpșuni 1L",
        "category": "Ingrasaminte",
        "subcategory": "Vitaflora",
        "image": "/static/images/products/vitaflora-solu-ie-nutritiv-pt-legume-1l.png",
        "description": "Nutriție curată pentru roșii, ardei, castraveți și căpșuni, stimulând legarea florilor și coacerea fructelor gustoase.",
        "featured": False,
        "rating": 4.9,
        "reviews_count": 35,
        "variations": [
            {"size": "1L", "price": 17.00, "stock": 35, "sku": "VF-LEG-1L"}
        ],
        "default_size": "1L",
        "price": 17.00
    },
    # FLORASOL LICHIDE
    {
        "id": new_id + 12,
        "name": "Soluție nutritivă Florasol Universală",
        "category": "Ingrasaminte",
        "subcategory": "Florasol",
        "image": "/static/images/products/florasol-solutie-nutritiva-universala.jpg",
        "description": "Îngrășământ lichid economic și eficient pentru toate culturile floricole de interior și de grădină.",
        "featured": False,
        "rating": 4.7,
        "reviews_count": 26,
        "variations": [
            {"size": "500ml", "price": 10.50, "stock": 40, "sku": "FS-UNI-500"},
            {"size": "1L", "price": 16.50, "stock": 45, "sku": "FS-UNI-1L"}
        ],
        "default_size": "500ml",
        "price": 10.50
    },
    {
        "id": new_id + 13,
        "name": "Soluție nutritivă Florasol Plante de Balcon și Mușcate",
        "category": "Ingrasaminte",
        "subcategory": "Florasol",
        "image": "/static/images/products/florasol-solu-ie-nutritiv-pt-plante-de-b.jpg",
        "description": "Formulă clasică pentru fertilizarea mușcatelor și florilor cultivate în ghivece și jardiniere exterioare.",
        "featured": False,
        "rating": 4.7,
        "reviews_count": 24,
        "variations": [
            {"size": "500ml", "price": 10.50, "stock": 40, "sku": "FS-MUS-500"},
            {"size": "1L", "price": 16.50, "stock": 45, "sku": "FS-MUS-1L"}
        ],
        "default_size": "500ml",
        "price": 10.50
    },
    # HUMIFLOR LICHIDE
    {
        "id": new_id + 14,
        "name": "Soluție nutritivă Humiflor Plante de Cameră 1L",
        "category": "Ingrasaminte",
        "subcategory": "Humiflor",
        "image": "/static/images/products/humiflor-solutie-nutritiva-plante-de-cam.jpg",
        "description": "Tápoldat natural Humiflor cu acizi humici pentru revigorarea plantelor de cameră.",
        "featured": False,
        "rating": 4.7,
        "reviews_count": 18,
        "variations": [
            {"size": "1L", "price": 13.00, "stock": 35, "sku": "HU-CAM-1L"}
        ],
        "default_size": "1L",
        "price": 13.00
    },
    {
        "id": new_id + 15,
        "name": "Soluție nutritivă Humiflor Plante de Balcon 1L",
        "category": "Ingrasaminte",
        "subcategory": "Humiflor",
        "image": "/static/images/products/humiflor-solutie-nutritiva-plante-de-bal.jpg",
        "description": "Susține rezistența și înflorirea abundentă a florilor din balcoane și terase.",
        "featured": False,
        "rating": 4.7,
        "reviews_count": 19,
        "variations": [
            {"size": "1L", "price": 13.00, "stock": 35, "sku": "HU-BAL-1L"}
        ],
        "default_size": "1L",
        "price": 13.00
    },
    {
        "id": new_id + 16,
        "name": "Soluție nutritivă Humiflor Plante de Grădină 1L",
        "category": "Ingrasaminte",
        "subcategory": "Humiflor",
        "image": "/static/images/products/humiflor-solutie-nutritiva-plante-de-gra.jpg",
        "description": "Îngrășământ complex pentru arbuști ornamentali, trandafiri și flori perene de grădină.",
        "featured": False,
        "rating": 4.7,
        "reviews_count": 22,
        "variations": [
            {"size": "1L", "price": 13.00, "stock": 30, "sku": "HU-GRA-1L"}
        ],
        "default_size": "1L",
        "price": 13.00
    },
    # SOLIDE & BATOANE NUTRIITIVE
    {
        "id": new_id + 17,
        "name": "Batoane nutritive solide Vitaflora Plante cu Flori",
        "category": "Ingrasaminte",
        "subcategory": "Solide",
        "image": "/static/images/products/batoane-nutritive-plante-flori.png",
        "description": "Batoane nutritive solide cu eliberare lentă și controlată timp de până la 60 de zile. Se introduc simplu în pământul din ghiveci și eliberează nutrienți la fiecare udare.",
        "featured": True,
        "rating": 4.9,
        "reviews_count": 44,
        "variations": [
            {"size": "30 bucăți", "price": 6.16, "stock": 60, "sku": "VF-BAT-FL30"},
            {"size": "60 bucăți", "price": 11.50, "stock": 45, "sku": "VF-BAT-FL60"}
        ],
        "default_size": "30 bucăți",
        "price": 6.16
    },
    {
        "id": new_id + 18,
        "name": "Batoane nutritive solide Vitaflora Plante cu Frunze Verzi",
        "category": "Ingrasaminte",
        "subcategory": "Solide",
        "image": "/static/images/products/batoane-nutritive-plante-verzi.png",
        "description": "Batoane fertilizante solide concentrate în azot și fier pentru hrănirea de durată a ferigilor, palmierilor, ficușilor și plantelor mari de apartament.",
        "featured": False,
        "rating": 4.8,
        "reviews_count": 32,
        "variations": [
            {"size": "30 bucăți", "price": 6.16, "stock": 55, "sku": "VF-BAT-FR30"},
            {"size": "60 bucăți", "price": 11.50, "stock": 40, "sku": "VF-BAT-FR60"}
        ],
        "default_size": "30 bucăți",
        "price": 6.16
    },
    {
        "id": new_id + 19,
        "name": "Batoane nutritive solide Vitaflora Speciale Orhidee",
        "category": "Ingrasaminte",
        "subcategory": "Solide",
        "image": "/static/images/products/batoane-nutritive-orhidee.png",
        "description": "Batoane adaptate scoarței de orhidee, cu descompunere lentă și nutrienți esențiali care stimulează reînflorirea periodică fără arderea rădăcinilor.",
        "featured": True,
        "rating": 5.0,
        "reviews_count": 51,
        "variations": [
            {"size": "20 bucăți", "price": 7.99, "stock": 50, "sku": "VF-BAT-OR20"},
            {"size": "40 bucăți", "price": 14.50, "stock": 35, "sku": "VF-BAT-OR40"}
        ],
        "default_size": "20 bucăți",
        "price": 7.99
    }
]

unified_products.extend(fertilizers)
new_id += len(fertilizers)

# 3. PRODUSE DE ÎNGRIJIRE PLANTE, GHIVECE, DECORAȚIUNI
# (Keep flat categories without subcategories, but ensure variations structure)
other_items = []
for p in old_products:
    cat = p.get('category')
    if cat in ['Produse de Ingrijire plante', 'Ghivece', 'Decoratiuni']:
        # Ensure variations
        variations = p.get('variations')
        if not variations:
            size_label = "Standard"
            if cat == 'Ghivece':
                size_label = "Bucată"
            elif cat == 'Produse de Ingrijire plante':
                size_label = "500ml" if '0.5' in p['name'].lower() or '500' in p['name'].lower() else "Standard"
            variations = [
                {"size": size_label, "price": p['price'], "stock": p.get('stock', 25), "sku": p.get('sku', f"TD-{new_id}")}
            ]
        
        other_items.append({
            "id": new_id,
            "name": p['name'],
            "category": cat,
            "subcategory": "",  # no subcategories as requested!
            "image": p['image'],
            "description": p.get('description', ''),
            "featured": p.get('featured', False),
            "rating": p.get('rating', 4.8),
            "reviews_count": p.get('reviews_count', 15),
            "variations": variations,
            "default_size": variations[0]['size'],
            "price": variations[0]['price']
        })
        new_id += 1

unified_products.extend(other_items)

with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    json.dump(unified_products, f, ensure_ascii=False, indent=2)

print(f"SUCCESS: Created unified database with {len(unified_products)} products:")
print(f"  Pamant de Flori: {len(soils)} unified products (with 5L, 10L, 20L, 50L variations)")
print(f"  Ingrasaminte: {len(fertilizers)} unified products (with 500ml, 1L and stick variations)")
print(f"  Alte categorii (Ingrijire, Ghivece, Decoratiuni): {len(other_items)} products")
