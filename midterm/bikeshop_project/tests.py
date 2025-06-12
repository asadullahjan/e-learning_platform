from decimal import Decimal
from datetime import date, timedelta

from django.urls import reverse

from freezegun import freeze_time
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APITestCase

from .models import (
    Brand,
    Category,
    Customer,
    Order,
    OrderItem,
    Product,
    Staff,
    Stock,
    Store,
)


class OrderApiListTest(APITestCase):
    """Tests for the OrderListAPIView endpoint."""

    @classmethod
    def setUpTestData(cls):
        """Set up test data for order list tests."""
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
        cls.STATUS_PENDING = 1
        cls.STATUS_PROCESSING = 2
        cls.STATUS_REJECTED = 3
        cls.STATUS_COMPLETED = 4
        cls.url = reverse("order-list")

    def _create_order(cls, customer, order_date, order_status):
        """Create an order with default values."""
        return Order.objects.create(
            customer=customer,
            store=cls.store,
            staff=cls.staff,
            order_status=order_status,
            order_date=order_date,
            expected_delivery_date=order_date + timedelta(days=2),
        )

    def _get_orders(self, params=None):
        """Make GET request to order list endpoint and verify response."""
        resp = self.client.get(self.url, params or {})
        self.assertEqual(
            resp.status_code,
            status.HTTP_200_OK,
            f"Expected 200, got {resp.status_code}: {resp.data}",
        )
        return resp.data

    def test_get_order_list_returns_all_orders(self):
        """Test retrieving all orders."""
        self._create_order(
            customer=self.customer_a,
            order_date=date(2023, 6, 1),
            order_status=self.STATUS_PENDING,
        )
        self._create_order(
            customer=self.customer_b,
            order_date=date(2023, 7, 1),
            order_status=self.STATUS_COMPLETED,
        )
        orders = self._get_orders()
        self.assertEqual(
            len(orders), 2, f"Expected 2 orders, got {len(orders)}"
        )
        self.assertEqual(orders[0]["order_status_display"], "completed")

    def test_filter_by_customer_id_returns_customer_orders(self):
        """Test filtering orders by customer ID."""
        self._create_order(
            customer=self.customer_a,
            order_date=date(2023, 6, 1),
            order_status=self.STATUS_PENDING,
        )
        self._create_order(
            customer=self.customer_b,
            order_date=date(2023, 7, 1),
            order_status=self.STATUS_COMPLETED,
        )
        orders = self._get_orders({"customer_id": self.customer_a.id})
        self.assertEqual(
            len(orders), 1, f"Expected 1 order, got {len(orders)}"
        )
        self.assertEqual(orders[0]["customer"]["first_name"], "Alice")

    def test_filter_by_customer_id_invalid_id_returns_empty(self):
        """Test filtering with non-existent customer ID."""
        self._create_order(
            customer=self.customer_a,
            order_date=date(2023, 6, 1),
            order_status=self.STATUS_PENDING,
        )
        orders = self._get_orders({"customer_id": 99999})
        self.assertEqual(
            len(orders), 0, f"Expected 0 orders, got {len(orders)}"
        )

    def test_filter_by_start_date_includes_orders_from_date(self):
        """Test filtering orders by start date."""
        self._create_order(
            customer=self.customer_a,
            order_date=date(2023, 6, 1),
            order_status=self.STATUS_PENDING,
        )
        self._create_order(
            customer=self.customer_b,
            order_date=date(2023, 7, 1),
            order_status=self.STATUS_COMPLETED,
        )
        orders = self._get_orders({"start_date": "2023-06-01"})
        self.assertEqual(
            len(orders), 2, f"Expected 2 orders, got {len(orders)}"
        )
        orders = self._get_orders({"start_date": "2023-07-02"})
        self.assertEqual(
            len(orders), 0, f"Expected 0 orders, got {len(orders)}"
        )

    def test_filter_by_date_range_includes_orders_in_range(self):
        """Test filtering orders by date range."""
        self._create_order(
            customer=self.customer_a,
            order_date=date(2023, 6, 1),
            order_status=self.STATUS_PENDING,
        )
        self._create_order(
            customer=self.customer_b,
            order_date=date(2023, 7, 1),
            order_status=self.STATUS_COMPLETED,
        )
        orders = self._get_orders(
            {
                "start_date": "2023-05-01",
                "end_date": "2023-06-30",
            }
        )
        self.assertEqual(
            len(orders), 1, f"Expected 1 order, got {len(orders)}"
        )
        orders = self._get_orders(
            {
                "start_date": "2023-07-01",
                "end_date": "2023-07-31",
            }
        )
        self.assertEqual(
            len(orders), 1, f"Expected 1 order, got {len(orders)}"
        )

    def test_filter_by_store_id_returns_store_orders(self):
        """Test filtering orders by store ID."""
        self._create_order(
            customer=self.customer_a,
            order_date=date(2023, 6, 1),
            order_status=self.STATUS_PENDING,
        )
        self._create_order(
            customer=self.customer_b,
            order_date=date(2023, 7, 1),
            order_status=self.STATUS_COMPLETED,
        )
        orders = self._get_orders({"store_id": self.store.id})
        self.assertEqual(
            len(orders), 2, f"Expected 2 orders, got {len(orders)}"
        )

    def test_filter_by_staff_id_returns_staff_orders(self):
        """Test filtering orders by staff ID."""
        self._create_order(
            customer=self.customer_a,
            order_date=date(2023, 6, 1),
            order_status=self.STATUS_PENDING,
        )
        self._create_order(
            customer=self.customer_b,
            order_date=date(2023, 7, 1),
            order_status=self.STATUS_COMPLETED,
        )
        orders = self._get_orders({"staff_id": self.staff.id})
        self.assertEqual(
            len(orders), 2, f"Expected 2 orders, got {len(orders)}"
        )

    @freeze_time("2023-06-15")
    def test_filter_delayed_orders_returns_only_delayed(self):
        """Test filtering for delayed orders, excluding rejected orders."""
        late_completed = self._create_order(
            customer=self.customer_a,
            order_date=date(2023, 6, 1),
            order_status=self.STATUS_COMPLETED,
        )
        late_completed.expected_delivery_date = date(2023, 6, 5)
        late_completed.shipped_date = date(2023, 6, 10)
        late_completed.save()

        unshipped_delayed = self._create_order(
            customer=self.customer_a,
            order_date=date(2023, 5, 1),
            order_status=self.STATUS_PROCESSING,
        )
        unshipped_delayed.expected_delivery_date = date(2023, 5, 5)
        unshipped_delayed.shipped_date = None
        unshipped_delayed.save()

        rejected = self._create_order(
            customer=self.customer_a,
            order_date=date(2023, 5, 1),
            order_status=self.STATUS_REJECTED,
        )
        rejected.expected_delivery_date = date(2023, 5, 3)
        rejected.shipped_date = None
        rejected.save()

        orders = self._get_orders({"delayed_orders": True})
        self.assertEqual(
            len(orders), 2, f"Expected 2 orders, got {len(orders)}"
        )
        order_ids = {order["id"] for order in orders}
        self.assertEqual(order_ids, {late_completed.id, unshipped_delayed.id})
        self.assertNotIn(rejected.id, order_ids)

    @freeze_time("2023-05-01")
    def test_filter_delayed_orders_no_delayed_returns_empty(self):
        """Test delayed orders filter with no delayed orders."""
        self._create_order(
            customer=self.customer_a,
            order_date=date(2023, 6, 1),
            order_status=self.STATUS_PENDING,
        )
        orders = self._get_orders({"delayed_orders": True})
        self.assertEqual(
            len(orders), 0, f"Expected 0 orders, got {len(orders)}"
        )

    def test_multiple_filters_work_together(self):
        """Test combining multiple filters."""
        self._create_order(
            customer=self.customer_a,
            order_date=date(2023, 6, 1),
            order_status=self.STATUS_PENDING,
        )
        self._create_order(
            customer=self.customer_b,
            order_date=date(2023, 7, 1),
            order_status=self.STATUS_COMPLETED,
        )
        orders = self._get_orders(
            {
                "customer_id": self.customer_a.id,
                "start_date": "2023-06-01",
            }
        )
        self.assertEqual(
            len(orders), 1, f"Expected 1 order, got {len(orders)}"
        )
        self.assertEqual(orders[0]["customer"]["first_name"], "Alice")

    def test_invalid_date_format_returns_error(self):
        """Test handling invalid date formats."""
        resp = self.client.get(self.url, {"start_date": "invalid-date"})
        self.assertEqual(
            resp.status_code,
            status.HTTP_400_BAD_REQUEST,
            f"Expected 400, got {resp.status_code}: {resp.data}",
        )


