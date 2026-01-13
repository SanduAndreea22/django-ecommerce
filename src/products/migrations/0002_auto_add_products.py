# products/migrations/0002_auto_add_products.py
from django.db import migrations


def add_products(apps, schema_editor):
    Product = apps.get_model('products', 'Product')

    products_data = [
        ["Chanel No5", "Femei", "50 ml", None, 450, 10, "chanel-no5"],
        ["Dior J’adore", "Femei", "50 ml", None, 400, 12, "dior-jadore"],
        ["Gucci Bloom", "Femei", "50 ml", None, 350, 15, "gucci-bloom"],
        ["Bleu de Chanel", "Bărbați", "50 ml", None, 420, 10, "bleu-de-chanel"],
        ["Dior Sauvage", "Bărbați", "50 ml", None, 430, 8, "dior-sauvage"],
        ["CK One", "Unisex", "100 ml", None, 300, 20, "ck-one"],
        ["Tom Ford Neroli Portofino", "Unisex", "50 ml", None, 550, 5, "tom-ford-neroli"],
        ["Ruj roșu", "Buze", "Standard", "Roșu", 80, 25, "ruj-rosu"],
        ["Luciu de buze", "Buze", "Standard", "Nude", 60, 30, "luciu-buze"],
        ["Mascara", "Ochi", "Standard", "Negru", 90, 20, "mascara-negru"],
        ["Fard de pleoape", "Ochi", "Paletă", "Colorat", 120, 15, "fard-pleoape"],
        ["Eyeliner", "Ochi", "Standard", "Negru", 70, 25, "eyeliner-negru"],
        ["Fond de ten", "Față", "30 ml", "Beige", 150, 20, "fond-ten-beige"],
        ["Pudră", "Față", "20 g", "Translucent", 130, 15, "pudra-translucent"],
        ["Blush", "Față", "15 g", "Roz", 100, 18, "blush-roz"],
        ["Ceas Michael Kors", "Ceasuri", "Unisex", "Auriu", 850, 5, "ceas-mk-auriu"],
        ["Posetă Gucci", "Posete", "Standard", "Negru", 2000, 3, "poseta-gucci-negru"],
        ["Colier", "Bijuterii", "45 cm", "Argint", 300, 10, "colier-argint"],
        ["Cremă hidratantă", "Față", "50 ml", None, 120, 20, "crema-hidratanta"],
        ["Serum", "Față", "30 ml", None, 180, 15, "serum-fata"],
        ["Șampon", "Păr", "250 ml", None, 90, 25, "sampon-par"],
        ["Loțiune corp", "Corp", "200 ml", None, 100, 20, "lotiune-corp"],
        ["Set parfum + loțiune", "Parfum", "50 ml + 200 ml", None, 700, 10, "set-parfum-lotiune"]
    ]

    for p in products_data:
        Product.objects.get_or_create(
            name=p[0],
            slug=p[6],
            defaults={
                'price': p[4],  # ajustează dacă în model e 'pret'
                'stock': p[5],  # ajustează dacă în model e 'stoc'
                'description': f"Categorie: {p[1]}, Varianta: {p[2]}",
            }
        )


class Migration(migrations.Migration):
    dependencies = [
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_products),
    ]
