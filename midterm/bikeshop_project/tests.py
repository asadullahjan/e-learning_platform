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
    """Tests for the OrderListAPIView endpoint to verify order listing and filtering."""

    @classmethod
    def setUpTestData(cls):
        """Initialize shared test data for order list tests."""
        # Create two customers for filtering tests
        cls.customer_a = Customer.objects.create(
            first_name="Alice", last_name="Johnson", email="alice@example.com"
        )
        cls.customer_b = Customer.objects.create(
            first_name="Bob", last_name="Smith", email="bob@example.com"
        )
        # Create a store and staff member for orders
        cls.store = Store.objects.create(name="Downtown Store")
        cls.staff = Staff.objects.create(
            first_name="Staff", last_name="Member", store=cls.store
        )
        # Define order status constants for clarity
        cls.STATUS_PENDING = 1
        cls.STATUS_PROCESSING = 2
        cls.STATUS_REJECTED = 3
        cls.STATUS_COMPLETED = 4
        # Set URL for the order list endpoint
        cls.url = reverse("order-list")

    def _create_order(cls, customer, order_date, order_status):
        """Helper method to create an order with specified attributes."""
        return Order.objects.create(
            customer=customer,
            store=cls.store,
            staff=cls.staff,
            order_status=order_status,
            order_date=order_date,
            expected_delivery_date=order_date + timedelta(days=2),
        )

    def _get_orders(self, params=None):
        """Send GET request to order list endpoint and verify 200 response."""
        resp = self.client.get(self.url, params or {})
        self.assertEqual(
            resp.status_code,
            status.HTTP_200_OK,
            f"Expected 200, got {resp.status_code}: {resp.data}",
        )
        return resp.data

    def test_get_order_list_returns_all_orders(self):
        """Verify that all orders are retrieved correctly."""
        # Create two orders with different statuses
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
        # Fetch orders and check response
        orders = self._get_orders()
        self.assertEqual(
            len(orders), 2, f"Expected 2 orders, got {len(orders)}"
        )
        # Verify the first order's status display (most recent order)
        self.assertEqual(orders[0]["order_status_display"], "completed")

    def test_filter_by_customer_id_returns_customer_orders(self):
        """Test filtering orders by a specific customer ID."""
        # Create orders for two customers
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
        # Filter by customer_a's ID
        orders = self._get_orders({"customer_id": self.customer_a.id})
        self.assertEqual(
            len(orders), 1, f"Expected 1 order, got {len(orders)}"
        )
        # Verify the order belongs to customer_a
        self.assertEqual(orders[0]["customer"]["first_name"], "Alice")

    def test_filter_by_customer_id_invalid_id_returns_empty(self):
        """Test filtering with a non-existent customer ID returns no orders."""
        # Create an order for customer_a
        self._create_order(
            customer=self.customer_a,
            order_date=date(2023, 6, 1),
            order_status=self.STATUS_PENDING,
        )
        # Filter with an invalid customer ID
        orders = self._get_orders({"customer_id": 99999})
        self.assertEqual(
            len(orders), 0, f"Expected 0 orders, got {len(orders)}"
        )

    def test_filter_by_start_date_includes_orders_from_date(self):
        """Test filtering orders by start date includes correct orders."""
        # Create orders on different dates
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
        # Filter by start date including both orders
        orders = self._get_orders({"start_date": "2023-06-01"})
        self.assertEqual(
            len(orders), 2, f"Expected 2 orders, got {len(orders)}"
        )
        # Filter by start date after both orders
        orders = self._get_orders({"start_date": "2023-07-02"})
        self.assertEqual(
            len(orders), 0, f"Expected 0 orders, got {len(orders)}"
        )

    def test_filter_by_date_range_includes_orders_in_range(self):
        """Test filtering orders by a date range."""
        # Create orders on different dates
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
        # Filter by June range (should include June order)
        orders = self._get_orders(
            {
                "start_date": "2023-05-01",
                "end_date": "2023-06-30",
            }
        )
        self.assertEqual(
            len(orders), 1, f"Expected 1 order, got {len(orders)}"
        )
        # Filter by July range (should include July order)
        orders = self._get_orders(
            {
                "start_date": "2023-07-01",
                "end_date": "2023-07-31",
            }
        )
        self.assertEqual(
            len(orders), 1, f"Expected 1 order, got {len(orders)}"
        )

    def test_filter_by_store_id(self):
        """Test filtering orders by store ID."""
        # Create two orders for the same store
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
        # Filter by store ID
        orders = self._get_orders({"store_id": self.store.id})
        self.assertEqual(
            len(orders), 2, f"Expected 2 orders, got {len(orders)}"
        )

    def test_filter_by_staff_id(self):
        """Test filtering orders by staff ID."""
        # Create two orders handled by the same staff
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
        # Filter by staff ID
        orders = self._get_orders({"staff_id": self.staff.id})
        self.assertEqual(
            len(orders), 2, f"Expected 2 orders, got {len(orders)}"
        )

    @freeze_time("2023-06-15")
    def test_filter_delayed_orders_returns_only_delayed(self):
        """Test filtering for delayed orders, excluding rejected ones."""
        # Create a delayed completed order
        late_completed = self._create_order(
            customer=self.customer_a,
            order_date=date(2023, 6, 1),
            order_status=self.STATUS_COMPLETED,
        )
        late_completed.expected_delivery_date = date(2023, 6, 5)
        late_completed.shipped_date = date(2023, 6, 10)
        late_completed.save()

        # Create an unshipped delayed order
        unshipped_delayed = self._create_order(
            customer=self.customer_a,
            order_date=date(2023, 5, 1),
            order_status=self.STATUS_PROCESSING,
        )
        unshipped_delayed.expected_delivery_date = date(2023, 5, 5)
        unshipped_delayed.shipped_date = None
        unshipped_delayed.save()

        # Create a rejected order (should be excluded)
        rejected = self._create_order(
            customer=self.customer_a,
            order_date=date(2023, 5, 1),
            order_status=self.STATUS_REJECTED,
        )
        rejected.expected_delivery_date = date(2023, 5, 3)
        rejected.shipped_date = None
        rejected.save()

        # Filter delayed orders
        orders = self._get_orders({"delayed_orders": True})
        self.assertEqual(
            len(orders), 2, f"Expected 2 orders, got {len(orders)}"
        )
        # Verify only delayed orders are included
        order_ids = {order["id"] for order in orders}
        self.assertEqual(order_ids, {late_completed.id, unshipped_delayed.id})
        self.assertNotIn(rejected.id, order_ids)

    @freeze_time("2023-05-01")
    def test_filter_delayed_orders_no_delayed_returns_empty(self):
        """Test delayed orders filter when no orders are delayed."""
        # Create a non-delayed order
        self._create_order(
            customer=self.customer_a,
            order_date=date(2023, 6, 1),
            order_status=self.STATUS_PENDING,
        )
        # Filter delayed orders
        orders = self._get_orders({"delayed_orders": True})
        self.assertEqual(
            len(orders), 0, f"Expected 0 orders, got {len(orders)}"
        )

    def test_multiple_filters_work_together(self):
        """Test combining multiple filters (customer and date)."""
        # Create orders for different customers and dates
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
        # Apply customer and date filters
        orders = self._get_orders(
            {
                "customer_id": self.customer_a.id,
                "start_date": "2023-06-01",
            }
        )
        self.assertEqual(
            len(orders), 1, f"Expected 1 order, got {len(orders)}"
        )
        # Verify the filtered order
        self.assertEqual(orders[0]["customer"]["first_name"], "Alice")

    def test_invalid_date_format_returns_error(self):
        """Test handling of invalid date formats in filters."""
        # Send request with invalid date
        resp = self.client.get(self.url, {"start_date": "invalid-date"})
        self.assertEqual(
            resp.status_code,
            status.HTTP_400_BAD_REQUEST,
            f"Expected 400, got {resp.status_code}: {resp.data}",
        )


