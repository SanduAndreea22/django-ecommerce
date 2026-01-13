import os
import django
import random
from django.utils.text import slugify

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from products.models import Category, Product, Variant

# -------------------------
# Categorii
# -------------------------
categories = ["Parfumuri", "Machiaj", "Îngrijire corp"]
category_objs = {}

for cat_name in categories:
    slug = slugify(cat_name)
    cat_obj, _ = Category.objects.get_or_create(name=cat_name, slug=slug)
    category_objs[cat_name] = cat_obj

# -------------------------
# Produse și variante
# -------------------------
products_data = [
    # Parfumuri
    ("YSL Libre", "Parfum elegant floral-fructat", "Parfumuri", ["30 ml", "50 ml", "100 ml"]),
    ("Lancôme La Vie Est Belle", "Parfum dulce-floral", "Parfumuri", ["30 ml", "50 ml", "100 ml"]),
    ("Armani Si", "Parfum fructat-chypre", "Parfumuri", ["30 ml", "50 ml", "100 ml"]),
    ("Viktor&Rolf Flowerbomb", "Parfum oriental-floral", "Parfumuri", ["30 ml", "50 ml", "100 ml"]),
    ("Prada Paradoxe", "Parfum floral-lemnos", "Parfumuri", ["30 ml", "50 ml", "100 ml"]),
    ("Paco Rabanne 1 Million", "Parfum lemnos-condimentat", "Parfumuri", ["50 ml", "100 ml"]),
    ("Versace Eros", "Parfum aromatic-lemnos", "Parfumuri", ["50 ml", "100 ml"]),
    ("Jean Paul Gaultier Le Male", "Parfum oriental-fresch", "Parfumuri", ["50 ml", "100 ml"]),
    ("Baccarat Rouge 540", "Parfum lemnos-amber", "Parfumuri", ["50 ml", "100 ml"]),
    ("Byredo Gypsy Water", "Parfum lemnos-picant", "Parfumuri", ["50 ml", "100 ml"]),

    # Machiaj
    ("Ruj MAC Matte", "Ruj mat intens", "Machiaj", ["1.5 g"], ["Roșu", "Roz", "Nude"]),
    ("Estée Lauder Double Wear", "Fond de ten rezistent", "Machiaj", ["30 ml"], ["Bej", "Olive", "Almond"]),
    ("Too Faced Better Than Sex", "Mascara voluminoasă", "Machiaj", ["10 ml"], ["Negru"]),
    ("NARS Radiant Concealer", "Corector luminos", "Machiaj", ["6 ml"], ["Bej", "Sand", "Medium"]),

    # Îngrijire corp
    ("Jo Malone Wood Sage", "Apă de toaletă relaxantă", "Îngrijire corp", ["100 ml", "200 ml"]),
    ("Carolina Herrera Good Girl", "Apă de parfum sofisticată", "Îngrijire corp", ["100 ml", "200 ml"]),
    ("Mugler Alien", "Parfum floral-oriental", "Îngrijire corp", ["100 ml", "200 ml"]),
    ("Valentino Born in Roma", "Parfum floral-lemnos", "Îngrijire corp", ["100 ml", "200 ml"]),
    ("Dior Homme Intense", "Parfum lemnos-oriental", "Îngrijire corp", ["100 ml", "200 ml"]),
    ("Guerlain Mon Guerlain", "Parfum oriental-floral", "Îngrijire corp", ["100 ml", "200 ml"]),
    ("Chanel Coco Mademoiselle", "Parfum floral-lemnos", "Îngrijire corp", ["100 ml", "200 ml"]),
    ("Hermès Twilly", "Parfum fresh-floral", "Îngrijire corp", ["100 ml", "200 ml"]),
    ("Lancôme Idôle", "Parfum floral-modern", "Îngrijire corp", ["100 ml", "200 ml"]),
    ("Dior Sauvage", "Parfum aromatic-fresh", "Îngrijire corp", ["100 ml", "200 ml"]),
    ("Tom Ford Black Orchid", "Parfum oriental-floral", "Îngrijire corp", ["100 ml", "200 ml"]),
    ("Chanel Bleu de Chanel", "Parfum lemnos-aromatic", "Îngrijire corp", ["100 ml", "200 ml"]),
    ("Givenchy L'Interdit", "Parfum floral-oriental", "Îngrijire corp", ["100 ml", "200 ml"]),
    ("Yves Saint Laurent Black Opium", "Parfum oriental-vanilat", "Îngrijire corp", ["100 ml", "200 ml"]),
    ("Gucci Bloom", "Parfum floral", "Îngrijire corp", ["100 ml", "200 ml"]),
    ("Armani Code", "Parfum lemnos-oriental", "Îngrijire corp", ["100 ml", "200 ml"]),
    ("Burberry Her", "Parfum fructat-floral", "Îngrijire corp", ["100 ml", "200 ml"])
]

# -------------------------
# Creare produse și variante
# -------------------------
for p in products_data:
    name = p[0]
    description = p[1]
    category_name = p[2]
    sizes = p[3]
    colors = p[4] if len(p) > 4 else ["Clasic"]

    # slug unic
    slug = slugify(name)

    # Product
    product, created = Product.objects.get_or_create(
        name=name,
        slug=slug,
        category=category_objs[category_name],
        description=description,
        base_price=random.randint(50, 300),
        is_active=True
    )

    # Variants
    for size in sizes:
        for color in colors:
            sku = f"{slug.upper()}-{size.replace(' ', '').upper()}-{color.upper()}"
            Variant.objects.get_or_create(
                product=product,
                size=size,
                color=color,
                sku=sku,
                price_override=None,
                stock_quantity=random.randint(5, 50),
                is_active=True
            )

print("✅ 30 produse cu variante create!")

