from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, timedelta, date
from decimal import Decimal
from core.models import (
    Service, ServiceType, Part, PartType,
    Order, OrderService, OrderPart,
    Employee, Client, Specialization,
    Device, DeviceType
)

class OrderBaseTestCase(TestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass',
            first_name='Test',
            last_name='User'
        )
        
        # Create client
        self.client_user = Client.objects.create(
            user=self.user,
            phone_number='+375 (29) 123-45-67',
            address='Test Address',
            birth_date=date(1990, 1, 1),
            passport_number='MP1234567'
        )
        
        # Create employee
        self.employee_user = User.objects.create_user(
            username='employee',
            password='emppass',
            first_name='Test',
            last_name='Employee'
        )
        self.specialization = Specialization.objects.create(
            name='Test Spec',
            description='Test Description'
        )
        self.employee = Employee.objects.create(
            user=self.employee_user,
            phone_number='+375 (29) 765-43-21',
            birth_date=date(1985, 1, 1),
            passport_number='MP7654321',
            hire_date=date(2020, 1, 1)
        )
        self.employee.specializations.add(self.specialization)
        
        # Create device
        self.device_type = DeviceType.objects.create(
            name='Test Device Type',
            description='Test Description'
        )
        self.device = Device.objects.create(
            device_type=self.device_type,
            brand='Test Brand',
            model='Test Model',
            serial_number='123456789',
            description='Test Description'
        )
        
        # Create service
        self.service_type = ServiceType.objects.create(
            name='Test Service Type',
            description='Test Description'
        )
        self.service = Service.objects.create(
            name='Test Service',
            service_type=self.service_type,
            description='Test Description',
            price=Decimal('100.00'),
            duration=timedelta(hours=1)
        )
        
        # Create part
        self.part_type = PartType.objects.create(
            name='Test Part Type',
            description='Test Description'
        )
        self.part = Part.objects.create(
            part_type=self.part_type,
            name='Test Part',
            description='Test Description',
            price=Decimal('50.00'),
            quantity_in_stock=10
        )

class OrderCreationTests(OrderBaseTestCase):
    def test_create_order_minimal(self):
        """Test creating order with minimal required fields"""
        order = Order.objects.create(
            client=self.client_user,
            device=self.device,
            status='pending'
        )
        self.assertEqual(order.status, 'pending')
        self.assertIsNone(order.employee)
        self.assertEqual(order.total_cost, Decimal('0'))

    def test_create_order_full(self):
        """Test creating order with all fields"""
        order = Order.objects.create(
            client=self.client_user,
            device=self.device,
            employee=self.employee,
            status='in_progress',
            description='Test order description',
            visit_date=date.today() + timedelta(days=1)
        )
        self.assertEqual(order.status, 'in_progress')
        self.assertEqual(order.employee, self.employee)
        self.assertEqual(order.description, 'Test order description')

    def test_create_order_with_services_and_parts(self):
        """Test creating order with services and parts"""
        order = Order.objects.create(
            client=self.client_user,
            device=self.device,
            employee=self.employee,
            status='pending'
        )
        
        # Add multiple services
        OrderService.objects.create(
            order=order,
            service=self.service,
            quantity=2,
            price_at_time=self.service.price
        )
        
        # Add multiple parts
        OrderPart.objects.create(
            order=order,
            part=self.part,
            quantity=3,
            price_at_time=self.part.price
        )
        
        self.assertEqual(order.services.count(), 1)
        self.assertEqual(order.parts.count(), 1)
        self.assertEqual(
            order.calculate_total_cost(),
            (Decimal('100.00') * 2) + (Decimal('50.00') * 3)
        )

