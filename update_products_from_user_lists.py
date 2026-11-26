import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PRODUCTS_FILE = os.path.join(BASE_DIR, 'data', 'products.json')

with open(PRODUCTS_FILE, 'r', encoding='utf-8') as f:
    products = json.load(f)

# Update Virágföldek (Pământ de Flori)
soils_data = [
    # 1. PLANTASOL
    {
        "name": "Pământ de flori universal Plantasol",
        "category": "Pamant de Flori",
        "subcategory": "Plantasol",
        "image": "/static/images/products/pamant-de-flori-universal-plantasol-5l.png",
        "description": "Amestec de turbă universală Plantasol de înaltă calitate, îmbogățit cu nutrienți esențiali pentru toate plantele de apartament, balcon și grădină.",
        "featured": True,
        "rating": 4.9,
        "reviews_count": 52,
        "variations": [
            {"size": "5L", "price": 2.53, "stock": 60, "sku": "PL-UNI-5L"},
            {"size": "10L", "price": 4.76, "stock": 55, "sku": "PL-UNI-10L"},
            {"size": "20L", "price": 8.70, "stock": 50, "sku": "PL-UNI-20L"},
            {"size": "50L", "price": 18.98, "stock": 40, "sku": "PL-UNI-50L"}
        ]
    },
    # 2. FLORASOL (Exact 5L, 10L, 20L, 40L from image 1 & 2)
    {
        "name": "Pământ de flori universal Florasol",
        "category": "Pamant de Flori",
        "subcategory": "Florasol",
        "image": "/static/images/products/florasol-pamant-de-flori-universal.png",
        "description": "Substrat nutritiv complet Florasol cu biohumus și microelemente chelatizate. Ideal pentru replantarea și întreținerea plantelor cu flori și frunze.",
        "featured": True,
        "rating": 4.8,
        "reviews_count": 44,
        "variations": [
            {"size": "5L", "price": 4.64, "stock": 45, "sku": "FL-UNI-5L"},
            {"size": "10L", "price": 7.97, "stock": 40, "sku": "FL-UNI-10L"},
            {"size": "20L", "price": 13.84, "stock": 35, "sku": "FL-UNI-20L"},
            {"size": "40L", "price": 23.75, "stock": 30, "sku": "FL-UNI-40L"}
        ]
    },
    # 3. HUMIFLOR (Universal 5, 10, 20, 50L; Orhidee ONLY 5L from image 2)
    {
        "name": "Pământ de flori universal Humiflor",
        "category": "Pamant de Flori",
        "subcategory": "Humiflor",
        "image": "/static/images/products/pamant-de-flori-universal-humiflor.jpg",
        "description": "Pământ de flori nutritiv Humiflor cu humus natural și porozitate optimă pentru aerisirea rădăcinilor și reținerea echilibrată a umidității.",
        "featured": True,
        "rating": 4.8,
        "reviews_count": 39,
        "variations": [
            {"size": "5L", "price": 2.81, "stock": 50, "sku": "HU-UNI-5L"},
            {"size": "10L", "price": 5.27, "stock": 45, "sku": "HU-UNI-10L"},
            {"size": "20L", "price": 9.67, "stock": 40, "sku": "HU-UNI-20L"},
            {"size": "50L", "price": 21.08, "stock": 30, "sku": "HU-UNI-50L"}
        ]
    },
    {
        "name": "Substrat de orhidee Humiflor",
        "category": "Pamant de Flori",
        "subcategory": "Humiflor",
        "image": "/static/images/products/substrat-de-orhidee-humiflor-5l.jpg",
        "description": "Substrat special Humiflor din scoarță nobilă calibrată de pin mediteranean și turbă fibroasă pentru orhidee epifite. Disponibil exclusiv în ambalaj de 5L.",
        "featured": False,
        "rating": 4.9,
        "reviews_count": 31,
        "variations": [
            {"size": "5L", "price": 11.10, "stock": 40, "sku": "HU-ORH-5L"}
        ]
    },
    # 4. NUTRISOL (Plante camera ONLY 10L, Straturi inaltate ONLY 20L, Muscate ONLY 20L & 50L)
    {
        "name": "Nutrisol pământ de flori pentru plante de cameră",
        "category": "Pamant de Flori",
        "subcategory": "Nutrisol",
        "image": "/static/images/products/nutrisol-substrat-plante-de-camera-10l.jpg",
        "description": "Substrat premium Nutrisol dedicat plantelor de apartament, cu perlit și turbă fină pentru drenaj și prevenirea compactării solului. Ambalaj unic de 10L.",
        "featured": True,
        "rating": 4.9,
        "reviews_count": 35,
        "variations": [
            {"size": "10L", "price": 5.53, "stock": 55, "sku": "NU-CAM-10L"}
        ]
    },
    {
        "name": "Nutrisol pământ pentru plante de grădină și straturi înălțate",
        "category": "Pamant de Flori",
        "subcategory": "Nutrisol",
        "image": "/static/images/products/nutrisol-substrat-straturi-inaltate-20l.jpg",
        "description": "Substrat nutritiv de volum cu compost matur și turbă neagră pentru grădini de legume și straturi înălțate. Disponibil exclusiv în sac de 20L.",
        "featured": False,
        "rating": 4.8,
        "reviews_count": 27,
        "variations": [
            {"size": "20L", "price": 10.30, "stock": 45, "sku": "NU-INA-20L"}
        ]
    },
    {
        "name": "Nutrisol pământ de flori pentru mușcate și plante de balcon",
        "category": "Pamant de Flori",
        "subcategory": "Nutrisol",
        "image": "/static/images/products/nutrisol-pamant-de-flori-plante-de-balco.jpg",
        "description": "Formulă îmbogățită cu potasiu și fosfor pentru mușcate și flori de balcon viguroase, cu înflorire abundentă. Disponibil în saci de 20L și 50L.",
        "featured": True,
        "rating": 4.9,
        "reviews_count": 42,
        "variations": [
            {"size": "20L", "price": 10.15, "stock": 50, "sku": "NU-BAL-20L"},
            {"size": "50L", "price": 22.58, "stock": 35, "sku": "NU-BAL-50L"}
        ]
    },
    # 5. FLORIMO (Substraturi conform listei din Image 1)
    {
        "name": "Florimo Universal",
        "category": "Pamant de Flori",
        "subcategory": "Florimo",
        "image": "/static/images/products/florimo-pamant-de-flori-universal.png",
        "description": "Substrat universal premium Florimo din turbă de sphagnum, perlit și îngrășământ starter PG-Mix cu oligoelemente.",
        "featured": True,
        "rating": 5.0,
        "reviews_count": 64,
        "variations": [
            {"size": "3L", "price": 4.20, "stock": 40, "sku": "FO-UNI-3L"},
            {"size": "10L", "price": 8.50, "stock": 45, "sku": "FO-UNI-10L"},
            {"size": "20L", "price": 15.50, "stock": 40, "sku": "FO-UNI-20L"},
            {"size": "50L", "price": 32.00, "stock": 35, "sku": "FO-UNI-50L"}
        ]
    },
    {
        "name": "Florimo Acid",
        "category": "Pamant de Flori",
        "subcategory": "Florimo",
        "image": "/static/images/products/florimo-pamant-de-flori-acidulos.png",
        "description": "Substrat acidofil special (pH 4.0 - 5.0) pentru azalee, rododendroni, hortensii albastre, erica și afini de cultură.",
        "featured": False,
        "rating": 4.9,
        "reviews_count": 33,
        "variations": [
            {"size": "3L", "price": 4.90, "stock": 30, "sku": "FO-ACI-3L"},
            {"size": "10L", "price": 9.80, "stock": 35, "sku": "FO-ACI-10L"},
            {"size": "20L", "price": 18.00, "stock": 30, "sku": "FO-ACI-20L"}
        ]
    },
    {
        "name": "Florimo Pt. mușcate și pl. de balcon",
        "category": "Pamant de Flori",
        "subcategory": "Florimo",
        "image": "/static/images/products/florimo-pamant-de-flori-de-muscate.png",
        "description": "Substrat structurat cu argilă pentru reținerea apei și potasiu ridicat, special pentru mușcate curgătoare și de balcon.",
        "featured": False,
        "rating": 4.9,
        "reviews_count": 37,
        "variations": [
            {"size": "10L", "price": 9.00, "stock": 40, "sku": "FO-MUS-10L"},
            {"size": "20L", "price": 16.00, "stock": 35, "sku": "FO-MUS-20L"},
            {"size": "50L", "price": 34.00, "stock": 25, "sku": "FO-MUS-50L"}
        ]
    },
    {
        "name": "Florimo Pt. conifere",
        "category": "Pamant de Flori",
        "subcategory": "Florimo",
        "image": "/static/images/products/florimo-substrat-de-conifere.png",
        "description": "Substrat îmbogățit cu magneziu și fier, prevenind brunificarea acelor la tuia, brazi, molizi și ienuperi.",
        "featured": False,
        "rating": 4.8,
        "reviews_count": 29,
        "variations": [
            {"size": "20L", "price": 18.00, "stock": 35, "sku": "FO-CON-20L"},
            {"size": "50L", "price": 36.00, "stock": 30, "sku": "FO-CON-50L"}
        ]
    },
    {
        "name": "Florimo Pt. orchidee",
        "category": "Pamant de Flori",
        "subcategory": "Florimo",
        "image": "/static/images/products/substrat-de-orhidee-florimo-3l.png",
        "description": "Scoarță nobilă calibrată de pin cu adaos de cărbune activ pentru orhidee epifite.",
        "featured": False,
        "rating": 4.9,
        "reviews_count": 41,
        "variations": [
            {"size": "3L", "price": 24.07, "stock": 40, "sku": "FO-ORH-3L"}
        ]
    }
]

