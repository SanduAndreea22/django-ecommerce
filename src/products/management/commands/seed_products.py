import random

from django.core.management.base import BaseCommand
from django.utils.text import slugify

from products.models import Category, Product, Variant

CATEGORIES = ["Body Care", "Fragrance", "Hair Care", "Skincare", "Makeup"]

PRODUCTS = [
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

COLORS_BY_CATEGORY = {
    "Fragrance": ["Transparent"],
    "Skincare": ["White", "Beige", "Light Pink"],
    "Body Care": ["White", "Beige", "Cream"],
    "Hair Care": ["Clear", "White", "Yellowish"],
    "Makeup": ["Red", "Pink", "Nude", "Brown", "Black"],
}


class Command(BaseCommand):
    help = "Populează catalogul cu categorii, produse și variante demo. Sigur de rulat de mai multe ori (idempotent)."

    def handle(self, *args, **options):
        category_objs = {}
        for name in CATEGORIES:
            category, _ = Category.objects.get_or_create(name=name, slug=slugify(name))
            category_objs[name] = category

        products_created = 0
        variants_created = 0

        for name, category_name, base_price, sizes in PRODUCTS:
            slug = slugify(name)
            category = category_objs[category_name]

            product, created = Product.objects.get_or_create(
                slug=slug,
                defaults={
                    "name": name,
                    "category": category,
                    "base_price": base_price,
                    "description": f"{name} - available in various sizes and colors.",
                },
            )
            if created:
                products_created += 1

            for size in sizes:
                for color in COLORS_BY_CATEGORY[category_name]:
                    sku = f"{slug.upper()}-{size.replace(' ', '').upper()}-{color.upper()}"
                    _, created = Variant.objects.get_or_create(
                        sku=sku,
                        defaults={
                            "product": product,
                            "size": size,
                            "color": color,
                            "price_override": None,
                            "stock_quantity": random.randint(5, 50),
                        },
                    )
                    if created:
                        variants_created += 1

        self.stdout.write(self.style.SUCCESS(
            f"Seed complet: {products_created} produse noi, {variants_created} variante noi "
            f"({len(category_objs)} categorii)."
        ))
