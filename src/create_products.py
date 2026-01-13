# src/create_products.py
import os
import django
import random

from django.utils.text import slugify

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from products.models import Category, Product, Variant

# -------------------------------
# Categories (English)
# -------------------------------
categories = [
    "Body Care",
    "Fragrance",
    "Hair Care",
    "Skincare",
    "Makeup"
]

category_objs = {}
for cat_name in categories:
    slug = slugify(cat_name)
    cat_obj, _ = Category.objects.get_or_create(name=cat_name, slug=slug)
    category_objs[cat_name] = cat_obj

# -------------------------------
# Products (realistic)
# -------------------------------
products = [
    # Fragrances
    ("Dior J'adore Eau de Parfum", "Fragrance", 120.00, ["50ml", "100ml", "150ml"]),
    ("Chanel No.5 Eau de Parfum", "Fragrance", 130.00, ["50ml", "100ml"]),
    ("Jo Malone Peony & Blush Suede", "Fragrance", 140.00, ["30ml", "100ml"]),
    ("Yves Saint Laurent Black Opium", "Fragrance", 115.00, ["50ml", "90ml"]),
    ("Tom Ford Black Orchid", "Fragrance", 150.00, ["50ml", "100ml"]),

    # Skincare
    ("L'Oreal Revitalift Night Cream", "Skincare", 25.50, ["50ml"]),
    ("Neutrogena Hydro Boost Gel Cream", "Skincare", 18.99, ["48ml", "100ml"]),
    ("Clinique Moisture Surge 72H", "Skincare", 49.99, ["50ml", "100ml"]),
    ("Estee Lauder Advanced Night Repair", "Skincare", 85.00, ["30ml", "50ml", "75ml"]),
    ("Garnier Micellar Water", "Skincare", 5.99, ["100ml", "200ml"]),

    # Body Care
    ("Dove Nourishing Body Wash", "Body Care", 9.50, ["250ml", "500ml"]),
    ("Lush Body Lotion", "Body Care", 15.50, ["100ml", "250ml"]),
    ("Bath & Body Works Body Cream", "Body Care", 22.00, ["200ml"]),
    ("Nivea Soft Moisturizing Cream", "Body Care", 7.50, ["50ml", "100ml"]),
    ("The Body Shop Shea Body Butter", "Body Care", 20.00, ["200ml"]),

    # Hair Care
    ("Pantene Pro-V Shampoo", "Hair Care", 8.50, ["250ml", "500ml"]),
    ("Herbal Essences Conditioner", "Hair Care", 6.99, ["200ml", "400ml"]),
    ("Tresemmé Keratin Smooth Shampoo", "Hair Care", 7.99, ["250ml", "500ml"]),
    ("Garnier Fructis Hair Mask", "Hair Care", 12.50, ["300ml"]),

    # Makeup
    ("Maybelline Mascara Lash Sensational", "Makeup", 12.99, ["One Size"]),
    ("NYX Soft Matte Lip Cream", "Makeup", 9.99, ["One Size"]),
    ("Revlon ColorStay Foundation", "Makeup", 14.50, ["30ml", "50ml"]),
    ("MAC Lipstick Ruby Woo", "Makeup", 19.50, ["One Size"]),
    ("Urban Decay Naked Eyeshadow Palette", "Makeup", 49.99, ["One Size"]),
]

# -------------------------------
# Realistic colors for products
# -------------------------------
colors = {
    "Fragrance": ["Transparent"],
    "Skincare": ["White", "Beige", "Light Pink"],
    "Body Care": ["White", "Beige", "Cream"],
    "Hair Care": ["Clear", "White", "Yellowish"],
    "Makeup": ["Red", "Pink", "Nude", "Brown", "Black"]
}

# -------------------------------
# Create products & variants
# -------------------------------
for name, cat_name, base_price, sizes in products:
    slug = slugify(name)
    category = category_objs[cat_name]

    product, created = Product.objects.get_or_create(
        slug=slug,
        defaults={
            "name": name,
            "category": category,
            "base_price": base_price,
            "description": f"{name} - available in various sizes and colors."
        }
    )

    for size in sizes:
        for color in colors[cat_name]:
            sku = f"{slug.upper()}-{size.replace(' ', '').upper()}-{color.upper()}"
            if not Variant.objects.filter(sku=sku).exists():
                Variant.objects.create(
                    product=product,
                    size=size,
                    color=color,
                    price_override=None,
                    stock_quantity=random.randint(5, 50),
                    sku=sku
                )

print("✅ Realistic products and variants created successfully!")