class OrdersByWeekdayAPIViewTest(APITestCase):
    """Tests for the OrdersByWeekdayAPIView endpoint."""

    @classmethod
    def setUpTestData(cls):
        """Set up test data for weekday analysis tests."""
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
        cls.monday_orders = []
        for _ in range(3):
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
                price=Decimal("100.00"),
            )
            cls.monday_orders.append(order)
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
            price=Decimal("150.00"),
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
            price=Decimal("75.00"),
        )

    def test_orders_by_weekday_success(self):
        """Test retrieving weekday order statistics."""
        url = reverse("order-list-by-weekday")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("summary", resp.data)
        self.assertIn("weekday_data", resp.data)
        summary = resp.data["summary"]
        self.assertEqual(summary["total_orders"], 5)
        self.assertEqual(summary["total_revenue"], 975.0)  # 3*200 + 150 + 225
        weekday_data = resp.data["weekday_data"]
        monday_data = next(
            item for item in weekday_data if item["weekday"] == "Monday"
        )
        self.assertEqual(monday_data["total_orders"], 3)
        self.assertEqual(monday_data["total_revenue"], 600.0)
        self.assertEqual(monday_data["avg_order_value"], 200.0)
        self.assertAlmostEqual(monday_data["percentage_of_total"], 60.0)

    def test_orders_by_weekday_with_date_filter(self):
        """Test weekday analysis with date range filter."""
        url = reverse("order-list-by-weekday")
        resp = self.client.get(
            url,
            {
                "start_date": "2025-06-09",
                "end_date": "2025-06-10",
            },
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        summary = resp.data["summary"]
        self.assertEqual(summary["total_orders"], 4)  # Monday + Tuesday
        self.assertEqual(summary["total_revenue"], 750.0)  # 600 + 150

    def test_invalid_date_filter_returns_error(self):
        """Test handling invalid date format in filter."""
        url = reverse("order-list-by-weekday")
        resp = self.client.get(url, {"start_date": "invalid-date"})
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_orders_in_date_range_returns_empty(self):
        """Test response when no orders exist in date range."""
        url = reverse("order-list-by-weekday")
        resp = self.client.get(
            url,
            {
                "start_date": "2020-01-01",
                "end_date": "2020-01-31",
            },
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["summary"]["total_orders"], 0)
        self.assertEqual(len(resp.data["weekday_data"]), 0)


class TopContributingStaffAPIViewTest(APITestCase):
    """Tests for the TopContributingStaffAPIView endpoint."""

    @classmethod
    def setUpTestData(cls):
        """Set up test data for staff performance tests."""
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
        cls.high_performer = baker.make(
            Staff,
            first_name="John",
            last_name="High",
            store=cls.store,
            active=True,
        )
        cls.medium_performer = baker.make(
            Staff,
            first_name="Jane",
            last_name="Medium",
            store=cls.store,
            active=True,
        )
        cls.low_performer = baker.make(
            Staff,
            first_name="Joe",
            last_name="Low",
            store=cls.store,
            active=True,
        )
        cls.inactive = baker.make(
            Staff,
            first_name="Inactive",
            last_name="Staff",
            store=cls.store,
            active=False,
        )
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
                price=Decimal("200.00"),
            )
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
                price=Decimal("200.00"),
            )
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
                price=Decimal("100.00"),
            )

    def test_successful_staff_ranking(self):
        """Test retrieving top staff rankings."""
        url = reverse("top-contributing-staff")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("period_info", resp.data)
        self.assertIn("staff_data", resp.data)
        staff_data = resp.data["staff_data"]
        self.assertEqual(len(staff_data), 3)  # Only active staff
        self.assertEqual(staff_data[0]["name"], "John High")
        self.assertEqual(staff_data[0]["rank"], 1)
        self.assertEqual(staff_data[0]["order_count"], 10)
        self.assertEqual(staff_data[0]["total_revenue"], 4000.0)

    def test_staff_ranking_with_limit(self):
        """Test limiting the number of staff returned."""
        url = reverse("top-contributing-staff")
        resp = self.client.get(url, {"limit": "2"})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data["staff_data"]), 2)

    def test_filter_by_minimum_orders(self):
        """Test filtering staff by minimum order count."""
        url = reverse("top-contributing-staff")
        resp = self.client.get(url, {"min_orders": 5})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        staff_data = resp.data["staff_data"]
        self.assertEqual(len(staff_data), 2)  # High and medium performers
        self.assertEqual(
            {s["name"] for s in staff_data}, {"John High", "Jane Medium"}
        )

    def test_invalid_parameters_return_error(self):
        """Test handling invalid parameters."""
        url = reverse("top-contributing-staff")
        resp = self.client.get(url, {"limit": 0})
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

        resp = self.client.get(url, {"period": "invalid"})
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_different_periods(self):
        """Test staff ranking with different time periods."""
        url = reverse("top-contributing-staff")
        for period in ["week", "month", "quarter", "year"]:
            resp = self.client.get(url, {"period": period})
            self.assertEqual(resp.status_code, status.HTTP_200_OK)
            self.assertEqual(resp.data["period_info"]["period"], period)


