import os
import json
import re
import time
import hmac
import hashlib
import secrets
import datetime
import csv
import smtplib
from decimal import Decimal, ROUND_HALF_UP, ROUND_CEILING
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from collections import defaultdict
from io import StringIO
from flask import (
    Flask, render_template, request, jsonify, redirect,
    url_for, session, send_from_directory, flash, Response
)
from werkzeug.utils import secure_filename

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load local .env file into environment if present (zero external dependencies)
_ENV_FILE = os.path.join(BASE_DIR, '.env')
if os.path.exists(_ENV_FILE):
    with open(_ENV_FILE, 'r', encoding='utf-8') as _ef:
        for _line in _ef:
            _line = _line.strip()
            if _line and not _line.startswith('#') and '=' in _line:
                _k, _v = _line.split('=', 1)
                os.environ.setdefault(_k.strip(), _v.strip().strip('"').strip("'"))

DATA_DIR = os.path.join(BASE_DIR, 'data')
PRODUCTS_FILE = os.path.join(DATA_DIR, 'products.json')
ORDERS_FILE = os.path.join(DATA_DIR, 'orders.json')
SETTINGS_FILE = os.path.join(DATA_DIR, 'settings.json')
CRM_FILE = os.path.join(DATA_DIR, 'crm_clients.json')
B2B_REQUESTS_FILE = os.path.join(DATA_DIR, 'b2b_requests.json')
CATEGORIES_FILE = os.path.join(DATA_DIR, 'categories.json')
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'images', 'products')

# Central public contact phone (edit here or via SUPPORT_PHONE env / Admin Settings)
SUPPORT_PHONE = os.environ.get('SUPPORT_PHONE', '0740 000 000')

DEFAULT_CATEGORIES = [
    {
        "id": 1,
        "key": "Pamant de Flori",
        "display_name": "Pământ de Flori",
        "description": "Substraturi nutritive pentru înrădăcinare sănătoasă, drenaj optim și dezvoltarea viguroasă a plantelor de interior, balcon și grădină.",
        "icon": "fa-mountain",
        "unit_label": "produse",
        "fallback_image": "/static/images/categories/cat-pamant-de-flori.webp",
        "subcategories": ["Florasol", "Humiflor", "Nutrisol", "Plantasol", "Florimo"]
    },
    {
        "id": 2,
        "key": "Ingrasaminte",
        "display_name": "Soluții nutritive",
        "description": "Nutrienți concentrați și batoane fertilizante pentru o înflorire abundentă, frunziș verde intens și rezistență sporită a plantelor.",
        "icon": "fa-flask-vial",
        "unit_label": "produse",
        "fallback_image": "/static/images/categories/cat-solutii-nutritive.webp",
        "subcategories": ["Vitaflora", "Florasol", "Humiflor", "Solide"]
    },
    {
        "id": 3,
        "key": "Produse de Ingrijire plante",
        "display_name": "Îngrijire Plante",
        "description": "Soluții ecologice și organice pentru protecția plantelor împotriva dăunătorilor, bolilor și stresului climatic.",
        "icon": "fa-shield-halved",
        "unit_label": "produse",
        "fallback_image": "/static/images/categories/cat-ingrijire-plante.webp",
        "subcategories": []
    },
    {
        "id": 4,
        "key": "Ghivece",
        "display_name": "Ghivece & Jardiniere",
        "description": "Ghivece ceramice moderne SK, jardiniere de balcon și ghivece suspendate.",
        "icon": "fa-bucket",
        "unit_label": "produse",
        "fallback_image": "/static/images/categories/cat-ghivece.webp",
        "subcategories": []
    },
    {
        "id": 5,
        "key": "Decoratiuni",
        "display_name": "Decorațiuni",
        "description": "Figurine artistice pentru grădină, decorațiuni tematice și accesorii festive.",
        "icon": "fa-wand-magic-sparkles",
        "unit_label": "produse",
        "fallback_image": "/static/images/categories/cat-decoratiuni.webp",
        "subcategories": []
    }
]

DEFAULT_SETTINGS = {
    "order_email": "vanzari@torentdistribution.ro",
    "company_name": "TORENT DISTRIBUTION SRL",
    "company_cui": "RO________",
    "company_reg_com": "J__ / ____ / ____",
    "company_address": "România",
    "company_phone": "+40 700 000 000",
    "smtp_host": "",
    "smtp_port": 587,
    "smtp_user": "",
    "smtp_password": "",
    "smtp_use_tls": True
}

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'torent-distribution-horticulture-secret-key-2026')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 25 * 1024 * 1024  # 25MB max upload

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif'}

