# src/create_products.py
import os
import django
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from products.models import Category, Product, Variant

# -------------------------------
# 1. Creare categorii
# -------------------------------
categories = [
    "Parfum Femei",
    "Parfum Bărbați",
    "Parfum Unisex",
    "Make-up Buze",
    "Make-up Ochi",
    "Make-up Față",
    "Ceasuri",
    "Posete",
    "Bijuterii",
    "Îngrijire Corp",
]

category_objs = {}
for cat_name in categories:
    slug = cat_name.lower().replace(" ", "-")
    cat_obj, created = Category.objects.get_or_create(name=cat_name, slug=slug)
    category_objs[cat_name] = cat_obj

# -------------------------------
# 2. Produse + variante
# -------------------------------
products_data = [
    # name, category_name, description, base_price, variants [(size, color, stock, sku, price_override)]
    ["Chanel No5", "Parfum Femei", "Parfum clasic elegant", 450, [("50 ml", "N/A", 10, "CHANELNO5-50ML", None)]],
    ["Dior J'adore", "Parfum Femei", "Parfum floral și sofisticat", 400, [("50 ml", "N/A", 12, "DIORJADORE-50ML", None)]],
    ["Gucci Bloom", "Parfum Femei", "Parfum floral modern", 350, [("50 ml", "N/A", 15, "GUCCIBLOOM-50ML", None)]],
    ["Bleu de Chanel", "Parfum Bărbați", "Parfum masculin rafinat", 420, [("50 ml", "N/A", 10, "BLEUDECHANEL-50ML", None)]],
    ["Dior Sauvage", "Parfum Bărbați", "Parfum proaspăt și masculin", 430, [("50 ml", "N/A", 8, "DIORSAUVAGE-50ML", None)]],
    ["CK One", "Parfum Unisex", "Parfum unisex fresh", 300, [("100 ml", "N/A", 20, "CKONE-100ML", None)]],
    ["Tom Ford Neroli Portofino", "Parfum Unisex", "Parfum luxos și proaspăt", 550, [("50 ml", "N/A", 5, "TFNEROLI-50ML", None)]],
    ["Ruj Roșu MAC", "Make-up Buze", "Ruj mat intens", 80, [("Standard", "Roșu", 25, "RUJMAC-RED", None)]],
    ["Luciu de buze", "Make-up Buze", "Luciu strălucitor", 60, [("Standard", "Nude", 30, "LIPGLOSS-NUDE", None)]],
    ["Mascara Negru", "Make-up Ochi", "Mascara volum", 90, [("Standard", "Negru", 20, "MASCARA-BLACK", None)]],
    ["Fard de pleoape", "Make-up Ochi", "Paletă colorată", 120, [("Paletă", "Colorat", 15, "EYESHADOW-COLOR", None)]],
    ["Eyeliner Negru", "Make-up Ochi", "Liner precis", 70, [("Standard", "Negru", 25, "EYELINER-BLACK", None)]],
    ["Fond de ten", "Make-up Față", "Acoperire medie", 150, [("30 ml", "Beige", 20, "FOUNDATION-BEIGE", None)]],
    ["Pudră Translucent", "Make-up Față", "Matifiere fină", 130, [("20 g", "Translucent", 15, "POWDER-TRANSLUCENT", None)]],
    ["Blush Roz", "Make-up Față", "Accentuare obraji", 100, [("15 g", "Roz", 18, "BLUSH-PINK", None)]],
    ["Ceas Michael Kors", "Ceasuri", "Ceas elegant unisex", 850, [("Unisex", "Auriu", 5, "MKWATCH-GOLD", None)]],
    ["Posetă Gucci", "Posete", "Posetă neagră de lux", 2000, [("Standard", "Negru", 3, "GUCCI-BAG-BLACK", None)]],
    ["Colier Argint", "Bijuterii", "Colier delicat argint", 300, [("45 cm", "Argint", 10, "COLIER-SILVER", None)]],
    ["Cremă hidratantă", "Îngrijire Corp", "Hidratează pielea", 120, [("50 ml", "N/A", 20, "CREMA-HIDRATANTA", None)]],
    ["Serum față", "Îngrijire Corp", "Ser facial nutritiv", 180, [("30 ml", "N/A", 15, "SERUM-FATA", None)]],
    ["Șampon", "Îngrijire Corp", "Șampon pentru toate tipurile de păr", 90, [("250 ml", "N/A", 25, "SHAMPOO", None)]],
    ["Loțiune corp", "Îngrijire Corp", "Loțiune hidratantă", 100, [("200 ml", "N/A", 20, "LOTION", None)]],
    ["Set parfum + loțiune", "Parfum Femei", "Set cadou parfum + loțiune", 700, [("50 ml + 200 ml", "N/A", 10, "SET-PARFUM", None)]],
]

for p in products_data:
    cat = category_objs[p[1]]
    product, created = Product.objects.get_or_create(
        name=p[0],
        slug=p[0].lower().replace(" ", "-"),
        category=cat,
        defaults={
            'description': p[2],
            'base_price': p[3],
        }
    )

    # Creare variante
    for var in p[4]:
        size, color, stock, sku, price_override = var
        Variant.objects.get_or_create(
            product=product,
            size=size,
            color=color,
            stock_quantity=stock,
            sku=sku,
            defaults={
                'price_override': price_override
            }
        )

print("Am terminat! 25 de produse create cu variante.")

