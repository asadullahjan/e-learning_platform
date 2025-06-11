from decimal import Decimal
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
from datetime import date, timedelta
from django.db.models import F, Sum
from model_bakery import baker
from rest_framework import status
from django.utils import timezone
from freezegun import freeze_time


class OrderApiListTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # Create test data with more descriptive names
        cls.customer_a = Customer.objects.create(
            first_name="Alice", last_name="Johnson", email="alice@example.com"
        )
        cls.customer_b = Customer.objects.create(
            first_name="Bob", last_name="Smith", email="bob@example.com"
        )

        cls.store = Store.objects.create(name="Downtown Store")
        cls.staff = Staff.objects.create(
            first_name="Staff", last_name="Member", store=cls.store
        )

        # Use constants for order statuses for better readability
        cls.STATUS_PROCESSING = 1
        cls.STATUS_SHIPPED = 4
        cls.STATUS_REJECTED = 3

        # Create base test data
        cls.order_a = cls._create_order(
            customer=cls.customer_a,
            order_date=date(2023, 6, 1),
            order_status=cls.STATUS_PROCESSING,
        )

        cls.order_b = cls._create_order(
            customer=cls.customer_b,
            order_date=date(2023, 7, 1),
            shipped_date=date(2023, 7, 1),
            order_status=cls.STATUS_SHIPPED,
        )

        # Store the URL to avoid repetition
        cls.url = reverse("order-list")

    @classmethod
    def _create_order(cls, customer, order_date, order_status, **kwargs):
        """Helper method to create orders with consistent defaults."""
        defaults = {
            "customer": customer,
            "store": cls.store,
            "staff": cls.staff,
            "order_status": order_status,
            "order_date": order_date,
            "expected_delivery_date": order_date + timedelta(days=2),
        }
        defaults.update(kwargs)
        return Order.objects.create(**defaults)

    def _get_orders(self, params=None):
        """Helper method to make GET requests to the order list endpoint."""
        response = self.client.get(self.url, params or {})
        self.assertEqual(response.status_code, 200)
        return response.data

    def test_get_order_list_returns_all_orders(self):
        """Test that GET /orders returns all orders."""
        orders = self._get_orders()

        self.assertEqual(len(orders), 2)
        self.assertEqual(orders[0]["order_status_display"], "completed")

    def test_filter_by_customer_id_returns_customer_orders_only(self):
        """Test filtering orders by customer ID."""
        orders = self._get_orders({"customer_id": self.customer_a.id})

        self.assertEqual(len(orders), 1)
        self.assertEqual(orders[0]["customer"]["first_name"], "Alice")

    def test_filter_by_customer_id_with_invalid_id_returns_empty(self):
        """Test filtering with non-existent customer ID returns empty result."""
        orders = self._get_orders({"customer_id": 99999})

        self.assertEqual(len(orders), 0)

    def test_filter_by_start_date_includes_orders_from_date(self):
        """Test filtering orders by start date."""
        # Should include both orders (June 1st and July 1st)
        orders = self._get_orders({"start_date": "2023-06-01"})
        self.assertEqual(len(orders), 2)

        # Should include no orders (after July 1st)
        orders = self._get_orders({"start_date": "2023-07-02"})
        self.assertEqual(len(orders), 0)

    def test_filter_by_date_range_includes_orders_in_range(self):
        """Test filtering orders by date range."""
        # Should include only June order
        orders = self._get_orders(
            {"start_date": "2023-05-01", "end_date": "2023-06-30"}
        )
        self.assertEqual(len(orders), 1)

        # Should include only July order
        orders = self._get_orders(
            {"start_date": "2023-07-01", "end_date": "2023-07-31"}
        )
        self.assertEqual(len(orders), 1)

    def test_filter_by_store_id_returns_store_orders(self):
        """Test filtering orders by store ID."""
        orders = self._get_orders({"store_id": self.store.id})

        self.assertEqual(len(orders), 2)

    def test_filter_by_staff_id_returns_staff_orders(self):
        """Test filtering orders by staff ID."""
        orders = self._get_orders({"staff_id": self.staff.id})

        self.assertEqual(len(orders), 2)

    @freeze_time("2023-06-15")  # Mock current date for consistent testing
    def test_filter_delayed_orders_returns_only_delayed_orders(self):
        """Test filtering for delayed orders excludes rejected orders."""
        # Create delayed shipped order (shipped after expected delivery)
        late_shipped_order = self._create_order(
            customer=self.customer_a,
            order_date=date(2023, 6, 1),
            order_status=self.STATUS_SHIPPED,
            expected_delivery_date=date(2023, 6, 5),
            shipped_date=date(2023, 6, 10),
        )

        # Create delayed unshipped order (not shipped by expected delivery date)
        unshipped_delayed_order = self.order_a

        # Create rejected delayed order (should be excluded)
        rejected_order = self._create_order(
            customer=self.customer_a,
            order_date=date(2023, 5, 1),
            order_status=self.STATUS_REJECTED,
            expected_delivery_date=date(2023, 5, 3),
            shipped_date=None,
        )

        orders = self._get_orders({"delayed_orders": True})
        print(orders)
        # Should only return the 2 delayed orders, not the rejected one
        self.assertEqual(len(orders), 2)

        order_ids = {order["id"] for order in orders}
        self.assertEqual(
            order_ids, {late_shipped_order.id, unshipped_delayed_order.id}
        )
        self.assertNotIn(rejected_order.id, order_ids)

    def test_filter_delayed_orders_with_no_delayed_orders_returns_empty(self):
        """Test delayed orders filter returns empty when no delayed orders exist."""
        with freeze_time("2023-05-01"):  # Before any orders are delayed
            orders = self._get_orders({"delayed_orders": True})
            self.assertEqual(len(orders), 0)

    def test_multiple_filters_work_together(self):
        """Test that multiple filters can be applied simultaneously."""
        orders = self._get_orders(
            {"customer_id": self.customer_a.id, "start_date": "2023-06-01"}
        )

        self.assertEqual(len(orders), 1)
        self.assertEqual(orders[0]["customer"]["first_name"], "Alice")

    def test_invalid_date_format_returns_appropriate_response(self):
        """Test handling of invalid date formats."""
        response = self.client.get(self.url, {"start_date": "invalid-date"})
        # Adjust assertion based on your API's error handling
        self.assertIn(
            response.status_code, [400, 422]
        )  # Bad Request or Unprocessable Entity


