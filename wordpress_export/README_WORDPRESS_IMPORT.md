# Ghid Import WordPress / WooCommerce & Sablon Torent Distribution
# Útmutató: WordPress / WooCommerce Termékimportálás és Sablon

---

## 1. Termékek importálása WooCommerce-be (Import Produse)

A projekt gyökérkönyvtárában található `woocommerce_products_import.csv` fájl mind a **143 terméket** tartalmazza:
- Cím (Denumire)
- Kategória hierarchia (ex: `Pamant de Flori`, `Ingrasaminte > Lichide - Solutii Nutritive`, `Ghivece`, stb.)
- Ár RON-ban (Preț)
- Készlet (Stoc)
- SKU azonosító kód (Cod produs)
- Képek hivatkozásai (Imagini)
- Román nyelvű szakmai leírások (Descrieri)

### Lépések a WordPress felületén:
1. Lépj be a WordPress adminisztrációs felületre: `https://te-domain-neved.ro/wp-admin`
2. Menj a bal oldali menüben: **Produse (Products) &rarr; Toate Produsele &rarr; Import** gombra.
3. Válaszd ki a `woocommerce_products_import.csv` fájlt a gépedről.
4. Ha már korábban importáltál, pipáld be: *"Actualizează produsele existente"* (Meglévő termékek frissítése).
5. Kattints a **Continuare (Tovább)** gombra, a mezők automatikusan össze lesznek párosítva.
6. Kattints az **Execută importul (Import indítása)** gombra.
7. Pár másodpercen belül az összes termék megjelenik a WooCommerce webáruházadban!

---

## 2. A Torent Horticulture WordPress Sablon telepítése

A `wordpress_export/torent-theme/` mappát egyszerűen tömörítsd ZIP formátumba (`torent-theme.zip`), majd:
1. WordPress admin felületen: **Aspect (Megjelenés) &rarr; Teme (Sablonok) &rarr; Adăugare temă nouă (Új sablon hozzáadása)**.
2. Kattints a **Încărcare temă (Sablon feltöltése)** gombra, és válaszd ki a létrehozott `torent-theme.zip` fájlt.
3. Kattints az **Instalează acum (Telepítés most)**, majd az **Activează (Aktiválás)** gombra.

---

## 3. A Modern Önálló Webáruház és /admin felület helyi futtatása

A webáruházat bármikor elindíthatod és használhatod a saját gépeden is:
- Egyszerűen kattints duplán a **`run_shop.bat`** fájlra, vagy futtasd terminálból:
  ```bash
  python app.py
  ```
- **Főoldal / Webáruház:** `http://127.0.0.1:5000`
- **Admin felület (képfeltöltés, törlés, termékkezelés):** `http://127.0.0.1:5000/admin`
  - Felhasználónév: `admin`
  - Jelszó: `adminpassword2026`