class OrdersByWeekdayAPIViewTest(APITestCase):
    """Tests for the OrdersByWeekdayAPIView endpoint to verify weekday analysis."""

    @classmethod
    def setUpTestData(cls):
        """Initialize test data for weekday order statistics."""
        # Create a product with order items
        cls.brand = baker.make(Brand)
        cls.category = baker.make(Category)
        cls.product = baker.make(
            Product,
            brand=cls.brand,
            category=cls.category,
            price=Decimal("100.00"),
        )
        # Create store, customer, and staff
        cls.store = baker.make(Store)
        cls.customer = baker.make(Customer)
        cls.staff = baker.make(Staff, store=cls.store)
        # Create three orders on Monday
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
        # Create one order on Tuesday
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
        # Create one order on Friday
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
        """Verify successful retrieval of weekday order statistics."""
        url = reverse("order-list-by-weekday")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # Check response structure
        self.assertIn("summary", resp.data)
        self.assertIn("weekday_data", resp.data)
        # Verify summary totals
        summary = resp.data["summary"]
        self.assertEqual(summary["total_orders"], 5)
        self.assertEqual(summary["total_revenue"], 975.0)  # 3*200 + 150 + 225
        # Verify Monday's data
        weekday_data = resp.data["weekday_data"]
        monday_data = next(
            item for item in weekday_data if item["weekday"] == "Monday"
        )
        self.assertEqual(monday_data["total_orders"], 3)
        self.assertEqual(monday_data["total_revenue"], 600.0)
        self.assertEqual(monday_data["avg_order_value"], 200.0)
        self.assertAlmostEqual(monday_data["percentage_of_total"], 60.0)

    def test_orders_by_weekday_with_date_filter(self):
        """Test weekday analysis with a date range filter."""
        url = reverse("order-list-by-weekday")
        # Filter for Monday and Tuesday
        resp = self.client.get(
            url,
            {
                "start_date": "2025-06-09",
                "end_date": "2025-06-10",
            },
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # Verify filtered totals
        summary = resp.data["summary"]
        self.assertEqual(summary["total_orders"], 4)  # Monday + Tuesday
        self.assertEqual(summary["total_revenue"], 750.0)  # 600 + 150

    def test_invalid_date_filter_returns_error(self):
        """Test handling of invalid date format in weekday filter."""
        url = reverse("order-list-by-weekday")
        # Send invalid date
        resp = self.client.get(url, {"start_date": "invalid-date"})
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_orders_in_date_range_returns_empty(self):
        """Test response when no orders exist in the date range."""
        url = reverse("order-list-by-weekday")
        # Filter for a date range with no orders
        resp = self.client.get(
            url,
            {
                "start_date": "2020-01-01",
                "end_date": "2020-01-31",
            },
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # Verify empty response
        self.assertEqual(resp.data["summary"]["total_orders"], 0)
        self.assertEqual(len(resp.data["weekday_data"]), 0)


class TopContributingStaffAPIViewTest(APITestCase):
    """Tests for the TopContributingStaffAPIView endpoint to verify staff rankings."""

    @classmethod
    def setUpTestData(cls):
        """Initialize test data for staff performance analysis."""
        # Create store, product, and customer
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
        # Create staff with varying performance
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
        # Create 10 orders for high performer
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
        # Create 5 orders for medium performer
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
        # Create 2 orders for low performer
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
        """Verify successful retrieval of top staff rankings."""
        url = reverse("top-contributing-staff")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # Check response structure
        self.assertIn("period_info", resp.data)
        self.assertIn("staff_data", resp.data)
        # Verify top staff data
        staff_data = resp.data["staff_data"]
        self.assertEqual(len(staff_data), 3)  # Only active staff
        self.assertEqual(staff_data[0]["name"], "John High")
        self.assertEqual(staff_data[0]["rank"], 1)
        self.assertEqual(staff_data[0]["order_count"], 10)
        self.assertEqual(staff_data[0]["total_revenue"], 4000.0)

    def test_staff_ranking_with_limit(self):
        """Test limiting the number of staff in the ranking."""
        url = reverse("top-contributing-staff")
        # Request only top 2 staff
        resp = self.client.get(url, {"limit": "2"})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data["staff_data"]), 2)

    def test_filter_by_minimum_orders(self):
        """Test filtering staff by minimum order count."""
        url = reverse("top-contributing-staff")
        # Filter staff with at least 5 orders
        resp = self.client.get(url, {"min_orders": 5})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        staff_data = resp.data["staff_data"]
        self.assertEqual(len(staff_data), 2)  # High and medium performers
        self.assertEqual(
            {s["name"] for s in staff_data}, {"John High", "Jane Medium"}
        )

    def test_invalid_parameters_return_error(self):
        """Test handling of invalid parameters for staff ranking."""
        url = reverse("top-contributing-staff")
        # Test invalid limit
        resp = self.client.get(url, {"limit": 0})
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        # Test invalid period
        resp = self.client.get(url, {"period": "invalid"})
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_different_periods(self):
        """Test staff ranking across different time periods."""
        url = reverse("top-contributing-staff")
        # Test each period
        for period in ["week", "month", "quarter", "year"]:
            resp = self.client.get(url, {"period": period})
            self.assertEqual(resp.status_code, status.HTTP_200_OK)
            self.assertEqual(resp.data["period_info"]["period"], period)