class OrderStatusTests(OrderBaseTestCase):
    def setUp(self):
        super().setUp()
        self.order = Order.objects.create(
            client=self.client_user,
            device=self.device,
            employee=self.employee,
            status='pending'
        )

    def test_status_flow(self):
        """Test the normal flow of order statuses"""
        # Initial status
        self.assertEqual(self.order.status, 'pending')
        
        # Move to in_progress
        self.order.status = 'in_progress'
        self.order.save()
        self.assertEqual(self.order.status, 'in_progress')
        
        # Move to completed
        self.order.status = 'completed'
        self.order.save()
        self.assertEqual(self.order.status, 'completed')

    def test_cancel_order(self):
        """Test cancelling orders in different states"""
        # Cancel from pending
        self.order.status = 'cancelled'
        self.order.save()
        self.assertEqual(self.order.status, 'cancelled')
        
        # Create new order and cancel from in_progress
        order2 = Order.objects.create(
            client=self.client_user,
            device=self.device,
            status='in_progress'
        )
        order2.status = 'cancelled'
        order2.save()
        self.assertEqual(order2.status, 'cancelled')

    def test_invalid_status_transition(self):
        """Test that invalid status raises validation error"""
        with self.assertRaises(ValidationError):
            self.order.status = 'invalid_status'
            self.order.full_clean()

class OrderCalculationTests(OrderBaseTestCase):
    def setUp(self):
        super().setUp()
        self.order = Order.objects.create(
            client=self.client_user,
            device=self.device,
            employee=self.employee,
            status='in_progress'
        )

    def test_empty_order_cost(self):
        """Test that empty order has zero cost"""
        self.assertEqual(self.order.calculate_total_cost(), Decimal('0'))
        self.assertEqual(self.order.calculate_employee_earnings(), Decimal('0'))

    def test_service_only_order(self):
        """Test calculations for order with only services"""
        OrderService.objects.create(
            order=self.order,
            service=self.service,
            quantity=2,
            price_at_time=self.service.price
        )
        
        expected_total = Decimal('100.00') * 2
        expected_earnings = expected_total * Decimal('0.3')
        
        self.assertEqual(self.order.calculate_total_cost(), expected_total)
        self.assertEqual(self.order.calculate_employee_earnings(), expected_earnings)

    def test_parts_only_order(self):
        """Test calculations for order with only parts"""
        OrderPart.objects.create(
            order=self.order,
            part=self.part,
            quantity=3,
            price_at_time=self.part.price
        )
        
        expected_total = Decimal('50.00') * 3
        expected_earnings = expected_total * Decimal('0.1')
        
        self.assertEqual(self.order.calculate_total_cost(), expected_total)
        self.assertEqual(self.order.calculate_employee_earnings(), expected_earnings)

    def test_complex_order_calculations(self):
        """Test calculations for order with multiple services and parts"""
        # Add multiple services with different quantities
        OrderService.objects.create(
            order=self.order,
            service=self.service,
            quantity=2,
            price_at_time=self.service.price
        )
        
        service2 = Service.objects.create(
            name='Test Service 2',
            service_type=self.service_type,
            description='Test Description',
            price=Decimal('150.00'),
            duration=timedelta(hours=2)
        )
        OrderService.objects.create(
            order=self.order,
            service=service2,
            quantity=1,
            price_at_time=service2.price
        )
        
        # Add multiple parts with different quantities
        OrderPart.objects.create(
            order=self.order,
            part=self.part,
            quantity=3,
            price_at_time=self.part.price
        )
        
        part2 = Part.objects.create(
            part_type=self.part_type,
            name='Test Part 2',
            description='Test Description',
            price=Decimal('75.00'),
            quantity_in_stock=5
        )
        OrderPart.objects.create(
            order=self.order,
            part=part2,
            quantity=2,
            price_at_time=part2.price
        )
        
        # Calculate expected totals
        services_total = (Decimal('100.00') * 2) + (Decimal('150.00') * 1)
        parts_total = (Decimal('50.00') * 3) + (Decimal('75.00') * 2)
        expected_total = services_total + parts_total
        
        # Calculate expected earnings
        services_earnings = services_total * Decimal('0.3')
        parts_earnings = parts_total * Decimal('0.1')
        expected_earnings = services_earnings + parts_earnings
        
        self.assertEqual(self.order.calculate_total_cost(), expected_total)
        self.assertEqual(self.order.calculate_employee_earnings(), expected_earnings) 