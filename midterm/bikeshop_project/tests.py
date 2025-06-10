from rest_framework.test import APITestCase
from django.urls import reverse
from .models import (
    Order,
    Customer,
    Store,
    Staff,
    Brand,
    Product,
    Category,
    Stock,
    OrderItem,
)
from datetime import date
from model_bakery import baker


class OrderApiListTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.customer_a = Customer.objects.create(
            first_name="Test", last_name="Customer", email="1@outlook.com"
        )
        cls.customer_b = Customer.objects.create(
            first_name="B", last_name="Customer", email="2@outlook.com"
        )

        cls.store = Store.objects.create(name="Test store")
        cls.staff = Staff.objects.create(
            first_name="Test", last_name="Staff", store=cls.store
        )

        # Create default order for customer_a
        cls.order = cls.create_order(
            customer=cls.customer_a,
            order_date=date(2023, 6, 1),
            order_status=1,
        )

        cls.create_order(
            customer=cls.customer_b,
            order_date=date(2023, 7, 1),
            order_status=2,
        )

    @classmethod
    def create_order(cls, customer, order_date, order_status):
        return Order.objects.create(
            customer=customer,
            store=cls.store,
            staff=cls.staff,
            order_status=order_status,
            order_date=order_date,
            expected_delivery_date=order_date.replace(day=order_date.day + 2),
        )

    def test_get_order_list(self):
        url = reverse("order-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(
            response.data[0]["order_status_display"], "processing"
        )

    def test_filter_by_customer_id(self):
        url = reverse("order-list")
        response = self.client.get(url, {"customer_id": self.customer_a.id})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["customer"]["first_name"], "Test")

    def test_filter_by_start_date(self):
        url = reverse("order-list")

        response = self.client.get(url, {"start_date": "2023-06-01"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

        response = self.client.get(url, {"start_date": "2023-07-02"})
        self.assertEqual(len(response.data), 0)

    def test_filter_by_date_range(self):
        url = reverse("order-list")

        response = self.client.get(
            url, {"start_date": "2023-05-01", "end_date": "2023-06-30"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

        response = self.client.get(
            url, {"start_date": "2023-07-01", "end_date": "2023-07-31"}
        )
        self.assertEqual(len(response.data), 1)

    def test_filter_by_store_id(self):
        url = reverse("order-list")
        response = self.client.get(url, {"store_id": self.store.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    def test_filter_by_staff_id(self):
        url = reverse("order-list")
        response = self.client.get(url, {"staff_id": self.staff.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)


class OrdersByWeekdayAPIView(APITestCase):
    @classmethod
    def setUpTestData(cls):
        baker.make(Order, order_date=date(2025, 6, 9), _quantity=2)
        baker.make(Order, order_date=date(2025, 6, 8), _quantity=4)
        baker.make(Order, order_date=date(2025, 6, 6), _quantity=1)

    def test_orders_by_weekday(self):
        url = reverse("order-list-by-weekday")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 3)

        monday_data = next(
            (item for item in response.data if item["weekday"] == "Monday"),
            None,
        )
        self.assertIsNotNone(monday_data)
        self.assertEqual(monday_data["total"], 2)


class TopContributingStaff(APITestCase):
    @classmethod
    def setUpTestData(cls):
        staff1 = baker.make(Staff, first_name="staff1", last_name="Staff")
        staff2 = baker.make(Staff, first_name="staff2", last_name="Staff")
        staff3 = baker.make(Staff, first_name="staff3", last_name="Staff")

        baker.make(Order, staff=staff1, _quantity=5)
        baker.make(Order, staff=staff2, _quantity=3)
        baker.make(Order, staff=staff3, _quantity=6)

    def test_orders_by_weekday(self):
        url = reverse("top-contributing-staff")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 3)

        staff = next(
            (
                staff
                for staff in response.data
                if staff["first_name"] == "staff3"
            ),
            None,
        )
        self.assertIsNotNone(staff)
        self.assertEqual(staff["order_count"], 6)


class BikesByBrandAPITestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # Create 2 brands
        cls.brand1 = baker.make(Brand, name="BrandOne")
        cls.brand2 = baker.make(Brand, name="BrandTwo")

        # Create 3 products for brand1 and 2 for brand2
        cls.products_brand1 = baker.make(
            Product, brand=cls.brand1, _quantity=3
        )
        cls.products_brand2 = baker.make(
            Product, brand=cls.brand2, _quantity=2
        )

    def test_bikes_by_brand(self):
        # Use reverse with brand_id as a URL argument
        url = reverse("bikes-by-brand", kwargs={"brand_id": self.brand1.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 3)

        # Confirm all returned products belong to brand1
        for product in response.data:
            self.assertEqual(product["brand"]["id"], self.brand1.id)


class CreateOrder(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # Create objects and store references to use their actual IDs
        cls.customer = baker.make(Customer)
        cls.product = baker.make(Product, price=150.0)  # Set a known price
        cls.staff = baker.make(Staff)
        cls.store = baker.make(Store)

        # Create stock linking the specific product and store
        cls.stock = baker.make(
            Stock,
            product=cls.product,
            store=cls.store,
            quantity=10,  # Ensure enough stock for the test
        )

    def test_order_create(self):
        url = reverse(
            "create-order",
        )
        payload = {
            "customer": self.customer.id,
            "store": self.store.id,
            "staff": self.staff.id,
            "order_status": 1,
            "order_date": "2025-03-31",
            "expected_delivery_date": "2025-04-02",
            "items": [
                {
                    "product": self.product.id,
                    "quantity": 2,
                },
            ],
        }
        response = self.client.post(url, payload, format="json")

        self.assertEqual(response.status_code, 201)

        # Check response structure based on your updated view
        self.assertIn("order", response.data)
        self.assertEqual(
            response.data["order"]["customer"]["id"], self.customer.id
        )

        # Verify stock was decremented
        self.stock.refresh_from_db()
        self.assertEqual(self.stock.quantity, 8)


class UpdateOrder(APITestCase):
    @classmethod
    def setUpTestData(cls):
        brand = Brand.objects.create(name="test brand")
        category = Category.objects.create(name="test category")
        cls.p1 = Product.objects.create(
            name="test product",
            model_year="1",
            price=15,
            brand=brand,
            category=category,
        )
        store = baker.make(Store)
        Stock.objects.create(store=store, quantity=20, product=cls.p1)
        cls.order = baker.make(Order, store=store)

    def test_order_update(self):
        url = reverse("update-order", kwargs={"pk": self.order.id})
        response = self.client.patch(
            url,
            {
                "order_status": 1,
                "order_date": "2025-06-12",
                "order_items": [
                    {"product": self.p1.id, "quantity": 2},
                ],
            },
            content_type="application/json",
        )

        stock = Stock.objects.get(store=self.order.store, product=self.p1.id)
        order_items = OrderItem.objects.filter(order=self.order.id)

        self.assertEqual(len(order_items), 1)
        self.assertEqual(order_items[0].quantity, 2)
        self.assertEqual(stock.quantity, 18)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], 1)
        self.assertEqual(response.data["order_status"], 1)
        self.assertEqual(response.data["order_date"], "2025-06-12")
