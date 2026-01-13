# src/create_products.py
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from products.models import Product, Category

# -------------------------------
# Categoriile
# -------------------------------
categories = [
    "Parfumuri Femei",
    "Parfumuri Bărbați",
    "Parfumuri Unisex",
    "Machiaj Buze",
    "Machiaj Ochi",
    "Machiaj Față",
    "Îngrijire Păr",
    "Îngrijire Corp",
    "Bijuterii",
    "Ceasuri",
    "Posete"
]

category_objects = {}
for name in categories:
    slug = name.lower().replace(" ", "-")
    obj, created = Category.objects.get_or_create(name=name, slug=slug)
    category_objects[name] = obj

# -------------------------------
# Produsele
# -------------------------------
products_data = [
    ["Chanel No5", "Parfumuri Femei", "50 ml", None, 450, 10, "chanel-no5"],
    ["Dior J'adore", "Parfumuri Femei", "50 ml", None, 400, 12, "dior-jadore"],
    ["Gucci Bloom", "Parfumuri Femei", "50 ml", None, 350, 15, "gucci-bloom"],
    ["Bleu de Chanel", "Parfumuri Bărbați", "50 ml", None, 420, 10, "bleu-de-chanel"],
    ["Dior Sauvage", "Parfumuri Bărbați", "50 ml", None, 430, 8, "dior-sauvage"],
    ["CK One", "Parfumuri Unisex", "100 ml", None, 300, 20, "ck-one"],
    ["Tom Ford Neroli Portofino", "Parfumuri Unisex", "50 ml", None, 550, 5, "tom-ford-neroli"],
    ["Ruj Roșu", "Machiaj Buze", "Standard", "Roșu", 80, 25, "ruj-rosu"],
    ["Luciu de buze", "Machiaj Buze", "Standard", "Nude", 60, 30, "luciu-buze"],
    ["Mascara", "Machiaj Ochi", "Standard", "Negru", 90, 20, "mascara-negru"],
    ["Fard de pleoape", "Machiaj Ochi", "Paletă", "Colorat", 120, 15, "fard-pleoape"],
    ["Eyeliner", "Machiaj Ochi", "Standard", "Negru", 70, 25, "eyeliner-negru"],
    ["Fond de ten", "Machiaj Față", "30 ml", "Beige", 150, 20, "fond-ten-beige"],
    ["Pudră", "Machiaj Față", "20 g", "Translucent", 130, 15, "pudra-translucent"],
    ["Blush", "Machiaj Față", "15 g", "Roz", 100, 18, "blush-roz"],
    ["Ceas Michael Kors", "Ceasuri", "Unisex", "Auriu", 850, 5, "ceas-mk-auriu"],
    ["Posetă Gucci", "Posete", "Standard", "Negru", 2000, 3, "poseta-gucci-negru"],
    ["Colier Argint", "Bijuterii", "45 cm", "Argint", 300, 10, "colier-argint"],
    ["Cremă hidratantă", "Îngrijire Corp", "50 ml", None, 120, 20, "crema-hidratanta"],
    ["Serum", "Îngrijire Față", "30 ml", None, 180, 15, "serum-fata"],
    ["Șampon", "Îngrijire Păr", "250 ml", None, 90, 25, "sampon-par"],
    ["Loțiune corp", "Îngrijire Corp", "200 ml", None, 100, 20, "lotiune-corp"],
    ["Set parfum + loțiune", "Parfumuri Femei", "50 ml + 200 ml", None, 700, 10, "set-parfum-lotiune"],
    ["Creion sprâncene", "Machiaj Ochi", "Standard", "Maro", 50, 20, "creion-sprancene"],
    ["Balsam de buze", "Machiaj Buze", "5 g", "Translucent", 40, 30, "balsam-buze"]
]

for p in products_data:
    category = category_objects[p[1]]
    Product.objects.get_or_create(
        name=p[0],
        slug=p[6],
        defaults={
            "category": category,
            "size": p[2],
            "color": p[3] if p[3] else "",
            "price": p[4],
            "stock": p[5],
            "description": f"{p[0]} – categorie: {p[1]}, dimensiune: {p[2]}"
        }
    )

print("✅ 25 de produse create cu succes!")