# Update Îngrășăminte (Vitaflora, Florasol, Humiflor, Solide) - Exact prices from Image 3
fertilizers_data = [
    # VITAFLORA
    {
        "name": "Vitaflora 1 Pt. plante cu flori",
        "category": "Ingrasaminte",
        "subcategory": "Vitaflora",
        "image": "/static/images/products/vitaflora-solutie-nutritiva-plante-cu-fl.png",
        "description": "Soluție nutritivă concentrată pentru plante cu flori. Stimulează formarea bobocilor și o înflorire de lungă durată.",
        "featured": True,
        "rating": 4.9,
        "reviews_count": 52,
        "variations": [
            {"size": "0.1L", "price": 4.48, "stock": 40, "sku": "10101"},
            {"size": "0.5L", "price": 9.71, "stock": 50, "sku": "10105"},
            {"size": "1L", "price": 15.89, "stock": 60, "sku": "10110"}
        ]
    },
    {
        "name": "Vitaflora 2 Pt. plante cu frunze",
        "category": "Ingrasaminte",
        "subcategory": "Vitaflora",
        "image": "/static/images/products/vitaflora-solutie-nutritiva-plante-cu-fr.png",
        "description": "Soluție nutritivă bogată în azot și magneziu pentru stimularea fotosintezei și un frunziș viguros, verde intens.",
        "featured": False,
        "rating": 4.8,
        "reviews_count": 34,
        "variations": [
            {"size": "0.1L", "price": 4.48, "stock": 35, "sku": "10201"},
            {"size": "0.5L", "price": 9.71, "stock": 45, "sku": "10205"},
            {"size": "1L", "price": 15.89, "stock": 50, "sku": "10210"}
        ]
    },
    {
        "name": "Vitaflora 3 Universal",
        "category": "Ingrasaminte",
        "subcategory": "Vitaflora",
        "image": "/static/images/products/vitaflora-solutie-nutritiva-universala.png",
        "description": "Îngrășământ lichid complet cu raport echilibrat de macro și microelemente chelatizate EDTA pentru toate plantele.",
        "featured": True,
        "rating": 4.9,
        "reviews_count": 58,
        "variations": [
            {"size": "0.1L", "price": 4.48, "stock": 40, "sku": "10301"},
            {"size": "0.5L", "price": 9.71, "stock": 55, "sku": "10305"},
            {"size": "1L", "price": 15.89, "stock": 65, "sku": "10310"}
        ]
    },
    {
        "name": "Vitaflora 5 Pt. stimularea înfloririi",
        "category": "Ingrasaminte",
        "subcategory": "Vitaflora",
        "image": "/static/images/products/vitaflora-solutie-nutritiva-stimularea-i.png",
        "description": "Biostimulator de înflorire cu fosfor și fitohormoni naturali pentru pornirea mugurilor florali.",
        "featured": False,
        "rating": 4.8,
        "reviews_count": 31,
        "variations": [
            {"size": "0.1L", "price": 4.48, "stock": 30, "sku": "10501"},
            {"size": "0.5L", "price": 9.93, "stock": 40, "sku": "10505"},
            {"size": "1L", "price": 16.18, "stock": 45, "sku": "10510"}
        ]
    },
    {
        "name": "Vitaflora 6 Pt. mușcate",
        "category": "Ingrasaminte",
        "subcategory": "Vitaflora",
        "image": "/static/images/products/vitaflora-solutie-nutritiva-muscate-si-p.png",
        "description": "Formulă specializată pentru mușcate curgătoare și drepte, petunii și flori de balcon expuse la soare intens.",
        "featured": True,
        "rating": 5.0,
        "reviews_count": 67,
        "variations": [
            {"size": "0.1L", "price": 4.48, "stock": 45, "sku": "10601"},
            {"size": "0.5L", "price": 10.13, "stock": 55, "sku": "10605"},
            {"size": "1L", "price": 16.51, "stock": 70, "sku": "10610"}
        ]
    },
    {
        "name": "Vitaflora 7 Pt. gazon",
        "category": "Ingrasaminte",
        "subcategory": "Vitaflora",
        "image": "/static/images/products/vitaflora-solu-ie-nutritiv-pt-gazon-1l.png",
        "description": "Îngrășământ lichid profesional pentru înverzirea și regenerarea rapidă a gazonului.",
        "featured": False,
        "rating": 4.8,
        "reviews_count": 25,
        "variations": [
            {"size": "1L", "price": 16.72, "stock": 40, "sku": "10710"}
        ]
    },
    {
        "name": "Vitaflora 8 Pt. cactuși",
        "category": "Ingrasaminte",
        "subcategory": "Vitaflora",
        "image": "/static/images/products/vitaflora-solutie-nutritiva-cactusi.png",
        "description": "Raport optim NPK cu azot scăzut, prevenind crăparea țesuturilor suculente la cactuși și aloe.",
        "featured": False,
        "rating": 4.7,
        "reviews_count": 22,
        "variations": [
            {"size": "0.1L", "price": 4.48, "stock": 30, "sku": "10801"},
            {"size": "0.5L", "price": 9.93, "stock": 35, "sku": "10805"}
        ]
    },
    {
        "name": "Vitaflora Pt. orhidee",
        "category": "Ingrasaminte",
        "subcategory": "Vitaflora",
        "image": "/static/images/products/vitaflora-solutie-nutritiva-orhidee.png",
        "description": "Formulă blândă cu salinitate redusă, protejând rădăcinile aeriene și stimulând apariția noilor tije florale.",
        "featured": True,
        "rating": 5.0,
        "reviews_count": 59,
        "variations": [
            {"size": "0.1L", "price": 4.73, "stock": 40, "sku": "11301"},
            {"size": "0.5L", "price": 11.37, "stock": 45, "sku": "11305"}
        ]
    },
    {
        "name": "Vitaflora Pt. citrice și pl. medit.",
        "category": "Ingrasaminte",
        "subcategory": "Vitaflora",
        "image": "/static/images/products/vitaflora-solu-ie-nutritiv-pt-citrice-0-.png",
        "description": "Special pentru lămâi, portocali, măslini și leandri, prevenind cloroza frunzelor prin conținut generos de fier.",
        "featured": False,
        "rating": 4.9,
        "reviews_count": 33,
        "variations": [
            {"size": "0.5L", "price": 10.93, "stock": 35, "sku": "10905"}
        ]
    },
    {
        "name": "Vitaflora Bonsai",
        "category": "Ingrasaminte",
        "subcategory": "Vitaflora",
        "image": "/static/images/products/vitaflora-solutie-nutritiva-universala.png",
        "description": "Îngrășământ special dozat pentru creșterea echilibrată a arborilor bonsai de interior și exterior.",
        "featured": False,
        "rating": 4.8,
        "reviews_count": 18,
        "variations": [
            {"size": "0.1L", "price": 4.48, "stock": 25, "sku": "10001"},
            {"size": "0.5L", "price": 10.13, "stock": 30, "sku": "10005"}
        ]
    },
    {
        "name": "Vitaflora Pt. Plante curgătoare",
        "category": "Ingrasaminte",
        "subcategory": "Vitaflora",
        "image": "/static/images/products/vitaflora-solutie-nutritiva-plante-curga.png",
        "description": "Nutriție avansată pentru petunii curgătoare, fuchsia, begonia pendula și iederă.",
        "featured": False,
        "rating": 4.8,
        "reviews_count": 28,
        "variations": [
            {"size": "0.5L", "price": 10.13, "stock": 35, "sku": "11005"},
            {"size": "1L", "price": 15.70, "stock": 40, "sku": "11010"}
        ]
    },
    {
        "name": "Vitaflora Pt. conifere",
        "category": "Ingrasaminte",
        "subcategory": "Vitaflora",
        "image": "/static/images/products/vitaflora-solu-ie-nutritiv-pt-conifere-1.png",
        "description": "Prevenirea îngălbenirii acelor și fortificarea rădăcinilor la tuia, brazi și chiparoși.",
        "featured": False,
        "rating": 4.8,
        "reviews_count": 30,
        "variations": [
            {"size": "1L", "price": 15.38, "stock": 40, "sku": "11110"}
        ]
    },
    {
        "name": "Vitaflora Pt. legume",
        "category": "Ingrasaminte",
        "subcategory": "Vitaflora",
        "image": "/static/images/products/vitaflora-solu-ie-nutritiv-pt-legume-1l.png",
        "description": "Nutriție curată pentru roșii, ardei, castraveți și căpșuni, favorizând fructificarea gustoasă.",
        "featured": False,
        "rating": 4.9,
        "reviews_count": 36,
        "variations": [
            {"size": "1L", "price": 16.51, "stock": 35, "sku": "11210"}
        ]
    },
    # FLORASOL LICHIDE
    {
        "name": "Florasol Universal",
        "category": "Ingrasaminte",
        "subcategory": "Florasol",
        "image": "/static/images/products/florasol-solutie-nutritiva-universala.jpg",
        "description": "Soluție nutritivă completă Florasol pentru toate culturile floricole.",
        "featured": False,
        "rating": 4.7,
        "reviews_count": 25,
        "variations": [
            {"size": "0.5L", "price": 8.16, "stock": 40, "sku": "19305"},
            {"size": "1L", "price": 12.15, "stock": 45, "sku": "19310"}
        ]
    },
    {
        "name": "Florasol Pt. mușcate",
        "category": "Ingrasaminte",
        "subcategory": "Florasol",
        "image": "/static/images/products/florasol-solu-ie-nutritiv-pt-plante-de-b.jpg",
        "description": "Îngrășământ lichid Florasol special adaptat pentru mușcate și flori de balcon.",
        "featured": False,
        "rating": 4.7,
        "reviews_count": 27,
        "variations": [
            {"size": "0.5L", "price": 8.16, "stock": 40, "sku": "19605"},
            {"size": "1L", "price": 12.15, "stock": 45, "sku": "19610"}
        ]
    },
    # HUMIFLOR LICHIDE
    {
        "name": "Humiflor pentru plante de balcon 1L",
        "category": "Ingrasaminte",
        "subcategory": "Humiflor",
        "image": "/static/images/products/humiflor-solutie-nutritiva-plante-de-bal.jpg",
        "description": "Îngrășământ lichid Humiflor pentru flori de terasă și balcon.",
        "featured": False,
        "rating": 4.7,
        "reviews_count": 20,
        "variations": [
            {"size": "1L", "price": 11.98, "stock": 35, "sku": "H610"}
        ]
    },
    {
        "name": "Humiflor pentru plante de gradina 1L",
        "category": "Ingrasaminte",
        "subcategory": "Humiflor",
        "image": "/static/images/products/humiflor-solutie-nutritiva-plante-de-gra.jpg",
        "description": "Soluție nutritivă Humiflor pentru arbuști ornamentali și flori de grădină.",
        "featured": False,
        "rating": 4.7,
        "reviews_count": 22,
        "variations": [
            {"size": "1L", "price": 12.47, "stock": 30, "sku": "H510"}
        ]
    },
    {
        "name": "Humiflor pentru plante de camera 1L",
        "category": "Ingrasaminte",
        "subcategory": "Humiflor",
        "image": "/static/images/products/humiflor-solutie-nutritiva-plante-de-cam.jpg",
        "description": "Tápoldat Humiflor cu substanțe humice pentru plantele de apartament.",
        "featured": False,
        "rating": 4.7,
        "reviews_count": 24,
        "variations": [
            {"size": "1L", "price": 11.78, "stock": 35, "sku": "H310"}
        ]
    },
    # SOLIDE (Batoane)
    {
        "name": "Vitaflora Pt. plante cu flori (Batoane)",
        "category": "Ingrasaminte",
        "subcategory": "Solide",
        "image": "/static/images/products/batoane-nutritive-plante-flori.png",
        "description": "Batoane fertilizante solide cu eliberare prelungită timp de 60 de zile pentru plante cu flori.",
        "featured": True,
        "rating": 4.9,
        "reviews_count": 48,
        "variations": [
            {"size": "30g (30 buc)", "price": 7.24, "stock": 60, "sku": "10100"}
        ]
    },
    {
        "name": "Vitaflora Pt. plante cu frunze (Batoane)",
        "category": "Ingrasaminte",
        "subcategory": "Solide",
        "image": "/static/images/products/batoane-nutritive-plante-verzi.png",
        "description": "Batoane nutritive solide cu azot și magneziu pentru plante verzi de apartament.",
        "featured": False,
        "rating": 4.8,
        "reviews_count": 35,
        "variations": [
            {"size": "30g (30 buc)", "price": 7.24, "stock": 55, "sku": "10200"}
        ]
    },
    {
        "name": "Vitaflora Pt. orhidee (Batoane)",
        "category": "Ingrasaminte",
        "subcategory": "Solide",
        "image": "/static/images/products/batoane-nutritive-orhidee.png",
        "description": "Batoane speciale cu acțiune lentă adaptate rădăcinilor aeriene de orhidee.",
        "featured": True,
        "rating": 5.0,
        "reviews_count": 54,
        "variations": [
            {"size": "15g (20 buc)", "price": 7.72, "stock": 50, "sku": "11300"}
        ]
    }
]

