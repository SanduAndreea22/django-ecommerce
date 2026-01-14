# 🛒 Django E-Commerce Pro

**Django E-Commerce** is a full-featured online marketplace platform built with Django. The project has a modular architecture to handle complex retail logic: from product variations, shopping cart, secure checkout, to coupon systems and dashboards for users and admins.

👉 The live site is available here: https://django-ecommerce-c2s6.onrender.com

---

## ✨ Key Features

- ✅ **Advanced Product Management** – categories, product variants, and multiple image galleries.
- ✅ **Dynamic Shopping Cart** – real-time item management and calculations.
- ✅ **Secure Checkout** – order processing and shipping management.
- ✅ **Promotion System** – functional coupons and discounts.
- ✅ **User Dashboards** – profiles and order history tracking.
- ✅ **Admin Tools** – inventory and payment management.

---

## 🏗️ Project Architecture

The project is organized into modular apps, each handling a specific domain of the e-commerce ecosystem:

### 📱 Applications
- **`accounts`** – custom user models, profiles, and authentication.
- **`products`** – catalog: categories, products, and variants.
- **`cart`** – shopping cart logic (session or database).
- **`orders`** – order creation, status, and history.
- **`payments`** – transaction processing and payment verification.
- **`coupons`** – discount code generation and validation.
- **`dashboard`** – admin interface and analytics.

---

## 📊 Main Database Models

| Module | Core Models |
|:---|:---|
| **Identity** | `User`, `Profile` |
| **Catalog** | `Category`, `Product`, `Variant`, `ProductImage` |
| **Shopping** | `CartItem` |
| **Checkout** | `Order`, `OrderItem`, `ShippingAddress` |
| **Financial** | `Payment` |
| **Marketing** | `Coupon` |

---

## 🛠️ Tech Stack

- **Backend:** Django 4.x / Python 3.x
- **Frontend:** HTML5, CSS3, Bootstrap 5
- **Database:** PostgreSQL (Production) / SQLite (Dev)
- **Image Handling:** Pillow
- **Deployment:** Render / Railway

---

## ⚙️ Running Locally

1. **Clone & Navigate:**
```text
git clone https://github.com/SanduAndreea22/django-ecommerce.git
cd django-ecommerce/src
```

2. **Create & activate virtual environment:**
```text
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

3. **Install dependencies:**
```text
pip install -r requirements.txt
```

4. **Initialize database and create superuser:**
```text
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

5. **Run server:**
```text
python manage.py runserver
```

The server will be available at: `http://127.0.0.1:8000/`

---

## 👩‍💻 Author

**Andreea Sandu**  
LinkedIn: [linkedin.com/in/andreealuizasandu](https://linkedin.com/in/andreealuizasandu)  
GitHub: [@SanduAndreea22](https://github.com/SanduAndreea22)

✨ *Built with focus on scalability, clean code, and elegant UI.* ✨
