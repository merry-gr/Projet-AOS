#!/usr/bin/env python
import os
import sys
import django

# Add the product service to the Python path
sys.path.append('c:/microservices/product_service')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from products.models import Product

def create_test_products():
    # Create some test products
    products_data = [
        {
            'vendor_id': 1,
            'name': 'Test Product',
            'description': 'This is a test medical product for demonstration purposes.',
            'category': 'materiel_medical',
            'price': 1500.00,
            'stock': 50,
        },
        {
            'vendor_id': 1,
            'name': 'Paracitamol',
            'description': 'Common pain reliever and fever reducer medication.',
            'category': 'medicament',
            'price': 25.50,
            'stock': 100,
        },
        {
            'vendor_id': 2,
            'name': 'Medical Scanner',
            'description': 'High-quality medical imaging scanner for diagnostic purposes.',
            'category': 'diagnostic',
            'price': 150000.00,
            'stock': 5,
        },
        {
            'vendor_id': 2,
            'name': 'Medical Gloves',
            'description': 'Disposable medical gloves for protection and hygiene.',
            'category': 'protection',
            'price': 15.00,
            'stock': 500,
        }
    ]
    
    created_count = 0
    for product_data in products_data:
        product, created = Product.objects.get_or_create(
            name=product_data['name'],
            defaults=product_data
        )
        if created:
            created_count += 1
            print(f"Created product: {product.name}")
        else:
            print(f"Product already exists: {product.name}")
    
    print(f"\nTotal products in database: {Product.objects.count()}")
    print(f"New products created: {created_count}")
    
    # List all products
    print("\nAll products:")
    for product in Product.objects.all():
        print(f"- {product.name} ({product.category}) - {product.price} DA - Stock: {product.stock}")

if __name__ == '__main__':
    create_test_products()