class OrdersByWeekdayAPIViewTest(APITestCase):
    """
    IMPROVED: More comprehensive test coverage, edge cases, data validation
    """

    @classmethod
    def setUpTestData(cls):
        # Create necessary related objects
        cls.brand = baker.make(Brand)
        cls.category = baker.make(Category)
        cls.product = baker.make(
            Product,
            brand=cls.brand,
            category=cls.category,
            price=Decimal("100.00"),
        )
        cls.store = baker.make(Store)
        cls.customer = baker.make(Customer)
        cls.staff = baker.make(Staff, store=cls.store)

        # Create orders on specific days with order items
        cls.monday_orders = []
        for i in range(3):
            order = baker.make(
                Order,
                order_date=date(2025, 6, 9),  # Monday
                customer=cls.customer,
                store=cls.store,
                staff=cls.staff,
            )
            baker.make(
                OrderItem,
                order=order,
                product=cls.product,
                quantity=2,
                price=100.00,
            )
            cls.monday_orders.append(order)

        # Create orders on other days
        cls.tuesday_order = baker.make(
            Order,
            order_date=date(2025, 6, 10),  # Tuesday
            customer=cls.customer,
            store=cls.store,
            staff=cls.staff,
        )
        baker.make(
            OrderItem,
            order=cls.tuesday_order,
            product=cls.product,
            quantity=1,
            price=150.00,
        )

        cls.friday_order = baker.make(
            Order,
            order_date=date(2025, 6, 13),  # Friday
            customer=cls.customer,
            store=cls.store,
            staff=cls.staff,
        )
        baker.make(
            OrderItem,
            order=cls.friday_order,
            product=cls.product,
            quantity=3,
            price=75.00,
        )

    def test_orders_by_weekday_success(self):
        """Test successful weekday analysis"""
        url = reverse("order-list-by-weekday")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("summary", response.data)
        self.assertIn("weekday_data", response.data)

        # Check summary data
        summary = response.data["summary"]
        self.assertEqual(
            summary["total_orders"], 5
        )  # 3 Monday + 1 Tuesday + 1 Friday

        # Check weekday data structure
        weekday_data = response.data["weekday_data"]
        self.assertTrue(len(weekday_data) > 0)

        # Find Monday data (should be highest)
        monday_data = next(
            (item for item in weekday_data if item["weekday"] == "Monday"),
            None,
        )
        self.assertIsNotNone(monday_data)
        self.assertEqual(monday_data["total_orders"], 3)
        self.assertEqual(
            monday_data["total_revenue"], 600.0
        )  # 3 orders * 2 items * 100.00
        self.assertGreater(monday_data["percentage_of_total"], 0)

    def test_orders_by_weekday_with_date_filter(self):
        """Test weekday analysis with date filtering"""
        url = reverse("order-list-by-weekday")
        response = self.client.get(
            url, {"start_date": "2025-06-09", "end_date": "2025-06-10"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        summary = response.data["summary"]
        self.assertEqual(
            summary["total_orders"], 4
        )  # Monday + Tuesday orders only

    def test_orders_by_weekday_invalid_date(self):
        """Test error handling for invalid date format"""
        url = reverse("order-list-by-weekday")
        response = self.client.get(url, {"start_date": "invalid-date"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_orders_by_weekday_no_data(self):
        """Test response when no orders exist in date range"""
        url = reverse("order-list-by-weekday")
        response = self.client.get(
            url, {"start_date": "2020-01-01", "end_date": "2020-01-31"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["summary"]["total_orders"], 0)


class TopContributingStaffAPIViewTest(APITestCase):
    """
    IMPROVED: More comprehensive staff performance testing
    """

    @classmethod
    def setUpTestData(cls):
        # Create test data
        cls.store = baker.make(Store, name="Test Store")
        cls.brand = baker.make(Brand)
        cls.category = baker.make(Category)
        cls.product = baker.make(
            Product,
            brand=cls.brand,
            category=cls.category,
            price=Decimal("200.00"),
        )
        cls.customer = baker.make(Customer)

        # Create staff with different performance levels
        cls.high_performer = baker.make(
            Staff,
            first_name="High",
            last_name="Performer",
            store=cls.store,
            active=True,
        )
        cls.medium_performer = baker.make(
            Staff,
            first_name="Medium",
            last_name="Performer",
            store=cls.store,
            active=True,
        )
        cls.low_performer = baker.make(
            Staff,
            first_name="Low",
            last_name="Performer",
            store=cls.store,
            active=True,
        )
        cls.inactive_staff = baker.make(
            Staff,
            first_name="Inactive",
            last_name="Staff",
            store=cls.store,
            active=False,
        )

        # Create orders for high performer (10 orders)
        for i in range(10):
            order = baker.make(
                Order,
                staff=cls.high_performer,
                customer=cls.customer,
                store=cls.store,
                order_date=date.today() - timedelta(days=i),
            )
            baker.make(
                OrderItem,
                order=order,
                product=cls.product,
                quantity=2,
                price=200.00,
            )

        # Create orders for medium performer (5 orders)
        for i in range(5):
            order = baker.make(
                Order,
                staff=cls.medium_performer,
                customer=cls.customer,
                store=cls.store,
                order_date=date.today() - timedelta(days=i),
            )
            baker.make(
                OrderItem,
                order=order,
                product=cls.product,
                quantity=1,
                price=200.00,
            )

        # Create orders for low performer (2 orders)
        for i in range(2):
            order = baker.make(
                Order,
                staff=cls.low_performer,
                customer=cls.customer,
                store=cls.store,
                order_date=date.today() - timedelta(days=i),
            )
            baker.make(
                OrderItem,
                order=order,
                product=cls.product,
                quantity=1,
                price=100.00,
            )

    def test_top_contributing_staff_success(self):
        """Test successful staff ranking"""
        url = reverse("top-contributing-staff")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("period_info", response.data)
        self.assertIn("staff_data", response.data)

        staff_data = response.data["staff_data"]
        self.assertEqual(len(staff_data), 3)  # Only active staff

        # Check ranking (high performer should be first)
        self.assertEqual(staff_data[0]["name"], "High Performer")
        self.assertEqual(staff_data[0]["rank"], 1)
        self.assertEqual(staff_data[0]["order_count"], 10)

    def test_top_contributing_staff_with_limit(self):
        """Test staff ranking with custom limit"""
        url = reverse("top-contributing-staff")
        response = self.client.get(url, {"limit": 2})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        staff_data = response.data["staff_data"]
        self.assertEqual(len(staff_data), 2)

    def test_top_contributing_staff_with_min_orders(self):
        """Test filtering by minimum orders"""
        url = reverse("top-contributing-staff")
        response = self.client.get(url, {"min_orders": 5})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        staff_data = response.data["staff_data"]
        # Should only include high and medium performers
        self.assertEqual(len(staff_data), 2)

    def test_top_contributing_staff_invalid_parameters(self):
        """Test error handling for invalid parameters"""
        url = reverse("top-contributing-staff")

        # Test invalid limit
        response = self.client.get(url, {"limit": 0})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Test invalid period
        response = self.client.get(url, {"period": "invalid"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_top_contributing_staff_different_periods(self):
        """Test different time periods"""
        url = reverse("top-contributing-staff")

        periods = ["week", "month", "quarter", "year"]
        for period in periods:
            response = self.client.get(url, {"period": period})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["period_info"]["period"], period)


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
