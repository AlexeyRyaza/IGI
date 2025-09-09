from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from core.models import (
    Service, ServiceType, Order, Device, DeviceType,
    Client as ClientModel  # Renamed to avoid conflict
)
from datetime import timedelta, date
from decimal import Decimal
import json

class APITestCase(TestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass',
            email='test@example.com'
        )
        
        # Create client profile for user
        self.client_profile = ClientModel.objects.create(
            user=self.user,
            phone_number='+375 (29) 123-45-67',
            address='Test Address',
            birth_date=date(1990, 1, 1),
            passport_number='MP1234567'
        )
        
        self.client = Client()
        
        # Create test data
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