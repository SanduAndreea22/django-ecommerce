import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from accounts.models import CustomUser # Folosim modelul tău CustomUser

def create_admin():
    username = "admin_render"
    email = "emotional.planner.app@gmail.com"
    password = "ParolaTaPuternica123!" # Pune o parolă sigură aici

    if not CustomUser.objects.filter(username=username).exists():
        CustomUser.objects.create_superuser(username, email, password)
        print(f"Superuser {username} created successfully!")
    else:
        print(f"Superuser {username} already exists.")

if __name__ == "__main__":
    create_admin()