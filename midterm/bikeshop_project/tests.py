from rest_framework.test import APITestCase
from django.urls import reverse
from .models import Order, Customer, Store, Staff
from datetime import date


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

        # Additional order for filter tests
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
        self.assertEqual(response.data[0]["order_status_display"], "pending")

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