class BikesByBrandAPITest(APITestCase):
    """Tests for the BikesByBrandAPIView endpoint."""

    @classmethod
    def setUpTestData(cls):
        """Set up test data for bikes by brand tests."""
        cls.brand1 = baker.make(Brand, name="BrandOne")
        cls.brand2 = baker.make(Brand, name="BrandTwo")
        cls.products1 = baker.make(Product, brand=cls.brand1, _quantity=3)
        cls.products2 = baker.make(Product, brand=cls.brand2, _quantity=2)

    def test_retrieve_bikes_by_brand(self):
        """Test retrieving bikes for a specific brand."""
        url = reverse("bikes-by-brand", kwargs={"brand_id": self.brand1.id})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(resp.data), 3, f"Expected 3 products, got {len(resp.data)}"
        )
        for product in resp.data:
            self.assertEqual(product["brand"]["id"], self.brand1.id)


class CreateOrder(APITestCase):
    """Tests for the CreateNewOrderAPIView endpoint."""

    @classmethod
    def setUpTestData(cls):
        """Set up test data for order creation tests."""
        cls.customer = baker.make(Customer)
        cls.product = Product.objects.create(
            name="Test Product",
            price=Decimal("150.00"),
            brand=baker.make(Brand),
            category=baker.make(Category),
            model_year=2023,
        )
        cls.staff = baker.make(Staff)
        cls.store = baker.make(Store)
        cls.stock = Stock.objects.create(
            product=cls.product,
            store=cls.store,
            quantity=10,
        )

    def test_create_order_success(self):
        """Test successful order creation."""
        url = reverse("create-order")
        payload = {
            "customer": str(self.customer.id),
            "store": str(self.store.id),
            "staff": str(self.staff.id),
            "order_status": 1,
            "order_date": "2025-06-12",
            "expected_delivery_date": "2025-06-14",
            "order_items": [
                {"product": self.product.id, "quantity": 2},
            ],
        }
        resp = self.client.post(url, payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertIn("order", resp.data)
        self.assertEqual(
            resp.data["order"]["customer"]["id"], self.customer.id
        )
        self.stock.refresh_from_db()
        self.assertEqual(self.stock.quantity, 8)

    def test_create_order_no_items(self):
        """Test creating order with no items."""
        url = reverse("create-order")
        payload = {
            "customer": str(self.customer.id),
            "store": str(self.store.id),
            "staff": str(self.staff.id),
            "order_status": 1,
            "order_date": "2025-06-12",
            "expected_delivery_date": "2025-06-14",
            "order_items": [],
        }
        resp = self.client.post(url, payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertIn(
            "Order must have at least one item",
            str(resp.data),
        )

    def test_create_order_duplicate_items(self):
        """Test creating order with duplicate products."""
        url = reverse("create-order")
        payload = {
            "customer": str(self.customer.id),
            "store": str(self.store.id),
            "staff": str(self.staff.id),
            "order_status": 1,
            "order_date": "2025-06-12",
            "expected_delivery_date": "2025-06-14",
            "order_items": [
                {"product": self.product.id, "quantity": 2},
                {"product": self.product.id, "quantity": 3},
            ],
        }
        resp = self.client.post(url, payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertIn(
            "Duplicate products found",
            str(resp.data),
        )

    def test_create_order_insufficient_stock(self):
        """Test creating order with insufficient stock."""
        url = reverse("create-order")
        payload = {
            "customer": str(self.customer.id),
            "store": str(self.store.id),
            "staff": str(self.staff.id),
            "order_status": 1,
            "order_date": "2025-06-12",
            "expected_delivery_date": "2025-06-14",
            "order_items": [
                {"product": self.product.id, "quantity": 15},
            ],
        }
        resp = self.client.post(url, payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_409_CONFLICT)

        self.assertIn("Not enough stock", str(resp.data))
        # self.assertIn("Not enough stock", str(resp.data["non_field_errors"]))
        self.stock.refresh_from_db()
        self.assertEqual(self.stock.quantity, 10)

    def test_create_order_no_stock(self):
        """Test creating order with non-existent stock."""
        product_no_stock = Product.objects.create(
            name="No Stock Product",
            price=Decimal("100.00"),
            brand=baker.make(Brand),
            category=baker.make(Category),
            model_year=2023,
        )
        url = reverse("create-order")
        payload = {
            "customer": str(self.customer.id),
            "store": str(self.store.id),
            "staff": str(self.staff.id),
            "order_status": 1,
            "order_date": "2025-06-12",
            "expected_delivery_date": "2025-06-14",
            "order_items": [
                {"product": product_no_stock.id, "quantity": 1},
            ],
        }
        resp = self.client.post(url, payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_409_CONFLICT)

        self.assertIn(
            "is not available in this store",
            str(resp.data),
        )

    def test_create_order_invalid_dates(self):
        """Test creating order with invalid dates."""
        url = reverse("create-order")
        payload = {
            "customer": str(self.customer.id),
            "store": str(self.store.id),
            "staff": str(self.staff.id),
            "order_status": 1,
            "order_date": "2025-06-12",
            "expected_delivery_date": "2025-06-10",
            "order_items": [
                {"product": self.product.id, "quantity": 2},
            ],
        }
        resp = self.client.post(url, payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertIn(
            "Expected delivery date must be after",
            str(resp.data),
        )


class UpdateOrder(APITestCase):
    """Tests for the UpdateOrderAPIView endpoint."""

    @classmethod
    def setUpTestData(cls):
        """Set up test data for order update tests."""
        cls.brand = Brand.objects.create(name="Test Brand")
        cls.category = Category.objects.create(name="Test Category")
        cls.product = Product.objects.create(
            name="Test Product",
            model_year=2023,
            price=Decimal("15.00"),
            brand=cls.brand,
            category=cls.category,
        )
        cls.store = baker.make(Store)
        cls.stock = Stock.objects.create(
            store=cls.store,
            product=cls.product,
            quantity=20,
        )
        cls.order = baker.make(Order, store=cls.store)

    def test_order_update_success(self):
        """Test successful order update."""
        url = reverse("update-order", kwargs={"pk": self.order.id})
        payload = {
            "order_status": 1,
            "order_date": "2025-06-12",
            "order_items": [
                {"product": self.product.id, "quantity": 2},
            ],
        }
        resp = self.client.patch(url, payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["id"], self.order.id)
        self.assertEqual(resp.data["order_status"], 1)
        self.assertEqual(resp.data["order_date"], "2025-06-12")
        order_items = OrderItem.objects.filter(order=self.order.id)
        self.assertEqual(len(order_items), 1)
        self.assertEqual(order_items[0].quantity, 2)
        self.stock.refresh_from_db()
        self.assertEqual(self.stock.quantity, 18)

    def test_order_update_insufficient_stock(self):
        """Test updating order with insufficient stock."""
        url = reverse("update-order", kwargs={"pk": self.order.id})
        payload = {
            "order_status": 1,
            "order_date": "2025-06-12",
            "order_items": [
                {"product": self.product.id, "quantity": 25},
            ],
        }
        resp = self.client.patch(url, payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_409_CONFLICT)

        self.assertIn("Not enough stock", str(resp.data))
        # self.assertIn("Not enough stock", str(resp.data["non_field_errors"]))
        self.stock.refresh_from_db()
        self.assertEqual(self.stock.quantity, 20)
        self.assertEqual(
            OrderItem.objects.filter(order=self.order.id).count(), 0
        )

    def test_order_update_no_stock(self):
        """Test updating order with non-existent stock."""
        product_no_stock = baker.make(
            Product,
            name="No Stock Product",
            price=Decimal("100.00"),
            model_year=2025,
        )
        url = reverse("update-order", kwargs={"pk": self.order.id})
        payload = {
            "order_status": 1,
            "order_date": "2025-06-12",
            "order_items": [
                {"product": product_no_stock.id, "quantity": 1},
            ],
        }
        resp = self.client.patch(url, payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_409_CONFLICT)

        self.assertIn(
            "is not available in this store",
            str(resp.data),
        )
        self.stock.refresh_from_db()
        self.assertEqual(self.stock.quantity, 20)
        self.assertEqual(
            OrderItem.objects.filter(order=self.order.id).count(), 0
        )

    def test_order_update_duplicate_products(self):
        """Test updating order with duplicate products."""
        url = reverse("update-order", kwargs={"pk": self.order.id})
        payload = {
            "order_status": 1,
            "order_date": "2025-06-12",
            "order_items": [
                {"product": self.product.id, "quantity": 2},
                {"product": self.product.id, "quantity": 3},
            ],
        }
        resp = self.client.patch(url, payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertIn(
            "Duplicate products found",
            str(resp.data),
        )
        self.stock.refresh_from_db()
        self.assertEqual(self.stock.quantity, 20)
        self.assertEqual(
            OrderItem.objects.filter(order=self.order.id).count(), 0
        )

    def test_order_update_invalid_dates(self):
        """Test updating order with invalid dates."""
        url = reverse("update-order", kwargs={"pk": self.order.id})
        payload = {
            "order_status": 1,
            "order_date": "2025-06-12",
            "expected_delivery_date": "2025-06-10",
            "order_items": [
                {"product": self.product.id, "quantity": 2},
            ],
        }
        resp = self.client.patch(url, payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertIn(
            "Expected delivery date must be after",
            str(resp.data),
        )
        self.stock.refresh_from_db()
        self.assertEqual(self.stock.quantity, 20)
        self.assertEqual(
            OrderItem.objects.filter(order=self.order.id).count(), 0
        )