# Admin credentials
ADMIN_USERNAME = os.environ.get('ADMIN_USER', 'admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASS', 'adminpassword2026')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_products():
    if not os.path.exists(PRODUCTS_FILE):
        return []
    with open(PRODUCTS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_products(products):
    with open(PRODUCTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)

ORDER_STATUSES = ["Comandă nouă", "În prelucrare", "Finalizată"]
LEGACY_ORDER_STATUS_MAP = {
    "În așteptare": "Comandă nouă",
    "In asteptare": "Comandă nouă",
    "Comanda noua": "Comandă nouă",
    "În procesare": "În prelucrare",
    "In procesare": "În prelucrare",
    "In prelucrare": "În prelucrare",
    "Finalizata": "Finalizată"
}

def load_orders():
    if not os.path.exists(ORDERS_FILE):
        return []
    with open(ORDERS_FILE, 'r', encoding='utf-8') as f:
        orders = json.load(f)
    for o in orders:
        st = o.get('status', 'Comandă nouă')
        o['status'] = LEGACY_ORDER_STATUS_MAP.get(st, st if st in ORDER_STATUSES else 'Comandă nouă')
    return orders

def save_orders(orders):
    with open(ORDERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(orders, f, ensure_ascii=False, indent=2)

def load_settings():
    settings = dict(DEFAULT_SETTINGS)
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                saved = json.load(f)
                if isinstance(saved, dict):
                    settings.update(saved)
        except Exception:
            pass
    return settings

def save_settings(settings):
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)

def load_crm():
    if not os.path.exists(CRM_FILE):
        return []
    try:
        with open(CRM_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []

def save_crm(clients):
    with open(CRM_FILE, 'w', encoding='utf-8') as f:
        json.dump(clients, f, ensure_ascii=False, indent=2)

def load_categories():
    if not os.path.exists(CATEGORIES_FILE):
        save_categories(DEFAULT_CATEGORIES)
        return [dict(c) for c in DEFAULT_CATEGORIES]
    try:
        with open(CATEGORIES_FILE, 'r', encoding='utf-8') as f:
            cats = json.load(f)
            if isinstance(cats, list) and len(cats) > 0:
                return cats
    except Exception:
        pass
    return [dict(c) for c in DEFAULT_CATEGORIES]

def save_categories(categories):
    with open(CATEGORIES_FILE, 'w', encoding='utf-8') as f:
        json.dump(categories, f, ensure_ascii=False, indent=2)

DEFAULT_TVA_RATES = [11, 21]


def get_tva_rates(settings=None):
    if settings is None:
        settings = load_settings()
    raw = settings.get('tva_rates')
    if not isinstance(raw, list) or not raw:
        return list(DEFAULT_TVA_RATES)
    cleaned = []
    for r in raw:
        try:
            val = float(r)
            if val >= 0:
                cleaned.append(int(val) if val.is_integer() else round(val, 2))
        except (TypeError, ValueError):
            continue
    return sorted(set(cleaned)) or list(DEFAULT_TVA_RATES)


def default_tva_for_category(category):
    return 11 if category == 'Ingrasaminte' else 21


def calc_gross_from_net(pret_net, cota_tva):
    """Exact Decimal calculation: raw_gross = round(net * (1 + tva/100), 2), then ceiling to .50 or .00."""
    try:
        net_d = Decimal(str(pret_net)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    except Exception:
        net_d = Decimal('0.00')
    try:
        tva_d = Decimal(str(cota_tva))
    except Exception:
        tva_d = Decimal('21')
    raw_gross = (net_d * (Decimal('1') + tva_d / Decimal('100'))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    doubled_ceil = (raw_gross * Decimal('2')).to_integral_value(rounding=ROUND_CEILING)
    gross_d = (doubled_ceil / Decimal('2')).quantize(Decimal('0.01'))
    return float(net_d), float(gross_d)


def apply_product_tva_pricing(prod, cota_tva=None):
    """Recalculates pret_net, cota_tva, pret_brut, and price (gross) for a product and all its variations."""
    if cota_tva is None:
        cota_tva = prod.get('cota_tva', default_tva_for_category(prod.get('category', '')))
    tva_num = int(float(cota_tva)) if float(cota_tva).is_integer() else round(float(cota_tva), 2)
    prod['cota_tva'] = tva_num

    vars_list = prod.get('variations')
    if vars_list and isinstance(vars_list, list):
        for v in vars_list:
            base_net = v.get('pret_net', v.get('price', 0.0))
            net_val, gross_val = calc_gross_from_net(base_net, tva_num)
            v['pret_net'] = net_val
            v['cota_tva'] = tva_num
            v['pret_brut'] = gross_val
            v['price'] = gross_val
        prod['pret_net'] = min(v['pret_net'] for v in vars_list)
        prod['pret_brut'] = min(v['pret_brut'] for v in vars_list)
        prod['price'] = prod['pret_brut']
    else:
        base_net = prod.get('pret_net', prod.get('price', 0.0))
        net_val, gross_val = calc_gross_from_net(base_net, tva_num)
        prod['pret_net'] = net_val
        prod['pret_brut'] = gross_val
        prod['price'] = gross_val
    return prod


def compute_order_efactura_snapshot(raw_items, products_catalog):
    """Build immutable e-Factura order item snapshots and exact Decimal TVA breakdown."""
    prod_by_id = {p['id']: p for p in products_catalog}
    snapshot_items = []
    breakdown = {}

    total_net_d = Decimal('0.00')
    total_tva_d = Decimal('0.00')
    subtotal_brut_d = Decimal('0.00')

    for raw in (raw_items or []):
        pid = raw.get('id')
        qty = max(1, int(raw.get('quantity', 1)))
        req_size = str(raw.get('size', '') or '').strip()
        req_sku = str(raw.get('sku', '') or '').strip()

        prod = prod_by_id.get(pid)
        if prod:
            cota_tva = prod.get('cota_tva', default_tva_for_category(prod.get('category', '')))
            matched_var = None
            for v in prod.get('variations', []):
                if (req_sku and v.get('sku') == req_sku) or (req_size and v.get('size') == req_size):
                    matched_var = v
                    break
            unit_brut_raw = (matched_var.get('pret_brut', matched_var.get('price')) if matched_var else prod.get('pret_brut', prod.get('price')))
            item_name = raw.get('name') or (f"{prod['name']} ({matched_var['size']})" if matched_var and matched_var.get('size') != 'Standard' else prod['name'])
            item_size = matched_var.get('size', 'Standard') if matched_var else (req_size or 'Standard')
            item_sku = matched_var.get('sku', f"TD-{pid}") if matched_var else (req_sku or f"TD-{pid}")
        else:
            cota_tva = raw.get('cota_tva', 21)
            unit_brut_raw = raw.get('pret_brut_unitar', raw.get('price', 0.0))
            item_name = raw.get('name', 'Produs')
            item_size = req_size or 'Standard'
            item_sku = req_sku or f"TD-{pid or 0}"

        tva_num = int(float(cota_tva)) if float(cota_tva).is_integer() else round(float(cota_tva), 2)
        unit_brut_d = Decimal(str(unit_brut_raw)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        divisor = Decimal('1') + (Decimal(str(tva_num)) / Decimal('100'))
        unit_net_recalc_d = (unit_brut_d / divisor).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        val_bruta_d = (unit_brut_d * Decimal(qty)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        val_neta_d = (unit_net_recalc_d * Decimal(qty)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        val_tva_d = (val_bruta_d - val_neta_d).quantize(Decimal('0.01'))

        total_net_d += val_neta_d
        total_tva_d += val_tva_d
        subtotal_brut_d += val_bruta_d

        key = str(tva_num)
        if key not in breakdown:
            breakdown[key] = {
                "cota_tva": tva_num,
                "valoare_neta": Decimal('0.00'),
                "valoare_tva": Decimal('0.00'),
                "valoare_bruta": Decimal('0.00')
            }
        breakdown[key]["valoare_neta"] += val_neta_d
        breakdown[key]["valoare_tva"] += val_tva_d
        breakdown[key]["valoare_bruta"] += val_bruta_d

        snapshot_items.append({
            "id": pid,
            "name": item_name,
            "size": item_size,
            "sku": item_sku,
            "quantity": qty,
            "cota_tva": tva_num,
            "pret_brut_unitar": float(unit_brut_d),
            "price": float(unit_brut_d),
            "pret_net_recalculat": float(unit_net_recalc_d),
            "valoare_neta": float(val_neta_d),
            "valoare_tva": float(val_tva_d),
            "valoare_bruta": float(val_bruta_d)
        })

    shipping_d = Decimal('0.00') if subtotal_brut_d >= Decimal('150.00') else Decimal('19.00')
    grand_total_d = (subtotal_brut_d + shipping_d).quantize(Decimal('0.01'))

    tva_breakdown_list = [
        {
            "cota_tva": b["cota_tva"],
            "valoare_neta": float(b["valoare_neta"].quantize(Decimal('0.01'))),
            "valoare_tva": float(b["valoare_tva"].quantize(Decimal('0.01'))),
            "valoare_bruta": float(b["valoare_bruta"].quantize(Decimal('0.01')))
        }
        for _, b in sorted(breakdown.items(), key=lambda kv: float(kv[0]))
    ]

    return {
        "items": snapshot_items,
        "subtotal_brut": float(subtotal_brut_d.quantize(Decimal('0.01'))),
        "shipping_brut": float(shipping_d),
        "total_net": float(total_net_d.quantize(Decimal('0.01'))),
        "total_tva": float(total_tva_d.quantize(Decimal('0.01'))),
        "total_brut": float(subtotal_brut_d.quantize(Decimal('0.01'))),
        "total": float(grand_total_d),
        "tva_breakdown": tva_breakdown_list
    }


def build_company_order_email(order):
    """Generates e-Factura-ready plain-text and HTML email for company order notifications."""
    cust = order.get('customer', {})
    items = order.get('items', [])
    breakdown = order.get('tva_breakdown', [])
    total_net = float(order.get('total_net', 0.0))
    total_tva = float(order.get('total_tva', 0.0))
    subtotal_brut = float(order.get('subtotal_brut', order.get('total_brut', order.get('total', 0.0))))
    shipping_brut = float(order.get('shipping_brut', 0.0))
    grand_total = float(order.get('total', subtotal_brut))

    subject = f"Comandă nouă #{order['id']} - {cust.get('name', 'Client')} ({grand_total:.2f} RON TVA inclus)"

    # Plain-text version
    plain_rows = []
    for it in items:
        cota = it.get('cota_tva', 21)
        p_net = float(it.get('pret_net_recalculat', 0.0))
        p_brut = float(it.get('pret_brut_unitar', it.get('price', 0.0)))
        v_net = float(it.get('valoare_neta', 0.0))
        v_tva = float(it.get('valoare_tva', 0.0))
        v_brut = float(it.get('valoare_bruta', p_brut * int(it.get('quantity', 1))))
        plain_rows.append(
            f" - {it.get('name')} | Cant: {it.get('quantity')} | TVA: {cota}% | "
            f"Net unitar: {p_net:.2f} RON | Brut unitar: {p_brut:.2f} RON | "
            f"Total Net: {v_net:.2f} + TVA: {v_tva:.2f} = {v_brut:.2f} RON"
        )

    breakdown_plain = "\n".join(
        f"   * TVA {b['cota_tva']}%: Bază netă {b['valoare_neta']:.2f} RON | TVA {b['valoare_tva']:.2f} RON | Brut {b['valoare_bruta']:.2f} RON"
        for b in breakdown
    )

    plain_body = (
        f"Comandă nouă #{order['id']} primită pe Torent Distribution (Date facturare / e-Factura)\n"
        f"Data: {order.get('date')}\n"
        f"====================================================================\n"
        f"Client: {cust.get('name', '-')}\n"
        f"Telefon: {cust.get('phone', '-')}\n"
        f"Email: {cust.get('email', '-')}\n"
        f"Adresă: {cust.get('county', '')}, {cust.get('city', '')}, {cust.get('address', '')}\n"
        f"Metodă plată: {order.get('payment_method', '-')}\n"
        f"Acord GDPR CRM: {'DA' if order.get('gdpr_crm_consent') else 'NU'}\n"
        f"====================================================================\n"
        f"Produse comandate (prețuri nete recalculate din brutul plătit):\n"
        + "\n".join(plain_rows) + "\n"
        f"====================================================================\n"
        f"Total Net produse (fără TVA): {total_net:.2f} RON\n"
        f"Total TVA produse:            {total_tva:.2f} RON\n"
        + (f"{breakdown_plain}\n" if breakdown_plain else "")
        + f"Subtotal produse (TVA inclus): {subtotal_brut:.2f} RON\n"
        + f"Transport (TVA inclus):        {shipping_brut:.2f} RON\n"
        + f"TOTAL DE PLATĂ (TVA INCLUS):   {grand_total:.2f} RON\n"
    )

    # HTML version
    html_rows = ""
    for it in items:
        cota = it.get('cota_tva', 21)
        p_net = float(it.get('pret_net_recalculat', 0.0))
        p_brut = float(it.get('pret_brut_unitar', it.get('price', 0.0)))
        v_net = float(it.get('valoare_neta', 0.0))
        v_tva = float(it.get('valoare_tva', 0.0))
        v_brut = float(it.get('valoare_bruta', p_brut * int(it.get('quantity', 1))))
        html_rows += (
            f"<tr>"
            f"<td style='padding:8px;border:1px solid #cbd5e1;'><strong>{it.get('name')}</strong></td>"
            f"<td style='padding:8px;border:1px solid #cbd5e1;text-align:center;'>{it.get('quantity')}</td>"
            f"<td style='padding:8px;border:1px solid #cbd5e1;text-align:center;'>{cota}%</td>"
            f"<td style='padding:8px;border:1px solid #cbd5e1;text-align:right;'>{p_net:.2f} RON</td>"
            f"<td style='padding:8px;border:1px solid #cbd5e1;text-align:right;'>{p_brut:.2f} RON</td>"
            f"<td style='padding:8px;border:1px solid #cbd5e1;text-align:right;'>{v_net:.2f} RON</td>"
            f"<td style='padding:8px;border:1px solid #cbd5e1;text-align:right;'>{v_tva:.2f} RON</td>"
            f"<td style='padding:8px;border:1px solid #cbd5e1;text-align:right;font-weight:700;'>{v_brut:.2f} RON</td>"
            f"</tr>"
        )

    breakdown_html = "".join(
        f"<tr><td style='padding:4px 8px;color:#475569;'>Din care TVA {b['cota_tva']}% (bază {b['valoare_neta']:.2f} RON):</td>"
        f"<td style='padding:4px 8px;text-align:right;font-weight:600;'>{b['valoare_tva']:.2f} RON</td></tr>"
        for b in breakdown
    )

    html_body = f"""<!DOCTYPE html>
<html lang="ro"><body style="font-family:Arial,sans-serif;color:#0f172a;line-height:1.5;">
<h2 style="color:#064e3b;margin-bottom:6px;">Comandă nouă #{order['id']} — Torent Distribution</h2>
<p style="margin-top:0;color:#475569;">Data: {order.get('date')} | Metodă plată: <strong>{order.get('payment_method', '-')}</strong></p>
<div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;padding:12px 16px;margin-bottom:16px;">
  <strong>Client:</strong> {cust.get('name', '-')} &nbsp;|&nbsp;
  <strong>Telefon:</strong> {cust.get('phone', '-')} &nbsp;|&nbsp;
  <strong>Email:</strong> {cust.get('email', '-')}<br>
  <strong>Adresă livrare:</strong> {cust.get('county', '')}, {cust.get('city', '')}, {cust.get('address', '')}
</div>
<table style="width:100%;border-collapse:collapse;font-size:13px;margin-bottom:16px;">
  <thead>
    <tr style="background:#064e3b;color:#ffffff;">
      <th style="padding:8px;border:1px solid #064e3b;text-align:left;">Produs &amp; Ambalaj</th>
      <th style="padding:8px;border:1px solid #064e3b;text-align:center;">Cant.</th>
      <th style="padding:8px;border:1px solid #064e3b;text-align:center;">TVA %</th>
      <th style="padding:8px;border:1px solid #064e3b;text-align:right;">Preț net</th>
      <th style="padding:8px;border:1px solid #064e3b;text-align:right;">Preț brut</th>
      <th style="padding:8px;border:1px solid #064e3b;text-align:right;">Total net</th>
      <th style="padding:8px;border:1px solid #064e3b;text-align:right;">TVA</th>
      <th style="padding:8px;border:1px solid #064e3b;text-align:right;">Total brut</th>
    </tr>
  </thead>
  <tbody>{html_rows}</tbody>
</table>
<table style="margin-left:auto;border-collapse:collapse;font-size:14px;min-width:340px;">
  <tr><td style="padding:5px 8px;">Total Net (fără TVA):</td><td style="padding:5px 8px;text-align:right;font-weight:700;">{total_net:.2f} RON</td></tr>
  <tr><td style="padding:5px 8px;">Total TVA produse:</td><td style="padding:5px 8px;text-align:right;font-weight:700;">{total_tva:.2f} RON</td></tr>
  {breakdown_html}
  <tr><td style="padding:5px 8px;">Transport (TVA inclus):</td><td style="padding:5px 8px;text-align:right;">{shipping_brut:.2f} RON</td></tr>
  <tr style="background:#ecfdf5;color:#064e3b;font-size:16px;">
    <td style="padding:8px;font-weight:800;">TOTAL DE PLATĂ (TVA inclus):</td>
    <td style="padding:8px;text-align:right;font-weight:800;">{grand_total:.2f} RON</td>
  </tr>
</table>
</body></html>"""
    return subject, plain_body, html_body


def send_order_email(order, settings):
    target_email = (settings.get('order_email') or 'vanzari@torentdistribution.ro').strip()
    smtp_host = (settings.get('smtp_host') or '').strip()
    smtp_user = (settings.get('smtp_user') or '').strip()
    smtp_password = (settings.get('smtp_password') or '').strip()
    smtp_port = int(settings.get('smtp_port') or 587)
    smtp_use_tls = bool(settings.get('smtp_use_tls', True))

    subject, plain_body, html_body = build_company_order_email(order)

    if not smtp_host or not smtp_user or not smtp_password:
        return "pending_smtp", f"Destinatar configurat: {target_email} (configurează SMTP în Setări Admin pentru trimitere automată)"

    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = smtp_user
        msg['To'] = target_email
        msg.attach(MIMEText(plain_body, 'plain', 'utf-8'))
        msg.attach(MIMEText(html_body, 'html', 'utf-8'))

        with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
            if smtp_use_tls:
                server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(smtp_user, [target_email], msg.as_string())

            # Optional B2C confirmation email to customer (gross prices, TVA inclus)
            cust = order.get('customer', {})
            cust_email = (cust.get('email') or '').strip()
            if cust_email and '@' in cust_email:
                cust_items = "\n".join(
                    f" - {it.get('name')} x {it.get('quantity')} buc = {float(it.get('valoare_bruta', 0.0)):.2f} RON (TVA inclus)"
                    for it in order.get('items', [])
                )
                cust_body = (
                    f"Bună ziua, {cust.get('name', '')}!\n\n"
                    f"Vă mulțumim pentru comanda #{order['id']} plasată pe Torent Distribution.\n\n"
                    f"Produse comandate:\n{cust_items}\n\n"
                    f"Transport: {float(order.get('shipping_brut', 0.0)):.2f} RON\n"
                    f"TOTAL DE PLATĂ (TVA inclus): {float(order.get('total', 0.0)):.2f} RON\n"
                    f"Metodă plată: {order.get('payment_method', '-')}\n\n"
                    f"Echipa Torent Distribution vă va contacta în cel mai scurt timp pentru confirmarea livrării.\n"
                )
                cmsg = MIMEText(cust_body, 'plain', 'utf-8')
                cmsg['Subject'] = f"Confirmare comandă #{order['id']} - Torent Distribution"
                cmsg['From'] = smtp_user
                cmsg['To'] = cust_email
                server.sendmail(smtp_user, [cust_email], cmsg.as_string())

        return "sent", f"Trimis cu succes la {target_email}"
    except Exception as exc:
        return "error", f"Eroare SMTP către {target_email}: {exc}"

def get_images_list():
    if not os.path.exists(UPLOAD_FOLDER):
        return []
    files = []
    for f in os.listdir(UPLOAD_FOLDER):
        ext = os.path.splitext(f)[1].lower().strip('.')
        if ext in ALLOWED_EXTENSIONS:
            full_path = os.path.join(UPLOAD_FOLDER, f)
            size_kb = round(os.path.getsize(full_path) / 1024, 1)
            files.append({
                "filename": f,
                "url": f"/static/images/products/{f}",
                "size_kb": size_kb
            })
    files.sort(key=lambda x: x['filename'])
    return files

# ----------------- ANTI-SCRAPER & SEO/GEO GUARD ----------------- #

ALLOWED_SEO_GEO_BOTS = (
    'googlebot', 'bingbot', 'duckduckbot', 'applebot', 'slurp', 'yandexbot',
    'gptbot', 'oai-searchbot', 'chatgpt-user', 'perplexitybot', 'claudebot',
    'claude-searchbot', 'anthropic-ai', 'google-extended', 'facebookexternalhit',
    'whatsapp', 'twitterbot', 'linkedinbot'
)

BLOCKED_SCRAPER_SIGNATURES = (
    'scrapy', 'python-requests', 'python-urllib', 'curl/', 'wget/', 'httpie',
    'go-http-client', 'libwww-perl', 'okhttp', 'aiohttp', 'httpx', 'phantomjs',
    'headlesschrome', 'playwright', 'selenium', 'puppeteer', 'mechanize',
    'beautifulsoup', 'httrack', 'ahrefsbot', 'semrushbot', 'mj12bot', 'dotbot',
    'petalbot', 'bytespider', 'barkrowler', 'screaming frog', 'dataforseobot',
    'megaindex', 'node-fetch', 'axios/'
)

RATE_LIMIT_BUCKETS = defaultdict(list)
TOKEN_TTL_SECONDS = 1800  # 30 minutes


def _is_allowed_seo_bot(ua_lower):
    return any(bot in ua_lower for bot in ALLOWED_SEO_GEO_BOTS)


def _is_blocked_scraper(ua_lower):
    if not ua_lower or len(ua_lower) < 10:
        return True
    if _is_allowed_seo_bot(ua_lower):
        return False
    return any(sig in ua_lower for sig in BLOCKED_SCRAPER_SIGNATURES)


def _check_rate_limit(bucket_key, max_requests, window_seconds=60):
    now = time.time()
    timestamps = RATE_LIMIT_BUCKETS[bucket_key]
    cutoff = now - window_seconds
    timestamps = [t for t in timestamps if t > cutoff]
    if len(timestamps) >= max_requests:
        RATE_LIMIT_BUCKETS[bucket_key] = timestamps
        return False
    timestamps.append(now)
    RATE_LIMIT_BUCKETS[bucket_key] = timestamps
    return True


def generate_catalog_token():
    ts = str(int(time.time()))
    nonce = secrets.token_hex(8)
    payload = f"{ts}.{nonce}"
    sig = hmac.new(app.secret_key.encode('utf-8'), payload.encode('utf-8'), hashlib.sha256).hexdigest()[:24]
    return f"{payload}.{sig}"


def verify_catalog_token(token):
    if not token or token.count('.') != 2:
        return False
    ts_str, nonce, sig = token.split('.', 2)
    try:
        ts = int(ts_str)
    except ValueError:
        return False
    if abs(time.time() - ts) > TOKEN_TTL_SECONDS:
        return False
    payload = f"{ts_str}.{nonce}"
    expected_sig = hmac.new(app.secret_key.encode('utf-8'), payload.encode('utf-8'), hashlib.sha256).hexdigest()[:24]
    return hmac.compare_digest(sig, expected_sig)


@app.context_processor
def inject_security_context():
    s = load_settings()
    public_settings = {k: v for k, v in s.items() if not k.startswith('smtp_')}
    host = request.host_url.rstrip('/')
    clean_path = request.path or '/'
    canonical_url = f"{host}{clean_path}"
    active_phone = (public_settings.get('company_phone') or '').strip() or SUPPORT_PHONE
    return {
        "catalog_token": generate_catalog_token(),
        "site_settings": public_settings,
        "SUPPORT_PHONE": active_phone,
        "canonical_url": canonical_url,
        "site_host": host
    }


@app.before_request
def anti_scraper_guard():
    path = request.path or ''
    if path.startswith('/static/') or path.startswith('/admin') or path in ('/robots.txt', '/sitemap.xml', '/llms.txt'):
        return None

    ua_lower = (request.headers.get('User-Agent') or '').strip().lower()
    if _is_blocked_scraper(ua_lower):
        return jsonify({"error": "Acces blocat pentru scripturi automate de colectare a datelor."}), 403

    client_ip = request.headers.get('X-Forwarded-For', request.remote_addr or 'unknown').split(',')[0].strip()

    if path == '/api/products':
        if not _check_rate_limit(f"api:{client_ip}", max_requests=20, window_seconds=60):
            return jsonify({"error": "Prea multe cereri. Vă rugăm încercați din nou într-un minut."}), 429
    elif path.startswith('/produs/') and not _is_allowed_seo_bot(ua_lower):
        if not _check_rate_limit(f"prod:{client_ip}", max_requests=45, window_seconds=60):
            return Response("Prea multe cereri. Vă rugăm așteptați câteva momente.", status=429, mimetype='text/plain')

    return None

# ----------------- SHOP PUBLIC ROUTES ----------------- #

THEMATIC_BG_CATEGORIES = {
    "Pamant de Flori",
    "Ingrasaminte",
    "Produse de Ingrijire plante"
}

CARD_THEME_RULES = [
    (("orhide", "orchid"), "/static/images/card-backgrounds/bg-orhidee.webp"),
    (("muscat", "balcon", "curgatoare", "inflorir", "cu flori", "trandafir"), "/static/images/card-backgrounds/bg-muscate.webp"),
    (("gazon",), "/static/images/card-backgrounds/bg-gazon.webp"),
    (("legum", "rosii", "capsun", "straturi", "rasadur", "gradina"), "/static/images/card-backgrounds/bg-legume.webp"),
    (("conifer", "tuia", "acid", "rododendron", "pin"), "/static/images/card-backgrounds/bg-conifere.webp"),
    (("cactu", "suculent"), "/static/images/card-backgrounds/bg-cactusi.webp"),
    (("frunz", "plante verzi", "camera", "bonsai", "palmier"), "/static/images/card-backgrounds/bg-plante-verzi.webp"),
]


def get_card_theme_bg(product):
    """Return a thematic WebP background path ONLY for Pământ de Flori, Soluții nutritive, and Îngrijire Plante."""
    if not product or product.get('category') not in THEMATIC_BG_CATEGORIES:
        return None
    raw_name = (product.get('name') or '').lower()
    norm = (
        raw_name
        .replace('ă', 'a').replace('â', 'a')
        .replace('î', 'i')
        .replace('ș', 's').replace('ş', 's')
        .replace('ț', 't').replace('ţ', 't')
    )
    for keywords, bg_path in CARD_THEME_RULES:
        if any(kw in norm for kw in keywords):
            return bg_path
    return "/static/images/card-backgrounds/bg-universal.webp"


CATEGORY_SEO = {
    "Pamant de Flori": {
        "slug": "pamant-de-flori",
        "title": "Pământ de Flori & Substraturi 3L-50L – Torent Distribution",
        "description": "Comandă pământ de flori universal, orhidee, mușcate, conifere și răsaduri (Florasol, Humiflor, Nutrisol, Plantasol, Florimo). Livrare rapidă în România.",
        "alt_suffix": "substrat nutritiv pământ de flori"
    },
    "Ingrasaminte": {
        "slug": "solutii-nutritive",
        "title": "Soluții Nutritive & Îngrășăminte – Torent Distribution",
        "description": "Soluții nutritive concentrate și batoane fertilizante Vitaflora, Florasol și Humiflor pentru flori, mușcate, orhidee, gazon, conifere și legume.",
        "alt_suffix": "soluție nutritivă îngrășământ plante"
    },
    "Produse de Ingrijire plante": {
        "slug": "ingrijire-plante",
        "title": "Produse Ecologice Îngrijire Plante – Torent Distribution",
        "description": "Soluții ecologice și organice cu pulverizator Florasol și Nutrisol pentru protecția și fortifierea plantelor de casă, balcon și grădină în România.",
        "alt_suffix": "soluție îngrijire și protecție plante"
    },
    "Ghivece": {
        "slug": "ghivece",
        "title": "Ghivece Ceramice & Jardiniere Balcon – Torent Distribution",
        "description": "Descoperă ghivece ceramice moderne SK, jardiniere de balcon și ghivece suspendate pentru plante de interior și terasă. Livrare rapidă în toată România.",
        "alt_suffix": "ghiveci și jardinieră plante"
    },
    "Decoratiuni": {
        "slug": "decoratiuni",
        "title": "Decorațiuni Grădină & Accesorii – Torent Distribution",
        "description": "Figurine artistice de grădină, decorațiuni tematice și accesorii ornamentale pentru curte, balcon și terasă. Stoc permanent, livrare națională.",
        "alt_suffix": "decorațiune grădină și interior"
    }
}

SLUG_TO_CATEGORY = {v["slug"]: k for k, v in CATEGORY_SEO.items()}


def get_category_slug(cat_key):
    if cat_key in CATEGORY_SEO:
        return CATEGORY_SEO[cat_key]["slug"]
    return re.sub(r'[^a-z0-9]+', '-', (cat_key or '').lower()).strip('-')


def build_product_alt(product):
    if not product:
        return "Produs horticol Torent Distribution"
    name = (product.get("name") or "").strip()
    brand = (product.get("subcategory") or "").strip()
    cat = product.get("category") or ""
    suffix = CATEGORY_SEO.get(cat, {}).get("alt_suffix", "produs horticol")
    parts = [name]
    if brand and brand.lower() not in name.lower():
        parts.append(brand)
    return f"{' '.join(parts)} - {suffix}"


def build_product_title(product):
    """Build a 50-60 char SEO-optimized Romanian product page title."""
    brand_suffix = " – Torent Distribution"
    name = (product.get("name") or "Produs horticol").strip()
    cat_labels = {
        "Pamant de Flori": "Pământ de Flori",
        "Ingrasaminte": "Soluție Nutritivă",
        "Produse de Ingrijire plante": "Îngrijire Plante",
        "Ghivece": "Ghiveci",
        "Decoratiuni": "Decorațiune",
    }
    full = f"{name}{brand_suffix}"
    if len(full) > 60:
        max_name = 60 - len(brand_suffix)
        return f"{name[:max_name].rstrip(' -,')}{brand_suffix}"
    if len(full) < 50:
        extra = cat_labels.get(product.get("category", ""), "Horticultură")
        candidate = f"{name} | {extra}{brand_suffix}"
        if len(candidate) <= 60:
            full = candidate
        if len(full) < 50:
            candidate2 = f"{name} – {extra} | Torent Distribution"
            if len(candidate2) <= 60:
                full = candidate2
    return full


def build_product_meta_desc(product):
    """Build a 140-155 char SEO meta description using unique short_description + B2C gross price."""
    base = (product.get("short_description") or product.get("description") or product.get("name") or "").replace("\n", " ").strip()
    base = re.sub(r"\s+", " ", base)
    price_val = float(product.get("pret_brut", product.get("price", 0.0)))
    if len(base) < 140:
        tail = f" Preț {price_val:.2f} RON (TVA inclus), livrare rapidă RO."
        if len(base) + len(tail) <= 155:
            base = base.rstrip(".") + "." + tail
        else:
            short_tail = f" {price_val:.2f} RON (TVA inclus)."
            if len(base) + len(short_tail) <= 155:
                base = base.rstrip(".") + "." + short_tail
    if len(base) > 155:
        base = base[:152].rsplit(" ", 1)[0].rstrip(".,;:") + "..."
    return base


app.jinja_env.globals['get_card_theme_bg'] = get_card_theme_bg
app.jinja_env.globals['get_category_slug'] = get_category_slug
app.jinja_env.globals['build_product_alt'] = build_product_alt
app.jinja_env.globals['build_product_title'] = build_product_title
app.jinja_env.globals['build_product_meta_desc'] = build_product_meta_desc

def get_active_categories():
    return [c for c in load_categories() if c.get('active', True)]


def get_active_products():
    active_cat_keys = {c['key'] for c in get_active_categories()}
    return [
        p for p in load_products()
        if p.get('active', True) and (not active_cat_keys or p.get('category') in active_cat_keys)
    ]


def _render_catalog_page(active_category=None):
    categories_list = get_active_categories()
    products = get_active_products()
    categories = [c['key'] for c in categories_list]

    subcategories = {
        c['key']: c.get('subcategories', [])
        for c in categories_list
        if c.get('subcategories')
    }

    category_counts = {}
    for c in categories:
        category_counts[c] = len([p for p in products if p.get('category') == c])

    subcat_counts = {}
    for cat, subs in subcategories.items():
        for s in subs:
            subcat_counts[f"{cat}_{s}"] = len([p for p in products if p.get('category') == cat and p.get('subcategory') == s])

    active_cat_obj = None
    page_title = "Torent Distribution – Pământ de Flori și Îngrășăminte RO"
    page_description = "Magazin online de horticultură Torent Distribution: pământ de flori, soluții nutritive și produse de îngrijire plante. Livrare rapidă în toată România."

    if active_category:
        active_cat_obj = next((c for c in categories_list if c['key'] == active_category), None)
        seo_meta = CATEGORY_SEO.get(active_category, {})
        if seo_meta:
            page_title = seo_meta["title"]
            page_description = seo_meta["description"]
        elif active_cat_obj:
            page_title = f"{active_cat_obj['display_name']} – Torent Distribution"
            page_description = (active_cat_obj.get('description') or page_description)[:155]

    return render_template(
        'index.html',
        products=products,
        categories=categories,
        categories_list=categories_list,
        subcategories=subcategories,
        category_counts=category_counts,
        subcat_counts=subcat_counts,
        total_products=len(products),
        active_category=active_category,
        active_cat_obj=active_cat_obj,
        page_title=page_title,
        page_description=page_description
    )


@app.route('/')
def home():
    return _render_catalog_page(active_category=None)


@app.route('/categorie/<slug>')
def category_page(slug):
    cat_key = SLUG_TO_CATEGORY.get(slug)
    if not cat_key:
        for c in get_active_categories():
            if get_category_slug(c['key']) == slug:
                cat_key = c['key']
                break
    if not cat_key:
        return render_template('404.html'), 404
    return _render_catalog_page(active_category=cat_key)

@app.route('/produs/<int:product_id>')
def product_detail(product_id):
    products = get_active_products()
    prod = next((p for p in products if p['id'] == product_id), None)
    if not prod:
        return render_template('404.html'), 404
    related = [p for p in products if p['category'] == prod['category'] and p['id'] != prod['id']][:4]
    return render_template('product_detail.html', product=prod, related=related)

@app.route('/api/products')
def api_products():
    token = request.headers.get('X-Catalog-Token', '')
    xhr = request.headers.get('X-Requested-With', '')
    if xhr != 'XMLHttpRequest' or not verify_catalog_token(token):
        return jsonify({"error": "Acces restricționat. Catalogul poate fi accesat doar prin interfața site-ului."}), 403
    # Strip internal_code so it never leaves the admin area; return only active products
    public_products = []
    for p in get_active_products():
        p_copy = dict(p)
        p_copy.pop('internal_code', None)
        if 'variations' in p_copy and isinstance(p_copy['variations'], list):
            p_copy['variations'] = [
                {k: v for k, v in var.items() if k != 'internal_code'}
                for var in p_copy['variations']
            ]
        public_products.append(p_copy)
    return jsonify(public_products)


@app.route('/llms.txt')
def llms_txt():
    host = request.host_url.rstrip('/')
    llms_path = os.path.join(BASE_DIR, 'llms.txt')
    if os.path.exists(llms_path):
        with open(llms_path, 'r', encoding='utf-8') as f:
            content = f.read()
        # Convert root-relative Markdown links to absolute URLs for AI crawlers
        content = content.replace('](/', f']({host}/')
        return Response(content, mimetype='text/plain; charset=utf-8')
    return Response("# Torent Distribution\n", mimetype='text/plain; charset=utf-8')


@app.route('/robots.txt')
def robots_txt():
    host = request.host_url.rstrip('/')
    lines = [
        "# Torent Distribution - SEO/GEO friendly, Anti-Scraper",
        "User-agent: *",
        "Allow: /",
        "Allow: /categorie/",
        "Allow: /produs/",
        "Allow: /b2b",
        "Allow: /llms.txt",
        "Disallow: /api/",
        "Disallow: /admin/",
        "",
        "# Allow major Search & AI (GEO) crawlers",
        "User-agent: Googlebot",
        "Allow: /",
        "Disallow: /api/",
        "Disallow: /admin/",
        "",
        "User-agent: Bingbot",
        "Allow: /",
        "Disallow: /api/",
        "Disallow: /admin/",
        "",
        "User-agent: OAI-SearchBot",
        "Allow: /",
        "Disallow: /api/",
        "Disallow: /admin/",
        "",
        "User-agent: ChatGPT-User",
        "Allow: /",
        "Disallow: /api/",
        "Disallow: /admin/",
        "",
        "User-agent: GPTBot",
        "Allow: /",
        "Disallow: /api/",
        "Disallow: /admin/",
        "",
        "User-agent: PerplexityBot",
        "Allow: /",
        "Disallow: /api/",
        "Disallow: /admin/",
        "",
        "User-agent: Claude-SearchBot",
        "Allow: /",
        "Disallow: /api/",
        "Disallow: /admin/",
        "",
        "# Block aggressive scraper & competitor intelligence bots",
        "User-agent: AhrefsBot",
        "Disallow: /",
        "User-agent: SemrushBot",
        "Disallow: /",
        "User-agent: MJ12bot",
        "Disallow: /",
        "User-agent: DotBot",
        "Disallow: /",
        "User-agent: Bytespider",
        "Disallow: /",
        "User-agent: Scrapy",
        "Disallow: /",
        "User-agent: HTTrack",
        "Disallow: /",
        "",
        f"Sitemap: {host}/sitemap.xml"
    ]
    return Response("\n".join(lines) + "\n", mimetype='text/plain; charset=utf-8')


@app.route('/sitemap.xml')
def sitemap_xml():
    host = request.host_url.rstrip('/')
    categories_list = get_active_categories()
    products = get_active_products()
    today = datetime.date.today().isoformat()
    urls = [
        f"  <url><loc>{host}/</loc><lastmod>{today}</lastmod><changefreq>daily</changefreq><priority>1.0</priority></url>",
        f"  <url><loc>{host}/b2b</loc><lastmod>{today}</lastmod><changefreq>monthly</changefreq><priority>0.9</priority></url>",
    ]
    for cat in categories_list:
        slug = get_category_slug(cat['key'])
        urls.append(
            f"  <url><loc>{host}/categorie/{slug}</loc><lastmod>{today}</lastmod><changefreq>weekly</changefreq><priority>0.9</priority></url>"
        )
    for p in products:
        urls.append(
            f"  <url><loc>{host}/produs/{p['id']}</loc><lastmod>{today}</lastmod><changefreq>weekly</changefreq><priority>0.8</priority></url>"
        )
    for legal_path in ('/termeni-si-conditii', '/politica-gdpr', '/politica-cookies', '/politica-retur'):
        urls.append(
            f"  <url><loc>{host}{legal_path}</loc><lastmod>{today}</lastmod><changefreq>yearly</changefreq><priority>0.3</priority></url>"
        )
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(urls)
        + "\n</urlset>\n"
    )
    return Response(xml, mimetype='application/xml; charset=utf-8')

# ----------------- LEGAL & COMPLIANCE PAGES (RO / EU) ----------------- #

@app.route('/termeni-si-conditii')
def legal_terms():
    return render_template('legal_page.html', page_type='terms', page_title='Termeni și Condiții')

@app.route('/politica-gdpr')
def legal_gdpr():
    return render_template('legal_page.html', page_type='gdpr', page_title='Politica de Confidențialitate & GDPR')

@app.route('/politica-cookies')
def legal_cookies():
    return render_template('legal_page.html', page_type='cookies', page_title='Politica de Utilizare Cookies')

@app.route('/politica-retur')
def legal_return():
    return render_template('legal_page.html', page_type='return', page_title='Politica de Retur (14 zile)')


# ----------------- B2B / EN-GROS PAGE & FORM API ----------------- #

B2B_ALLOWED_DOMAINS = (
    'Florărie',
    'Magazin de grădinărit / DIY',
    'Peisagistică',
    'Magazin online',
    'Distribuitor',
    'Altele'
)


def load_b2b_requests():
    if not os.path.exists(B2B_REQUESTS_FILE):
        return []
    try:
        with open(B2B_REQUESTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []


def save_b2b_requests(entries):
    with open(B2B_REQUESTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)


def send_b2b_email(entry):
    settings = load_settings()
    target_email = (os.environ.get('B2B_TARGET_EMAIL') or settings.get('order_email') or 'vanzari@torentdistribution.ro').strip()
    smtp_host = (os.environ.get('SMTP_HOST') or settings.get('smtp_host') or '').strip()
    smtp_user = (os.environ.get('SMTP_USER') or settings.get('smtp_user') or '').strip()
    smtp_password = (os.environ.get('SMTP_PASSWORD') or settings.get('smtp_password') or '').strip()
    smtp_port = int(os.environ.get('SMTP_PORT') or settings.get('smtp_port') or 587)
    smtp_use_tls_raw = os.environ.get('SMTP_USE_TLS')
    if smtp_use_tls_raw is not None:
        smtp_use_tls = smtp_use_tls_raw.strip().lower() in ('1', 'true', 'yes', 'on')
    else:
        smtp_use_tls = bool(settings.get('smtp_use_tls', True))

    subject = f"[Website Torent Distribution - B2B] Cerere ofertă nouă - {entry['company_name']}"
    body = (
        "Acest mesaj a fost trimis prin formularul B2B de pe website-ul Torent Distribution.\n"
        "================================================================\n\n"
        f"Data și ora trimiterii: {entry['date']}\n"
        f"Nume firmă:            {entry['company_name']}\n"
        f"CUI / CIF:             {entry['cui']}\n"
        f"Persoană de contact:   {entry['contact_person']}\n"
        f"Telefon:               {entry['phone']}\n"
        f"Email:                 {entry['email']}\n"
        f"Domeniu de activitate: {entry['domain']}\n\n"
        "Mesaj / Produse și cantități de interes:\n"
        "----------------------------------------------------------------\n"
        f"{entry['message'] or '(Niciun mesaj suplimentar)'}\n"
        "----------------------------------------------------------------\n"
    )

    if not smtp_host or not smtp_user or not smtp_password:
        return "pending_smtp", target_email, "SMTP neconfigurat — solicitarea a fost salvată local în data/b2b_requests.json"

    try:
        msg = MIMEText(body, 'plain', 'utf-8')
        msg['Subject'] = subject
        msg['From'] = smtp_user
        msg['To'] = target_email
        msg['Reply-To'] = entry['email']

        if smtp_port == 465 and not smtp_use_tls:
            with smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=10) as server:
                server.login(smtp_user, smtp_password)
                server.sendmail(smtp_user, [target_email], msg.as_string())
        else:
            with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
                if smtp_use_tls:
                    server.starttls()
                server.login(smtp_user, smtp_password)
                server.sendmail(smtp_user, [target_email], msg.as_string())
        return "sent", target_email, f"Trimis cu succes la {target_email}"
    except Exception as exc:
        return "error", target_email, f"Eroare SMTP: {exc}"


@app.route('/b2b')
def b2b_page():
    return render_template('b2b.html')


@app.route('/api/b2b', methods=['POST'])
def api_b2b_submit():
    data = request.get_json() or {}

    # Hidden anti-spam honeypot check
    if (data.get('website_url') or '').strip():
        return jsonify({
            "success": True,
            "message": "Solicitarea dumneavoastră a fost înregistrată. Vă mulțumim!"
        })

    client_ip = request.headers.get('X-Forwarded-For', request.remote_addr or 'unknown').split(',')[0].strip()
    if not _check_rate_limit(f"b2b:{client_ip}", max_requests=10, window_seconds=600):
        return jsonify({
            "success": False,
            "message": "Ați trimis prea multe solicitări într-un interval scurt. Vă rugăm așteptați câteva minute."
        }), 429

    company_name = (data.get('company_name') or '').strip()
    cui = (data.get('cui') or '').strip()
    contact_person = (data.get('contact_person') or '').strip()
    phone = (data.get('phone') or '').strip()
    email = (data.get('email') or '').strip()
    domain = (data.get('domain') or '').strip()
    message = (data.get('message') or '').strip()

    if not company_name or not cui or not contact_person or not phone or not email or not domain:
        return jsonify({
            "success": False,
            "message": "Vă rugăm să completați toate câmpurile obligatorii (Nume firmă, CUI/CIF, Persoană de contact, Telefon, Email, Domeniu de activitate)."
        }), 400

    if not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', email):
        return jsonify({
            "success": False,
            "message": "Adresa de email introdusă nu este validă."
        }), 400

    if domain not in B2B_ALLOWED_DOMAINS:
        domain = 'Altele'

    entries = load_b2b_requests()
    req_id = len(entries) + 1
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    entry = {
        "id": req_id,
        "date": now_str,
        "company_name": company_name,
        "cui": cui,
        "contact_person": contact_person,
        "phone": phone,
        "email": email,
        "domain": domain,
        "message": message
    }

    email_status, target_email, email_info = send_b2b_email(entry)
    entry["email_sent_to"] = target_email
    entry["email_status"] = email_status
    entry["email_info"] = email_info

    entries.insert(0, entry)
    save_b2b_requests(entries)

    return jsonify({
        "success": True,
        "request_id": req_id,
        "email_sent_to": target_email,
        "message": f"Solicitarea B2B pentru {company_name} a fost trimisă cu succes către echipa noastră de vânzări ({target_email})! Vă vom contacta în cel mai scurt timp."
    })


@app.route('/api/order', methods=['POST'])
def api_place_order():
    data = request.get_json()
    if not data or 'items' not in data or not data['items']:
        return jsonify({"success": False, "message": "Coșul de cumpărături este gol!"}), 400

    if not data.get('terms_accepted'):
        return jsonify({"success": False, "message": "Vă rugăm să acceptați Termenii și Condițiile și Politica GDPR pentru a plasa comanda."}), 400

    orders = load_orders()
    order_id = 1000 + len(orders) + 1
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    customer = data.get('customer', {})
    gdpr_crm_consent = bool(data.get('gdpr_crm_consent', False))

    products_catalog = load_products()
    snapshot = compute_order_efactura_snapshot(data.get('items', []), products_catalog)
    total_val = snapshot['total']

    settings = load_settings()
    target_email = settings.get('order_email', 'vanzari@torentdistribution.ro')

    new_order = {
        "id": order_id,
        "customer": customer,
        "items": snapshot['items'],
        "subtotal_brut": snapshot['subtotal_brut'],
        "shipping_brut": snapshot['shipping_brut'],
        "total_net": snapshot['total_net'],
        "total_tva": snapshot['total_tva'],
        "total_brut": snapshot['total_brut'],
        "total": total_val,
        "tva_breakdown": snapshot['tva_breakdown'],
        "payment_method": data.get('payment_method', 'Ramburs la livrare'),
        "status": "Comandă nouă",
        "date": now_str,
        "terms_accepted": True,
        "gdpr_crm_consent": gdpr_crm_consent,
        "email_sent_to": target_email
    }

    email_state, email_info = send_order_email(new_order, settings)
    new_order['email_status'] = email_state
    new_order['email_info'] = email_info

    orders.insert(0, new_order)
    save_orders(orders)

    # Save client to CRM ONLY if GDPR CRM consent was explicitly granted
    if gdpr_crm_consent:
        crm = load_crm()
        cust_email = (customer.get('email') or '').strip().lower()
        cust_phone = (customer.get('phone') or '').strip()

        existing = None
        for c in crm:
            if (cust_email and c.get('email', '').lower() == cust_email) or (cust_phone and c.get('phone') == cust_phone):
                existing = c
                break

        if existing:
            existing['name'] = customer.get('name') or existing.get('name', '')
            if cust_email:
                existing['email'] = customer.get('email', '').strip()
            if cust_phone:
                existing['phone'] = cust_phone
            existing['county'] = customer.get('county') or existing.get('county', '')
            existing['city'] = customer.get('city') or existing.get('city', '')
            existing['address'] = customer.get('address') or existing.get('address', '')
            existing['orders_count'] = int(existing.get('orders_count', 0)) + 1
            existing['total_spent'] = round(float(existing.get('total_spent', 0.0)) + total_val, 2)
            existing['last_order_date'] = now_str
            existing['gdpr_consent_date'] = now_str
        else:
            new_cid = max([c.get('id', 0) for c in crm], default=0) + 1
            crm.insert(0, {
                "id": new_cid,
                "name": customer.get('name', '').strip(),
                "phone": cust_phone,
                "email": customer.get('email', '').strip(),
                "county": customer.get('county', '').strip(),
                "city": customer.get('city', '').strip(),
                "address": customer.get('address', '').strip(),
                "orders_count": 1,
                "total_spent": total_val,
                "first_order_date": now_str,
                "last_order_date": now_str,
                "gdpr_consent": True,
                "gdpr_consent_date": now_str
            })
        save_crm(crm)

    return jsonify({
        "success": True,
        "order_id": order_id,
        "email_sent_to": target_email,
        "crm_saved": gdpr_crm_consent,
        "message": f"Comanda #{order_id} a fost înregistrată și trimisă către {target_email}! Vă mulțumim!"
    })

# ----------------- ADMIN ROUTES ----------------- #

def is_admin_logged():
    return session.get('is_admin') is True

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if is_admin_logged():
        return redirect(url_for('admin_panel'))
    
    error = None
    if request.method == 'POST':
        user = request.form.get('username', '').strip()
        pwd = request.form.get('password', '').strip()
        if user == ADMIN_USERNAME and pwd == ADMIN_PASSWORD:
            session['is_admin'] = True
            session['admin_user'] = user
            return redirect(url_for('admin_panel'))
        else:
            error = "Nume de utilizator sau parolă incorectă!"
            
    return render_template('admin_login.html', error=error)

@app.route('/admin/logout')
def admin_logout():
    session.pop('is_admin', None)
    session.pop('admin_user', None)
    return redirect(url_for('admin_login'))

@app.route('/admin')
def admin_panel():
    if not is_admin_logged():
        return redirect(url_for('admin_login'))
    
    products = load_products()
    orders = load_orders()
    images = get_images_list()
    crm_clients = load_crm()
    settings = load_settings()
    categories_list = load_categories()
    
    categories = [c['key'] for c in categories_list]
    subcategories = {
        c['key']: c.get('subcategories', [])
        for c in categories_list
        if c.get('subcategories')
    }
    category_counts = {
        c['key']: len([p for p in products if p.get('category') == c['key']])
        for c in categories_list
    }
    
    stats = {
        "total_products": len(products),
        "total_categories": len(categories_list),
        "total_orders": len(orders),
        "total_images": len(images),
        "total_crm": len(crm_clients),
        "revenue": sum(o.get('total', 0) for o in orders)
    }
    
    return render_template(
        'admin.html',
        products=products,
        orders=orders,
        images=images,
        crm_clients=crm_clients,
        settings=settings,
        tva_rates=get_tva_rates(settings),
        categories=categories,
        categories_list=categories_list,
        category_counts=category_counts,
        subcategories=subcategories,
        stats=stats
    )


# Admin API: Dynamic TVA Rates Management
@app.route('/admin/api/tva/add', methods=['POST'])
def admin_add_tva_rate():
    if not is_admin_logged():
        return jsonify({"success": False, "message": "Neautorizat"}), 403
    data = request.get_json() or {}
    raw_rate = str(data.get('rate', '')).replace(',', '.').replace('%', '').strip()
    try:
        val = float(raw_rate)
    except ValueError:
        return jsonify({"success": False, "message": "Introduceți o cotă TVA numerică validă (ex: 9, 11, 19, 21)."}), 400
    if val < 0 or val > 100:
        return jsonify({"success": False, "message": "Cota TVA trebuie să fie între 0% și 100%."}), 400
    norm_val = int(val) if val.is_integer() else round(val, 2)

    settings = load_settings()
    rates = get_tva_rates(settings)
    if norm_val in rates:
        return jsonify({"success": True, "tva_rates": rates, "rate": norm_val, "message": f"Cota TVA {norm_val}% există deja în listă."})
    rates.append(norm_val)
    rates = sorted(set(rates))
    settings['tva_rates'] = rates
    save_settings(settings)
    return jsonify({"success": True, "tva_rates": rates, "rate": norm_val, "message": f"Cota nouă de TVA ({norm_val}%) a fost adăugată!"})


@app.route('/admin/api/product/tva/<int:product_id>', methods=['POST'])
def admin_update_product_tva(product_id):
    if not is_admin_logged():
        return jsonify({"success": False, "message": "Neautorizat"}), 403
    data = request.get_json() or {}
    try:
        new_tva = float(str(data.get('cota_tva', '')).replace(',', '.'))
    except ValueError:
        return jsonify({"success": False, "message": "Cotă TVA invalidă."}), 400

    products = load_products()
    prod = next((p for p in products if p['id'] == product_id), None)
    if not prod:
        return jsonify({"success": False, "message": "Produs inexistent."}), 404

    apply_product_tva_pricing(prod, new_tva)
    save_products(products)
    return jsonify({
        "success": True,
        "product": {
            "id": prod['id'],
            "cota_tva": prod['cota_tva'],
            "pret_net": prod['pret_net'],
            "pret_brut": prod['pret_brut'],
            "price": prod['price'],
            "variations": prod.get('variations', [])
        },
        "message": f"TVA actualizat la {prod['cota_tva']}% (Brut: {prod['pret_brut']:.2f} RON)."
    })


# Admin API: Category CRUD
@app.route('/admin/api/category/save', methods=['POST'])
def admin_save_category():
    if not is_admin_logged():
        return jsonify({"success": False, "message": "Neautorizat"}), 403

    data = request.get_json() or {}
    cat_id = data.get('id')
    display_name = (data.get('display_name') or '').strip()
    description = (data.get('description') or '').strip()
    icon = (data.get('icon') or 'fa-leaf').strip()
    unit_label = (data.get('unit_label') or 'produse').strip()
    subcats_raw = (data.get('subcategories') or '').strip()
    subcats = [s.strip() for s in subcats_raw.split(',') if s.strip()] if subcats_raw else []

    if not display_name:
        return jsonify({"success": False, "message": "Denumirea categoriei este obligatorie!"}), 400

    categories_list = load_categories()

    if cat_id:
        try:
            cat_id_int = int(cat_id)
        except ValueError:
            cat_id_int = None
        cat = next((c for c in categories_list if c.get('id') == cat_id_int), None)
        if not cat:
            return jsonify({"success": False, "message": "Categoria nu a fost găsită."}), 404
        cat['display_name'] = display_name
        cat['description'] = description
        cat['icon'] = icon
        cat['unit_label'] = unit_label
        cat['subcategories'] = subcats
        save_categories(categories_list)
        return jsonify({
            "success": True,
            "category": cat,
            "message": f"Categoria „{display_name}” a fost actualizată cu succes!"
        })
    else:
        # Check duplicate key / display_name
        if any(c.get('key', '').lower() == display_name.lower() or c.get('display_name', '').lower() == display_name.lower() for c in categories_list):
            return jsonify({"success": False, "message": f"Categoria „{display_name}” există deja!"}), 400

        new_id = max([c.get('id', 0) for c in categories_list], default=0) + 1
        new_cat = {
            "id": new_id,
            "key": display_name,
            "display_name": display_name,
            "description": description or f"Produse profesionale din categoria {display_name}.",
            "icon": icon,
            "unit_label": unit_label,
            "fallback_image": "/static/images/products/pamant-de-flori-universal-plantasol-5l.png",
            "subcategories": subcats
        }
        categories_list.append(new_cat)
        save_categories(categories_list)
        return jsonify({
            "success": True,
            "category": new_cat,
            "message": f"Categoria nouă „{display_name}” a fost adăugată și poate fi selectată acum la produse!"
        })


@app.route('/admin/api/category/delete/<int:cat_id>', methods=['POST'])
def admin_delete_category(cat_id):
    if not is_admin_logged():
        return jsonify({"success": False, "message": "Neautorizat"}), 403

    categories_list = load_categories()
    cat = next((c for c in categories_list if c.get('id') == cat_id), None)
    if not cat:
        return jsonify({"success": False, "message": "Categoria nu a fost găsită."}), 404

    products = load_products()
    used_count = len([p for p in products if p.get('category') == cat['key']])
    if used_count > 0:
        return jsonify({
            "success": False,
            "message": f"Nu poți șterge categoria „{cat['display_name']}” deoarece conține {used_count} produse. Mută sau șterge produsele mai întâi."
        }), 400

    categories_list = [c for c in categories_list if c.get('id') != cat_id]
    save_categories(categories_list)
    return jsonify({"success": True, "message": f"Categoria „{cat['display_name']}” a fost ștearsă!"})


@app.route('/admin/api/category/toggle-active/<int:cat_id>', methods=['POST'])
def admin_toggle_category_active(cat_id):
    if not is_admin_logged():
        return jsonify({"success": False, "message": "Neautorizat"}), 403

    data = request.get_json() or {}
    is_active = bool(data.get('active', True))
    categories_list = load_categories()
    cat = next((c for c in categories_list if c.get('id') == cat_id), None)
    if not cat:
        return jsonify({"success": False, "message": "Categoria nu a fost găsită."}), 404

    cat['active'] = is_active
    save_categories(categories_list)
    return jsonify({
        "success": True,
        "id": cat_id,
        "active": is_active,
        "message": f"Categoria „{cat['display_name']}” este acum {'ACTIVĂ' if is_active else 'INACTIVĂ'}."
    })


@app.route('/admin/api/product/toggle-active/<int:product_id>', methods=['POST'])
def admin_toggle_product_active(product_id):
    if not is_admin_logged():
        return jsonify({"success": False, "message": "Neautorizat"}), 403

    data = request.get_json() or {}
    is_active = bool(data.get('active', True))
    products = load_products()
    prod = next((p for p in products if p.get('id') == product_id), None)
    if not prod:
        return jsonify({"success": False, "message": "Produsul nu a fost găsit."}), 404

    prod['active'] = is_active
    save_products(products)
    return jsonify({
        "success": True,
        "id": product_id,
        "active": is_active,
        "message": f"Produsul „{prod['name']}” este acum {'ACTIV' if is_active else 'INACTIV'}."
    })


@app.route('/admin/api/order/status/<int:order_id>', methods=['POST'])
def admin_update_order_status(order_id):
    if not is_admin_logged():
        return jsonify({"success": False, "message": "Neautorizat"}), 403

    data = request.get_json() or {}
    new_status = (data.get('status') or '').strip()
    new_status = LEGACY_ORDER_STATUS_MAP.get(new_status, new_status)
    if new_status not in ORDER_STATUSES:
        return jsonify({"success": False, "message": f"Status invalid. Valori permise: {', '.join(ORDER_STATUSES)}"}), 400

    orders = load_orders()
    order = next((o for o in orders if o.get('id') == order_id), None)
    if not order:
        return jsonify({"success": False, "message": "Comanda nu a fost găsită."}), 404

    order['status'] = new_status
    save_orders(orders)
    return jsonify({
        "success": True,
        "order_id": order_id,
        "status": new_status,
        "message": f"Statusul comenzii #{order_id} a fost schimbat în „{new_status}”."
    })

# Admin API: Product CRUD
@app.route('/admin/api/product/save', methods=['POST'])
def admin_save_product():
    if not is_admin_logged():
        return jsonify({"success": False, "message": "Neautorizat"}), 403
    
    products = load_products()
    pid = request.form.get('id', type=int)
    name = request.form.get('name', '').strip()
    category = request.form.get('category', '').strip()
    subcategory = request.form.get('subcategory', '').strip()
    price_net = request.form.get('price', type=float, default=0.0)
    cota_tva_raw = request.form.get('cota_tva', '').strip()
    try:
        cota_tva = float(cota_tva_raw.replace(',', '.')) if cota_tva_raw else float(default_tva_for_category(category))
    except ValueError:
        cota_tva = float(default_tva_for_category(category))
    cota_tva = int(cota_tva) if cota_tva.is_integer() else round(cota_tva, 2)
    stock = request.form.get('stock', type=int, default=10)
    description = request.form.get('description', '').strip()
    image = request.form.get('image', '').strip()
    featured = 'featured' in request.form

    # Optional variations in JSON format (size, pret_net/price, stock, sku, internal_code)
    variations_raw = request.form.get('variations_json', '').strip()
    variations = []
    if variations_raw:
        try:
            parsed_vars = json.loads(variations_raw)
            if isinstance(parsed_vars, list):
                for idx, v in enumerate(parsed_vars):
                    v_size = str(v.get('size', '')).strip() or 'Standard'
                    raw_net = v.get('pret_net', v.get('price', 0))
                    try:
                        v_net_in = float(str(raw_net).replace(',', '.'))
                    except ValueError:
                        v_net_in = 0.0
                    v_net, v_brut = calc_gross_from_net(v_net_in, cota_tva)
                    try:
                        v_stock = int(v.get('stock', 25))
                    except ValueError:
                        v_stock = 25
                    v_internal = str(v.get('internal_code', '')).strip()
                    v_sku = str(v.get('sku', '')).strip() or f"TD-{pid or 100}-{idx + 1}"
                    var_obj = {
                        "size": v_size,
                        "pret_net": v_net,
                        "cota_tva": cota_tva,
                        "pret_brut": v_brut,
                        "price": v_brut,
                        "stock": v_stock,
                        "sku": v_sku
                    }
                    if v_internal:
                        var_obj["internal_code"] = v_internal
                    variations.append(var_obj)
        except Exception:
            variations = []

    if not variations:
        v_net, v_brut = calc_gross_from_net(price_net, cota_tva)
        variations = [{
            "size": "Standard",
            "pret_net": v_net,
            "cota_tva": cota_tva,
            "pret_brut": v_brut,
            "price": v_brut,
            "stock": stock,
            "sku": f"TD-{pid or 100}"
        }]

    min_net = min(v['pret_net'] for v in variations)
    min_brut = min(v['pret_brut'] for v in variations)
    stock = sum(v['stock'] for v in variations)

    # Handle image file upload if provided directly
    if 'image_file' in request.files:
        file = request.files['image_file']
        if file and file.filename and allowed_file(file.filename):
            fname = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], fname))
            image = f"/static/images/products/{fname}"

    if not name or not category:
        return jsonify({"success": False, "message": "Numele și categoria sunt obligatorii!"}), 400

    if pid:
        # Edit existing
        prod = next((p for p in products if p['id'] == pid), None)
        if prod:
            prod['name'] = name
            prod['category'] = category
            prod['subcategory'] = subcategory
            prod['cota_tva'] = cota_tva
            prod['pret_net'] = min_net
            prod['pret_brut'] = min_brut
            prod['price'] = min_brut
            prod['stock'] = stock
            prod['description'] = description
            if image:
                prod['image'] = image
            prod['featured'] = featured
            if variations_raw and variations:
                prod['variations'] = variations
                prod['default_size'] = variations[0]['size']
            elif not prod.get('variations'):
                prod['variations'] = variations
                prod['default_size'] = variations[0]['size']
    else:
        # Add new
        new_id = max([p['id'] for p in products], default=0) + 1
        new_prod = {
            "id": new_id,
            "name": name,
            "category": category,
            "subcategory": subcategory,
            "cota_tva": cota_tva,
            "pret_net": min_net,
            "pret_brut": min_brut,
            "price": min_brut,
            "stock": stock,
            "image": image if image else "/static/images/products/pamant-de-flori-universal-plantasol-5l.webp",
            "description": description,
            "featured": featured,
            "rating": 5.0,
            "reviews_count": 1,
            "variations": variations,
            "default_size": variations[0]['size']
        }
        products.insert(0, new_prod)

    save_products(products)
    return jsonify({"success": True, "message": "Produsul a fost salvat cu succes (prețuri brute recalculate automat)!"})

@app.route('/admin/api/product/delete/<int:product_id>', methods=['POST'])
def admin_delete_product(product_id):
    if not is_admin_logged():
        return jsonify({"success": False, "message": "Neautorizat"}), 403
    
    products = load_products()
    products = [p for p in products if p['id'] != product_id]
    save_products(products)
    return jsonify({"success": True, "message": f"Produsul #{product_id} a fost șters!"})

# Admin API: Image Management (Upload & Delete)
@app.route('/admin/api/image/upload', methods=['POST'])
def admin_upload_image():
    if not is_admin_logged():
        return jsonify({"success": False, "message": "Neautorizat"}), 403
    
    if 'file' not in request.files:
        return jsonify({"success": False, "message": "Niciun fișier selectat!"}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({"success": False, "message": "Niciun fișier selectat!"}), 400
        
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        base, ext = os.path.splitext(filename)
        target = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        counter = 1
        while os.path.exists(target):
            filename = f"{base}_{counter}{ext}"
            target = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            counter += 1
            
        file.save(target)
        file_url = f"/static/images/products/{filename}"
        return jsonify({
            "success": True,
            "message": f"Imaginea {filename} a fost încărcată cu succes!",
            "url": file_url,
            "filename": filename
        })
    else:
        return jsonify({"success": False, "message": "Format fișier nepermis! Permise: png, jpg, jpeg, webp, gif"}), 400

@app.route('/admin/api/image/delete', methods=['POST'])
def admin_delete_image():
    if not is_admin_logged():
        return jsonify({"success": False, "message": "Neautorizat"}), 403
    
    data = request.get_json() or {}
    filename = data.get('filename') or request.form.get('filename')
    if not filename:
        return jsonify({"success": False, "message": "Nume fișier lipsă!"}), 400
        
    safe_name = os.path.basename(filename)
    target_path = os.path.join(app.config['UPLOAD_FOLDER'], safe_name)
    
    if os.path.exists(target_path):
        try:
            os.remove(target_path)
            return jsonify({"success": True, "message": f"Imaginea {safe_name} a fost ștearsă cu succes!"})
        except Exception as e:
            return jsonify({"success": False, "message": f"Eroare la ștergere: {str(e)}"}), 500
    else:
        return jsonify({"success": False, "message": "Fișierul nu a fost găsit pe disc!"}), 404

# Admin API: WooCommerce Export
@app.route('/admin/export-woocommerce-csv')
def admin_export_csv():
    if not is_admin_logged():
        return redirect(url_for('admin_login'))
        
    products = load_products()
    output = StringIO()
    writer = csv.writer(output)
    
    fields = [
        "ID", "Type", "SKU", "Name", "Published", "Is featured?",
        "Visibility in catalog", "Short description", "Description",
        "Tax status", "In stock?", "Stock", "Regular price", "Categories", "Images"
    ]
    writer.writerow(fields)
    
    for p in products:
        cat_hierarchy = f"{p['category']} > {p.get('subcategory', '')}" if p.get('subcategory') else p['category']
        desc = p.get('description', '')
        if p.get('variations') and len(p['variations']) > 1:
            sizes_str = ", ".join([f"{v['size']} ({v['price']:.2f} RON)" for v in p['variations']])
            desc += f"<br><br><strong>Ambalaje disponibile:</strong> {sizes_str}"
            
        writer.writerow([
            p['id'],
            "simple",
            f"TD-{p['id']}",
            p['name'],
            1,
            1 if p.get('featured') else 0,
            "visible",
            p.get('description', '')[:120] + "...",
            desc,
            "taxable",
            1,
            sum(v.get('stock', 25) for v in p.get('variations', [{'stock': 25}])),
            f"{p.get('price', 0.0):.2f}",
            cat_hierarchy,
            p.get('image', '')
        ])
        
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv; charset=utf-8",
        headers={"Content-Disposition": "attachment;filename=torent_woocommerce_products_export.csv"}
    )

@app.route('/admin/export-price-csv')
def admin_export_price_csv():
    if not is_admin_logged():
        return redirect(url_for('admin_login'))

    products = load_products()
    output = StringIO()
    output.write('\ufeff')  # UTF-8 BOM for Romanian Excel
    writer = csv.writer(output, delimiter=';')
    writer.writerow(["cod_intern", "denumire_produs", "marime", "pret_net_ron", "cota_tva", "pret_brut_ron"])

    for p in products:
        cota = p.get('cota_tva', default_tva_for_category(p.get('category', '')))
        vars_list = p.get('variations') or [{
            "size": "Standard",
            "pret_net": p.get('pret_net', p.get('price', 0.0)),
            "pret_brut": p.get('pret_brut', p.get('price', 0.0)),
            "sku": f"TD-{p['id']}"
        }]
        for v in vars_list:
            code = v.get('internal_code') or v.get('sku') or f"TD-{p['id']}"
            v_net = float(v.get('pret_net', v.get('price', 0.0)))
            v_brut = float(v.get('pret_brut', v.get('price', 0.0)))
            writer.writerow([
                code,
                p.get('name', ''),
                v.get('size', 'Standard'),
                f"{v_net:.2f}",
                cota,
                f"{v_brut:.2f}"
            ])

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv; charset=utf-8",
        headers={"Content-Disposition": "attachment;filename=torent_lista_preturi_cod_intern.csv"}
    )


@app.route('/admin/api/prices/import-csv', methods=['POST'])
def admin_import_prices_csv():
    if not is_admin_logged():
        return jsonify({"success": False, "message": "Neautorizat"}), 403

    if 'file' not in request.files:
        return jsonify({"success": False, "message": "Nu a fost selectat niciun fișier CSV."}), 400

    file = request.files['file']
    if not file or not file.filename:
        return jsonify({"success": False, "message": "Fișier invalid."}), 400

    raw_bytes = file.read()
    text = None
    for enc in ('utf-8-sig', 'utf-8', 'cp1250', 'latin-1'):
        try:
            text = raw_bytes.decode(enc)
            break
        except UnicodeDecodeError:
            continue

    if text is None:
        return jsonify({"success": False, "message": "Nu s-a putut decoda fișierul CSV."}), 400

    # Auto-detect delimiter (semicolon, comma, or tab)
    first_line = text.splitlines()[0] if text.splitlines() else ''
    if first_line.count(';') >= first_line.count(',') and first_line.count(';') > 0:
        delimiter = ';'
    elif first_line.count('\t') > 0:
        delimiter = '\t'
    else:
        delimiter = ','

    reader = csv.DictReader(StringIO(text), delimiter=delimiter)
    if not reader.fieldnames:
        return jsonify({"success": False, "message": "Fișierul CSV nu are antet (coloane)."}), 400

    # Match column headers flexibly
    def normalize_col(c):
        return (c or '').strip().lower().replace('ă', 'a').replace('â', 'a').replace('î', 'i').replace('ș', 's').replace('ş', 's').replace('ț', 't').replace('ţ', 't')

    code_col = None
    price_col = None
    tva_col = None
    for col in reader.fieldnames:
        nc = normalize_col(col)
        if code_col is None and any(k in nc for k in ('cod_intern', 'cod intern', 'cod_produs', 'cod produs', 'cod', 'sku')):
            code_col = col
        if price_col is None and any(k in nc for k in ('pret_net', 'pret net', 'pret_ron', 'pret_nou', 'pret nou', 'pret lista', 'pret/buc', 'pret', 'price')) and 'brut' not in nc:
            price_col = col
        if tva_col is None and any(k in nc for k in ('cota_tva', 'cota tva', 'tva', 'vat')):
            tva_col = col

    if not code_col or not price_col:
        return jsonify({
            "success": False,
            "message": f"Nu am găsit coloanele necesare (cod_intern și pret_net_ron / pret_ron). Coloane detectate: {', '.join(reader.fieldnames)}"
        }), 400

    products = load_products()

    # Build lookup index: normalized internal_code (and fallback sku) -> list of (product, variation)
    code_map = {}
    for p in products:
        for v in p.get('variations', []):
            ic = (v.get('internal_code') or '').strip().lower()
            sk = (v.get('sku') or '').strip().lower()
            if ic:
                code_map.setdefault(ic, []).append((p, v))
            if sk and sk != ic:
                code_map.setdefault(sk, []).append((p, v))

    updated_count = 0
    updated_items = []
    not_found_codes = []
    touched_products = set()

    for row in reader:
        raw_code = (row.get(code_col) or '').strip()
        raw_price = (row.get(price_col) or '').strip()
        if not raw_code or not raw_price:
            continue

        # Parse net price (e.g. "15,50 RON" -> 15.50)
        cleaned_price = re.sub(r'[^0-9.,]', '', raw_price).replace(',', '.')
        try:
            new_net_in = float(cleaned_price)
        except ValueError:
            continue

        csv_tva = None
        if tva_col and row.get(tva_col):
            cleaned_tva = re.sub(r'[^0-9.,]', '', str(row.get(tva_col))).replace(',', '.')
            try:
                tva_f = float(cleaned_tva)
                if 0 <= tva_f <= 100:
                    csv_tva = int(tva_f) if tva_f.is_integer() else round(tva_f, 2)
            except ValueError:
                csv_tva = None

        key = raw_code.lower()
        matches = code_map.get(key)
        if not matches:
            not_found_codes.append(raw_code)
            continue

        for prod, var in matches:
            old_net = var.get('pret_net', var.get('price', 0.0))
            old_brut = var.get('pret_brut', var.get('price', 0.0))
            cota_tva = csv_tva if csv_tva is not None else prod.get('cota_tva', default_tva_for_category(prod.get('category', '')))
            prod['cota_tva'] = cota_tva
            new_net, new_brut = calc_gross_from_net(new_net_in, cota_tva)
            var['pret_net'] = new_net
            var['cota_tva'] = cota_tva
            var['pret_brut'] = new_brut
            var['price'] = new_brut
            touched_products.add(prod['id'])
            updated_count += 1
            if len(updated_items) < 30:
                updated_items.append({
                    "code": raw_code,
                    "product": prod['name'],
                    "size": var.get('size', 'Standard'),
                    "cota_tva": cota_tva,
                    "old_net": old_net,
                    "new_net": new_net,
                    "old_price": old_brut,
                    "new_price": new_brut
                })

    # Recalculate base product net/gross prices for all touched products
    for p in products:
        if p['id'] in touched_products and p.get('variations'):
            p['pret_net'] = min(v.get('pret_net', v.get('price', 0.0)) for v in p['variations'])
            p['pret_brut'] = min(v.get('pret_brut', v.get('price', 0.0)) for v in p['variations'])
            p['price'] = p['pret_brut']

    if updated_count > 0:
        save_products(products)

    return jsonify({
        "success": True,
        "updated_count": updated_count,
        "updated_items": updated_items,
        "not_found_codes": not_found_codes[:50],
        "not_found_total": len(not_found_codes),
        "message": f"Actualizare finalizată: {updated_count} prețuri nete importate și recalculate în brut (TVA inclus)!"
    })


@app.route('/admin/api/settings/save', methods=['POST'])
def admin_save_settings():
    if not is_admin_logged():
        return jsonify({"success": False, "message": "Neautorizat"}), 403

    data = request.get_json() or {}
    settings = load_settings()

    order_email = (data.get('order_email') or '').strip()
    if not order_email or '@' not in order_email:
        return jsonify({"success": False, "message": "Introduceți o adresă de email validă pentru comenzi!"}), 400

    settings['order_email'] = order_email
    settings['company_name'] = (data.get('company_name') or settings.get('company_name', '')).strip()
    settings['company_cui'] = (data.get('company_cui') or settings.get('company_cui', '')).strip()
    settings['company_reg_com'] = (data.get('company_reg_com') or settings.get('company_reg_com', '')).strip()
    settings['company_address'] = (data.get('company_address') or settings.get('company_address', '')).strip()
    settings['company_phone'] = (data.get('company_phone') or settings.get('company_phone', '')).strip()

    settings['smtp_host'] = (data.get('smtp_host') or '').strip()
    try:
        settings['smtp_port'] = int(data.get('smtp_port') or 587)
    except ValueError:
        settings['smtp_port'] = 587
    settings['smtp_user'] = (data.get('smtp_user') or '').strip()
    if data.get('smtp_password'):
        settings['smtp_password'] = data.get('smtp_password')
    settings['smtp_use_tls'] = bool(data.get('smtp_use_tls', True))

    save_settings(settings)
    return jsonify({
        "success": True,
        "message": f"Setările au fost salvate! Comenzile vor fi direcționate către {order_email}."
    })


@app.route('/admin/api/crm/delete/<int:client_id>', methods=['POST'])
def admin_delete_crm_client(client_id):
    if not is_admin_logged():
        return jsonify({"success": False, "message": "Neautorizat"}), 403

    crm = load_crm()
    crm = [c for c in crm if c.get('id') != client_id]
    save_crm(crm)
    return jsonify({"success": True, "message": f"Clientul CRM #{client_id} a fost șters definitiv (conform GDPR)."})


@app.route('/admin/export-crm-csv')
def admin_export_crm_csv():
    if not is_admin_logged():
        return redirect(url_for('admin_login'))

    crm = load_crm()
    output = StringIO()
    output.write('\ufeff')
    writer = csv.writer(output, delimiter=';')
    writer.writerow(["ID", "Nume", "Telefon", "Email", "Județ", "Localitate", "Adresă", "Nr. Comenzi", "Total (RON + TVA)", "Acord GDPR", "Data Acord GDPR", "Ultima Comandă"])
    for c in crm:
        writer.writerow([
            c.get('id', ''),
            c.get('name', ''),
            c.get('phone', ''),
            c.get('email', ''),
            c.get('county', ''),
            c.get('city', ''),
            c.get('address', ''),
            c.get('orders_count', 1),
            f"{float(c.get('total_spent', 0)):.2f}",
            "DA" if c.get('gdpr_consent') else "NU",
            c.get('gdpr_consent_date', ''),
            c.get('last_order_date', '')
        ])
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv; charset=utf-8",
        headers={"Content-Disposition": "attachment;filename=torent_crm_clienti_gdpr.csv"}
    )


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5050))
    print("=" * 65)
    print("  PORNIRE WEBSHOP TORENT DISTRIBUTION (HORTICULTURA)")
    print(f"  Site principal: http://127.0.0.1:{port}")
    print(f"  Panou Admin:    http://127.0.0.1:{port}/admin")
    print("  Utilizator:     admin  |  Parola: adminpassword2026")
    print("=" * 65)
    app.run(host='0.0.0.0', port=port, debug=True)