# Produse de Ingrijire plante - Update Florasol Solutie Ecologica
care_items = [
    {
        "name": "Florasol Solutie Ecologica Ingrijire plante 0.5L",
        "category": "Produse de Ingrijire plante",
        "subcategory": "",
        "image": "/static/images/products/florasol-insecticid-ecologic-0-5l.png",
        "description": "Soluție ecologică gata de aplicare pentru protecția și revigorarea plantelor împotriva dăunătorilor și stresului climatic.",
        "featured": True,
        "rating": 4.9,
        "reviews_count": 38,
        "variations": [
            {"size": "0.5L", "price": 12.12, "stock": 45, "sku": "19500"}
        ]
    }
]

# Keep other items from existing database (Ghivece, Decoratiuni, other Ingrijire)
other_items = []
for p in products:
    if p.get('category') in ['Ghivece', 'Decoratiuni']:
        other_items.append(p)
    elif p.get('category') == 'Produse de Ingrijire plante' and 'florasol' not in p.get('name', '').lower():
        other_items.append(p)

# Assemble updated database with default_size and starting price
final_list = []
cur_id = 1

for item in soils_data + fertilizers_data + care_items + other_items:
    item['id'] = cur_id
    item['default_size'] = item['variations'][0]['size']
    item['price'] = item['variations'][0]['price']
    final_list.append(item)
    cur_id += 1

with open(PRODUCTS_FILE, 'w', encoding='utf-8') as f:
    json.dump(final_list, f, ensure_ascii=False, indent=2)

print(f"SUCCESS: Updated database with {len(final_list)} products.")
print(f"  Virágföldek (Soils): {len(soils_data)}")
print(f"  Îngrășăminte (Fertilizers): {len(fertilizers_data)}")
print(f"  Ingrijire / Ghivece / Decoratiuni: {len(care_items) + len(other_items)}")
