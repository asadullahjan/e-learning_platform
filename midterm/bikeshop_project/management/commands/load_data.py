import csv
import os
from collections import defaultdict
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import transaction

from bikeshop_project.models import (
    Customer,
    Product,
    Order,
    Brand,
    Category,
    Store,
    Stock,
    Staff,
    OrderItem,
)


class Command(BaseCommand):
    help = "Load data from CSV files into database using bulk operations"
    project_root = settings.BASE_DIR

    def handle(self, *args, **kwargs):
        with transaction.atomic():
            self.load_brands()
            self.load_customers()
            self.load_categories()
            self.load_products()
            self.load_stores()
            self.load_stocks()
            self.load_staffs()
            self.load_orders()
            self.load_order_items()
        self.stdout.write(self.style.SUCCESS("All data loaded successfully."))

    def load_brands(self):
        """Load brands using bulk_create for better performance"""
        brands = []
        existing_ids = set(Brand.objects.values_list("id", flat=True))

        with open(
            os.path.join(
                self.project_root, "bikeshop_project/data/brands.csv"
            ),
            newline="",
            encoding="utf-8",
        ) as file:
            reader = csv.DictReader(file)
            for row in reader:
                brand_id = int(row["brand_id"])
                if brand_id not in existing_ids:
                    brands.append(Brand(id=brand_id, name=row["brand_name"]))

        if brands:
            Brand.objects.bulk_create(brands, ignore_conflicts=True)
        self.stdout.write(f"Loaded {len(brands)} brands")

    def load_customers(self):
        """Load customers using bulk_create"""
        customers = []
        existing_ids = set(Customer.objects.values_list("id", flat=True))

        with open(
            os.path.join(
                self.project_root, "bikeshop_project/data/customers.csv"
            ),
            newline="",
            encoding="utf-8",
        ) as file:
            reader = csv.DictReader(file)
            for row in reader:
                customer_id = int(row["customer_id"])
                if customer_id not in existing_ids:
                    customers.append(
                        Customer(
                            id=customer_id,
                            first_name=row["first_name"],
                            last_name=row["last_name"],
                            email=row["email"],
                            phone=row["phone"],
                            street=row["street"],
                            city=row["city"],
                            state=row["state"],
                            zip_code=row["zip_code"],
                        )
                    )

        if customers:
            Customer.objects.bulk_create(customers, ignore_conflicts=True)
        self.stdout.write(f"Loaded {len(customers)} customers")

    def load_categories(self):
        """Load categories using bulk_create"""
        categories = []
        existing_ids = set(Category.objects.values_list("id", flat=True))

        with open(
            os.path.join(
                self.project_root, "bikeshop_project/data/categories.csv"
            ),
            newline="",
            encoding="utf-8",
        ) as file:
            reader = csv.DictReader(file)
            for row in reader:
                category_id = int(row["category_id"])
                if category_id not in existing_ids:
                    categories.append(
                        Category(
                            id=category_id,
                            name=row["category_name"],
                        )
                    )

        if categories:
            Category.objects.bulk_create(categories, ignore_conflicts=True)
        self.stdout.write(f"Loaded {len(categories)} categories")

    def load_products(self):
        """Load products using bulk_create with foreign key lookups"""
        products = []
        existing_ids = set(Product.objects.values_list("id", flat=True))

        # Pre-fetch foreign key mappings
        brand_map = {b.id: b for b in Brand.objects.all()}
        category_map = {c.id: c for c in Category.objects.all()}

        with open(
            os.path.join(
                self.project_root, "bikeshop_project/data/products.csv"
            ),
            newline="",
            encoding="utf-8",
        ) as file:
            reader = csv.DictReader(file)
            for row in reader:
                product_id = int(row["product_id"])
                brand_id = int(row["brand_id"])
                category_id = int(row["category_id"])

                if (
                    product_id not in existing_ids
                    and brand_id in brand_map
                    and category_id in category_map
                ):

                    products.append(
                        Product(
                            id=product_id,
                            name=row["product_name"],
                            model_year=int(row["model_year"]),
                            price=Decimal(row["list_price"]),
                            brand=brand_map[brand_id],
                            category=category_map[category_id],
                        )
                    )

        if products:
            Product.objects.bulk_create(products, ignore_conflicts=True)
        self.stdout.write(f"Loaded {len(products)} products")

    def load_stores(self):
        """Load stores using bulk_create"""
        stores = []
        existing_ids = set(Store.objects.values_list("id", flat=True))

        with open(
            os.path.join(
                self.project_root, "bikeshop_project/data/stores.csv"
            ),
            newline="",
            encoding="utf-8",
        ) as file:
            reader = csv.DictReader(file)
            for row in reader:
                store_id = int(row["store_id"])
                if store_id not in existing_ids:
                    stores.append(
                        Store(
                            id=store_id,
                            name=row["store_name"],
                            phone=row["phone"],
                            email=row["email"],
                            street=row["street"],
                            city=row["city"],
                            state=row["state"],
                            zip_code=row["zip_code"],
                        )
                    )

        if stores:
            Store.objects.bulk_create(stores, ignore_conflicts=True)
        self.stdout.write(f"Loaded {len(stores)} stores")

    def load_stocks(self):
        """Load stocks using bulk_create with composite key handling"""
        stocks = []

        # Get existing stock combinations to avoid duplicates
        existing_stocks = set(
            Stock.objects.values_list("store_id", "product_id")
        )

        # Pre-fetch foreign key mappings
        store_map = {s.id: s for s in Store.objects.all()}
        product_map = {p.id: p for p in Product.objects.all()}

        with open(
            os.path.join(
                self.project_root, "bikeshop_project/data/stocks.csv"
            ),
            newline="",
            encoding="utf-8",
        ) as file:
            reader = csv.DictReader(file)
            for row in reader:
                store_id = int(row["store_id"])
                product_id = int(row["product_id"])

                if (
                    (store_id, product_id) not in existing_stocks
                    and store_id in store_map
                    and product_id in product_map
                ):

                    stocks.append(
                        Stock(
                            store=store_map[store_id],
                            product=product_map[product_id],
                            quantity=int(row["quantity"].strip() or 0),
                        )
                    )

        if stocks:
            Stock.objects.bulk_create(stocks, ignore_conflicts=True)
        self.stdout.write(f"Loaded {len(stocks)} stock records")

    def load_staffs(self):
        """Load staff in two passes: first without managers, then update managers"""
        # First pass: create staff without manager relationships
        staff_list = []
        existing_ids = set(Staff.objects.values_list("id", flat=True))
        store_map = {s.id: s for s in Store.objects.all()}

        staff_data = []  # Store for second pass

        with open(
            os.path.join(
                self.project_root, "bikeshop_project/data/staffs.csv"
            ),
            newline="",
            encoding="utf-8",
        ) as file:
            reader = csv.DictReader(file)
            for row in reader:
                staff_data.append(row)
                staff_id = int(row["staff_id"])
                store_id = int(row["store_id"])

                if staff_id not in existing_ids and store_id in store_map:

                    staff_list.append(
                        Staff(
                            id=staff_id,
                            first_name=row["first_name"],
                            last_name=row["last_name"],
                            email=row["email"],
                            phone=row["phone"],
                            active=row["active"] == "1",
                            store=store_map[store_id],
                        )
                    )

        if staff_list:
            Staff.objects.bulk_create(staff_list, ignore_conflicts=True)

        # Second pass: update manager relationships
        staff_map = {s.id: s for s in Staff.objects.all()}
        updates = []

        for row in staff_data:
            if row["manager_id"]:
                staff_id = int(row["staff_id"])
                manager_id = int(row["manager_id"])

                if staff_id in staff_map and manager_id in staff_map:
                    staff = staff_map[staff_id]
                    staff.manager = staff_map[manager_id]
                    updates.append(staff)

        if updates:
            Staff.objects.bulk_update(updates, ["manager"])

        self.stdout.write(f"Loaded {len(staff_list)} staff members")

    def load_orders(self):
        """Load orders using bulk_create"""
        orders = []
        existing_ids = set(Order.objects.values_list("id", flat=True))

        # Pre-fetch foreign key mappings
        customer_map = {c.id: c for c in Customer.objects.all()}
        store_map = {s.id: s for s in Store.objects.all()}
        staff_map = {s.id: s for s in Staff.objects.all()}

        with open(
            os.path.join(
                self.project_root, "bikeshop_project/data/orders.csv"
            ),
            newline="",
            encoding="utf-8",
        ) as file:
            reader = csv.DictReader(file)
            for row in reader:
                order_id = int(row["order_id"])
                customer_id = int(row["customer_id"])
                store_id = int(row["store_id"])
                staff_id = int(row["staff_id"])

                if (
                    order_id not in existing_ids
                    and customer_id in customer_map
                    and store_id in store_map
                    and staff_id in staff_map
                ):

                    orders.append(
                        Order(
                            id=order_id,
                            order_status=row["order_status"],
                            order_date=self.parse_date(row["order_date"]),
                            expected_delivery_date=self.parse_date(
                                row["required_date"]
                            ),
                            shipped_date=self.parse_date(row["shipped_date"]),
                            customer=customer_map[customer_id],
                            store=store_map[store_id],
                            staff=staff_map[staff_id],
                        )
                    )

        if orders:
            Order.objects.bulk_create(orders, ignore_conflicts=True)
        self.stdout.write(f"Loaded {len(orders)} orders")

    def load_order_items(self):
        """Load order items using bulk_create with composite key handling"""
        order_items = []

        # Get existing order item combinations to avoid duplicates
        existing_items = set(
            OrderItem.objects.values_list("order_id", "product_id")
        )

        # Pre-fetch foreign key mappings
        order_map = {o.id: o for o in Order.objects.all()}
        product_map = {p.id: p for p in Product.objects.all()}

        with open(
            os.path.join(
                self.project_root, "bikeshop_project/data/order_items.csv"
            ),
            newline="",
            encoding="utf-8",
        ) as file:
            reader = csv.DictReader(file)
            for row in reader:
                order_id = int(row["order_id"])
                product_id = int(row["product_id"])

                if (
                    (order_id, product_id) not in existing_items
                    and order_id in order_map
                    and product_id in product_map
                ):

                    order_items.append(
                        OrderItem(
                            order=order_map[order_id],
                            product=product_map[product_id],
                            quantity=int(row["quantity"].strip() or 0),
                            price=Decimal(row["list_price"]),
                            discount=Decimal(row["discount"].strip() or 0),
                        )
                    )

        if order_items:
            OrderItem.objects.bulk_create(order_items, ignore_conflicts=True)
        self.stdout.write(f"Loaded {len(order_items)} order items")

    @staticmethod
    def parse_date(value):
        """Parse date value, returning None for empty/null values"""
        if value in ("", "NULL", None):
            return None
        return value