class BikesByBrandAPITest(APITestCase):
    """Tests for the BikesByBrandAPIView endpoint to verify bike filtering by brand."""

    @classmethod
    def setUpTestData(cls):
        """Initialize test data for bikes by brand tests."""
        # Create two brands with associated products
        cls.brand1 = baker.make(Brand, name="BrandOne")
        cls.brand2 = baker.make(Brand, name="BrandTwo")
        cls.products1 = baker.make(Product, brand=cls.brand1, _quantity=3)
        cls.products2 = baker.make(Product, brand=cls.brand2, _quantity=2)

    def test_retrieve_bikes_by_brand(self):
        """Verify retrieval of bikes for a specific brand."""
        url = reverse("bikes-by-brand", kwargs={"brand_id": self.brand1.id})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # Verify number of products
        self.assertEqual(
            len(resp.data), 3, f"Expected 3 products, got {len(resp.data)}"
        )
        # Verify all products belong to the brand
        for product in resp.data:
            self.assertEqual(product["brand"]["id"], self.brand1.id)


class CreateOrder(APITestCase):
    """Tests for the CreateNewOrderAPIView endpoint to verify order creation."""

    @classmethod
    def setUpTestData(cls):
        """Initialize test data for order creation tests."""
        # Create customer, product, staff, store, and stock
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
        """Verify successful creation of a new order."""
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
        # Verify response structure
        self.assertIn("order", resp.data)
        self.assertEqual(
            resp.data["order"]["customer"]["id"], self.customer.id
        )
        # Verify stock update
        self.stock.refresh_from_db()
        self.assertEqual(self.stock.quantity, 8)

    def test_create_order_no_items(self):
        """Test order creation with no items fails."""
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
        # Verify error message
        self.assertIn(
            "Order must have at least one item",
            str(resp.data),
        )

    def test_create_order_duplicate_items(self):
        """Test order creation with duplicate products fails."""
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
        # Verify error message
        self.assertIn(
            "Duplicate products found",
            str(resp.data),
        )

    def test_create_order_insufficient_stock(self):
        """Test order creation with insufficient stock fails."""
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
        # Verify error message and stock unchanged
        self.assertIn("Not enough stock", str(resp.data))
        self.stock.refresh_from_db()
        self.assertEqual(self.stock.quantity, 10)

    def test_create_order_no_stock(self):
        """Test order creation with non-existent stock fails."""
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
        # Verify error message
        self.assertIn(
            "is not available in this store",
            str(resp.data),
        )

    def test_create_order_invalid_dates(self):
        """Test order creation with invalid dates fails."""
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
        # Verify error message
        self.assertIn(
            "Expected delivery date must be after",
            str(resp.data),
        )


