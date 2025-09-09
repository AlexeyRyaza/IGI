from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from datetime import date, timedelta
from core.models import Client, Employee, Specialization

class PhoneNumberValidationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )

    def test_invalid_phone_numbers(self):
        """Test various invalid phone number formats"""
        invalid_numbers = [
            '+375291234567',  # No spaces and brackets
            '375 (29) 123-45-67',  # Missing plus
            '+375 (28) 123-45-67',  # Invalid operator code
            '+375 (29) 1234567',  # Missing hyphens
            '+375 (29) 123-45-678',  # Too many digits
            '+375 (29) 123-4-567',  # Wrong hyphen placement
            '+375(29)123-45-67',  # Missing spaces
            '+375 (29) 12-34-567'  # Wrong grouping
        ]
        
        for number in invalid_numbers:
            client = Client(
                user=self.user,
                phone_number=number,
                address='Test Address',
                birth_date=date(1990, 1, 1),
                passport_number='MP1234567'
            )
            with self.assertRaises(ValidationError):
                client.full_clean()

class AgeValidationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )
        self.specialization = Specialization.objects.create(
            name='Test Spec',
            description='Test Description'
        )

    def test_future_birth_date(self):
        """Test that birth dates in the future are invalid"""
        # Client with future birth date
        future_client = Client(
            user=self.user,
            phone_number='+375 (29) 123-45-67',
            address='Test Address',
            birth_date=date.today() + timedelta(days=1),
            passport_number='MP1234567'
        )
        with self.assertRaises(ValidationError):
            future_client.full_clean()

        # Employee with future birth date
        future_employee = Employee(
            user=self.user,
            phone_number='+375 (29) 123-45-67',
            birth_date=date.today() + timedelta(days=1),
            passport_number='MP1234567',
            hire_date=date.today()
        )
        with self.assertRaises(ValidationError):
            future_employee.full_clean()

class PassportValidationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )

    def test_valid_passport_numbers(self):
        """Test valid passport number formats"""
        valid_passports = [
            'MP1234567',
            'AB9876543',
            'KH5555555',
            'PP1111111'
        ]
        
        for passport in valid_passports:
            client = Client(
                user=self.user,
                phone_number='+375 (29) 123-45-67',
                address='Test Address',
                birth_date=date(1990, 1, 1),
                passport_number=passport
            )
            try:
                client.full_clean()
            except ValidationError as e:
                self.fail(f"Validation failed for valid passport {passport}: {e}")

    def test_invalid_passport_numbers(self):
        """Test invalid passport number formats"""
        invalid_passports = [
            'M1234567',    # Missing second letter
            'MPP123456',   # Three letters
            'MP123456',    # Too short
            'MP12345678',  # Too long
            'mp1234567',   # Lowercase letters
            '12345678',    # No letters
            'MPABCDEFG',   # Letters instead of numbers
            'M1P234567',   # Letters in wrong position
            '1MP234567',   # Numbers in wrong position
            'MP123456A'    # Letter at the end
        ]
        
        for passport in invalid_passports:
            client = Client(
                user=self.user,
                phone_number='+375 (29) 123-45-67',
                address='Test Address',
                birth_date=date(1990, 1, 1),
                passport_number=passport
            )
            with self.assertRaises(ValidationError):
                client.full_clean()

    def test_duplicate_passport_numbers(self):
        """Test that duplicate passport numbers are not allowed"""
        # Create first client
        Client.objects.create(
            user=self.user,
            phone_number='+375 (29) 123-45-67',
            address='Test Address',
            birth_date=date(1990, 1, 1),
            passport_number='MP1234567'
        )
        
        # Try to create another client with the same passport number
        user2 = User.objects.create_user(
            username='testuser2',
            password='testpass'
        )
        duplicate_client = Client(
            user=user2,
            phone_number='+375 (29) 987-65-43',
            address='Another Address',
            birth_date=date(1995, 1, 1),
            passport_number='MP1234567'
        )
        
        with self.assertRaises(ValidationError):
            duplicate_client.full_clean() 