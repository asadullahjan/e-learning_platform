import csv
import os

from decimal import Decimal
from django.core.management.base import BaseCommand
from django.conf import settings

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
    help = "Load data from CSV files into database"
    project_root = settings.BASE_DIR

    def handle(self, *args, **kwargs):
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
        # brand_id,brand_name
        with open(
            os.path.join(
                self.project_root, "bikeshop_project/data/brands.csv"
            ),
            newline="",
            encoding="utf-8",
        ) as file:
            reader = csv.DictReader(file)
            for row in reader:
                Brand.objects.update_or_create(
                    id=row["brand_id"], defaults={"name": row["brand_name"]}
                )

        self.stdout.write("Brands loaded")

    def load_customers(self):
        # customer_id,first_name,last_name,phone,email,street,city,state,zip_code
        with open(
            os.path.join(
                self.project_root, "bikeshop_project/data/customers.csv"
            ),
            newline="",
            encoding="utf-8",
        ) as file:
            reader = csv.DictReader(file)
            for row in reader:
                Customer.objects.update_or_create(
                    id=row["customer_id"],
                    defaults={
                        "first_name": row["first_name"],
                        "last_name": row["last_name"],
                        "email": row["email"],
                        "phone": row["phone"],
                        "street": row["street"],
                        "city": row["city"],
                        "state": row["state"],
                        "zip_code": row["zip_code"],
                    },
                )

        self.stdout.write("Customers loaded.")

    def load_categories(self):
        # category_id,category_name
        with open(
            os.path.join(
                self.project_root, "bikeshop_project/data/categories.csv"
            ),
            newline="",
            encoding="utf-8",
        ) as file:
            reader = csv.DictReader(file)
            for row in reader:
                Category.objects.update_or_create(
                    id=row["category_id"],
                    defaults={
                        "name": row["category_name"],
                    },
                )

        self.stdout.write("Categories loaded.")

    def load_products(self):
        # product_id,product_name,brand_id,category_id,model_year,list_price
        with open(
            os.path.join(
                self.project_root, "bikeshop_project/data/products.csv"
            ),
            newline="",
            encoding="utf-8",
        ) as file:
            reader = csv.DictReader(file)
            for row in reader:
                brand = Brand.objects.get(id=row["brand_id"])
                category = Category.objects.get(id=row["category_id"])
                Product.objects.update_or_create(
                    id=row["product_id"],
                    defaults={
                        "name": row["product_name"],
                        "model_year": row["model_year"],
                        "price": row["list_price"],
                        "brand": brand,
                        "category": category,
                    },
                )

        self.stdout.write("Products loaded.")

    def load_stores(self):
        # store_id,store_name,phone,email,street,city,state,zip_code
        with open(
            os.path.join(
                self.project_root, "bikeshop_project/data/stores.csv"
            ),
            newline="",
            encoding="utf-8",
        ) as file:
            reader = csv.DictReader(file)
            for row in reader:
                Store.objects.update_or_create(
                    id=row["store_id"],
                    defaults={
                        "name": row["store_name"],
                        "phone": row["phone"],
                        "email": row["email"],
                        "street": row["street"],
                        "city": row["city"],
                        "state": row["state"],
                        "zip_code": row["zip_code"],
                    },
                )

        self.stdout.write("Stores loaded.")

    def load_stocks(self):
        # store_id,product_id,quantity
        with open(
            os.path.join(
                self.project_root, "bikeshop_project/data/stocks.csv"
            ),
            newline="",
            encoding="utf-8",
        ) as file:
            reader = csv.DictReader(file)
            for row in reader:
                store = Store.objects.get(id=row["store_id"])
                product = Product.objects.get(id=row["product_id"])

                Stock.objects.update_or_create(
                    store=store,
                    product=product,
                    defaults={
                        "store": store,
                        "product": product,
                        "quantity": int(row["quantity"].strip() or 0),
                    },
                )

        self.stdout.write("Stocks loaded.")

    def load_staffs(self):
        # staff_id,first_name,last_name,email,phone,active,store_id,manager_id
        with open(
            os.path.join(
                self.project_root, "bikeshop_project/data/staffs.csv"
            ),
            newline="",
            encoding="utf-8",
        ) as file:
            reader = csv.DictReader(file)
            for row in reader:
                store = Store.objects.get(id=row["store_id"])
                Staff.objects.update_or_create(
                    id=row["staff_id"],
                    defaults={
                        "first_name": row["first_name"],
                        "last_name": row["last_name"],
                        "email": row["email"],
                        "phone": row["phone"],
                        "active": row["active"],
                        "store": store,
                        # 'manager' is skipped in first pass
                    },
                )

            for row in reader:
                if row["manager_id"]:  # Only if manager_id is present
                    staff = Staff.objects.get(id=row["staff_id"])
                    manager = Staff.objects.get(id=row["manager_id"])
                    staff.manager = manager
                    staff.save()

        self.stdout.write("Staffs loaded.")

    def load_orders(self):
        # order_id,customer_id,order_status,order_date,required_date,shipped_date,store_id,staff_id
        with open(
            os.path.join(
                self.project_root, "bikeshop_project/data/orders.csv"
            ),
            newline="",
            encoding="utf-8",
        ) as file:
            reader = csv.DictReader(file)
            for row in reader:
                customer = Customer.objects.get(id=row["customer_id"])
                store = Store.objects.get(id=row["store_id"])
                staff = Staff.objects.get(id=row["staff_id"])

                Order.objects.update_or_create(
                    id=row["order_id"],
                    defaults={
                        "order_status": row["order_status"],
                        "order_date": Command.parse_date(
                            value=row["order_date"]
                        ),
                        "expected_delivery_date": Command.parse_date(
                            value=row["required_date"]
                        ),
                        "shipped_date": Command.parse_date(
                            value=row["shipped_date"]
                        ),
                        "customer": customer,
                        "store": store,
                        "staff": staff,
                    },
                )

        self.stdout.write("Orders loaded.")

    def load_order_items(self):
        # order_id,item_id,product_id,quantity,list_price,discount
        with open(
            os.path.join(
                self.project_root, "bikeshop_project/data/order_items.csv"
            ),
            newline="",
            encoding="utf-8",
        ) as file:
            reader = csv.DictReader(file)
            for row in reader:
                order = Order.objects.get(id=row["order_id"])
                product = Product.objects.get(id=row["product_id"])

                OrderItem.objects.update_or_create(
                    order=order,
                    product=product,
                    defaults={
                        "quantity": int(row["quantity"].strip() or 0),
                        "price": row["list_price"],
                        "discount": Decimal(row["discount"].strip() or 0),
                        "order": order,
                        "product": product,
                    },
                )

        self.stdout.write("OrderItems loaded.")

    @staticmethod
    def parse_date(value):
        if value in ("", "NULL", None):
            return None
        return value