class UpdateOrder(APITestCase):
    """Tests for the UpdateOrderAPIView endpoint to verify order updates."""

    @classmethod
    def setUpTestData(cls):
        """Initialize test data for order update tests."""
        # Create product, store, stock, and order
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
        """Verify successful update of an existing order."""
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
        # Verify updated order details
        self.assertEqual(resp.data["id"], self.order.id)
        self.assertEqual(resp.data["order_status"], 1)
        self.assertEqual(resp.data["order_date"], "2025-06-12")
        # Verify order items
        order_items = OrderItem.objects.filter(order=self.order.id)
        self.assertEqual(len(order_items), 1)
        self.assertEqual(order_items[0].quantity, 2)
        # Verify stock update
        self.stock.refresh_from_db()
        self.assertEqual(self.stock.quantity, 18)

    def test_order_update_insufficient_stock(self):
        """Test updating order with insufficient stock fails."""
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
        # Verify error message and stock unchanged
        self.assertIn("Not enough stock", str(resp.data))
        self.stock.refresh_from_db()
        self.assertEqual(self.stock.quantity, 20)
        self.assertEqual(
            OrderItem.objects.filter(order=self.order.id).count(), 0
        )

    def test_order_update_no_stock(self):
        """Test updating order with non-existent stock fails."""
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
        # Verify error message and stock unchanged
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
        """Test updating order with duplicate products fails."""
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
        # Verify error message and stock unchanged
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
        """Test updating order with invalid dates fails."""
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
        # Verify error message and stock unchanged
        self.assertIn(
            "Expected delivery date must be after",
            str(resp.data),
        )
        self.stock.refresh_from_db()
        self.assertEqual(self.stock.quantity, 20)
        self.assertEqual(
            OrderItem.objects.filter(order=self.order.id).count(), 0
        )
