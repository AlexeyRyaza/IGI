from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import Order, Service, Client, Employee, Device, DeviceType
from datetime import timedelta, datetime
from decimal import Decimal
import random

class Command(BaseCommand):
    help = 'Creates test orders for a specific date'

    def add_arguments(self, parser):
        parser.add_argument(
            '--date',
            type=str,
            help='Date for orders in format DD/MM/YYYY',
        )
        parser.add_argument(
            '--count',
            type=int,
            default=10,
            help='Number of orders to create',
        )

    def handle(self, *args, **kwargs):
        # Парсим дату или используем текущую
        if kwargs['date']:
            try:
                date_str = kwargs['date']
                order_date = datetime.strptime(date_str, '%d/%m/%Y')
                order_date = timezone.make_aware(order_date)
            except ValueError:
                self.stdout.write(self.style.ERROR('Invalid date format. Use DD/MM/YYYY'))
                return
        else:
            order_date = timezone.now()

        count = kwargs['count']
        
        # Получаем существующие данные
        clients = list(Client.objects.all())
        employees = list(Employee.objects.all())
        services = list(Service.objects.all())
        
        if not clients or not employees or not services:
            self.stdout.write(self.style.ERROR('Необходимо сначала создать клиентов, сотрудников и услуги'))
            return
        
        # Получаем или создаем тип устройства
        device_type, _ = DeviceType.objects.get_or_create(
            name='Смартфон',
            defaults={'description': 'Мобильные телефоны и смартфоны'}
        )
        
        # Создаем заказы
        for i in range(count):
            # Создаем устройство
            device = Device.objects.create(
                device_type=device_type,
                brand=random.choice(['Apple', 'Samsung', 'Xiaomi', 'Huawei']),
                model=f'Model-{order_date.strftime("%Y%m%d")}-{i}',
                serial_number=f'SN{order_date.strftime("%Y%m%d")}-{random.randint(1000, 9999)}',
                description='Тестовое устройство'
            )
            
            # Создаем заказ
            order = Order.objects.create(
                client=random.choice(clients),
                device=device,
                employee=random.choice(employees),
                status=random.choice(['pending', 'in_progress', 'completed', 'cancelled']),
                created_at=order_date,
                visit_date=order_date.date(),
                total_cost=Decimal(random.randint(50, 500)),
                description='Тестовый заказ'
            )
            
            # Добавляем случайные услуги к заказу
            num_services = random.randint(1, 3)
            selected_services = random.sample(services, num_services)
            for service in selected_services:
                order.orderservice_set.create(
                    service=service,
                    quantity=1,
                    price_at_time=service.price
                )
            
            # Обновляем общую стоимость заказа
            total_cost = sum(os.price_at_time * os.quantity for os in order.orderservice_set.all())
            order.total_cost = total_cost
            order.save()
            
            self.stdout.write(self.style.SUCCESS(f'Created order #{order.id} for {order_date.strftime("%d/%m/%Y")}'))
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {count} orders for {order_date.strftime("%d/%m/%Y")}'
            )
        ) 