from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import FAQ, Order, Service, Client, Employee, Device, DeviceType
from django.contrib.auth.models import User
import random
from datetime import timedelta, datetime
from decimal import Decimal

class Command(BaseCommand):
    help = 'Generates test data for FAQ and Orders'

    def handle(self, *args, **kwargs):
        self.stdout.write('Generating test data...')
        
        # Генерируем FAQ записи
        faq_data = [
            {
                'entry_type': 'term',
                'title': 'Диагностика',
                'content': 'Комплексная проверка устройства для выявления неисправностей и определения необходимого ремонта.'
            },
            {
                'entry_type': 'term',
                'title': 'Модульный ремонт',
                'content': 'Замена неисправных модулей устройства на новые без вмешательства в их внутреннюю структуру.'
            },
            {
                'entry_type': 'term',
                'title': 'Компонентный ремонт',
                'content': 'Ремонт на уровне электронных компонентов устройства с использованием паяльного оборудования.'
            },
            {
                'entry_type': 'question',
                'title': 'Как долго длится ремонт?',
                'content': 'Стандартный срок ремонта составляет 1-3 рабочих дня. Точные сроки зависят от сложности неисправности и наличия необходимых запчастей.'
            },
            {
                'entry_type': 'question',
                'title': 'Есть ли гарантия на ремонт?',
                'content': 'Да, мы предоставляем гарантию на все виды ремонтных работ. Срок гарантии зависит от типа ремонта и составляет от 30 до 180 дней.'
            },
            {
                'entry_type': 'question',
                'title': 'Что делать, если устройство сломалось на гарантии?',
                'content': 'В случае поломки устройства в течение гарантийного срока необходимо обратиться в наш сервисный центр с гарантийным талоном. Ремонт будет произведен бесплатно, если поломка произошла не по вине пользователя.'
            },
            {
                'entry_type': 'term',
                'title': 'Пайка BGA',
                'content': 'Технология замены или восстановления микросхем с шариковыми выводами с использованием специального оборудования.'
            },
            {
                'entry_type': 'question',
                'title': 'Как записаться на ремонт?',
                'content': 'Записаться на ремонт можно через наш сайт, по телефону или придя лично в сервисный центр. При онлайн-записи вы можете выбрать удобное время визита.'
            },
            {
                'entry_type': 'question',
                'title': 'Сколько стоит диагностика?',
                'content': 'Базовая диагностика устройства бесплатна. Если требуется углубленная диагностика с разбором устройства, её стоимость составит от 20 рублей.'
            },
            {
                'entry_type': 'term',
                'title': 'Прошивка',
                'content': 'Обновление или восстановление программного обеспечения устройства.'
            },
        ]
        
        # Создаем FAQ записи
        for i, data in enumerate(faq_data):
            FAQ.objects.create(
                title=data['title'],
                content=data['content'],
                entry_type=data['entry_type'],
                order=i
            )
        
        # Получаем существующие данные для создания заказов
        clients = list(Client.objects.all())
        employees = list(Employee.objects.all())
        services = list(Service.objects.all())
        
        if not clients or not employees or not services:
            self.stdout.write(self.style.ERROR('Необходимо сначала создать клиентов, сотрудников и услуги'))
            return
        
        # Создаем тестовые заказы за последние 30 дней
        end_date = timezone.now()
        start_date = end_date - timedelta(days=30)
        
        # Получаем или создаем тип устройства
        device_type, _ = DeviceType.objects.get_or_create(
            name='Смартфон',
            defaults={'description': 'Мобильные телефоны и смартфоны'}
        )
        
        # Создаем заказы
        for i in range(50):  # Создаем 50 заказов
            # Случайная дата за последние 30 дней
            random_days = random.randint(0, 30)
            order_date = end_date - timedelta(days=random_days)
            
            # Создаем устройство
            device = Device.objects.create(
                device_type=device_type,
                brand=random.choice(['Apple', 'Samsung', 'Xiaomi', 'Huawei']),
                model=f'Model-{i}',
                serial_number=f'SN{i}-{random.randint(1000, 9999)}',
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
        
        self.stdout.write(self.style.SUCCESS('Successfully generated test data')) 