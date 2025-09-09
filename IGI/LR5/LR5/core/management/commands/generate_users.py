from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from core.models import Client
from django.utils import timezone
from datetime import timedelta
import random

class Command(BaseCommand):
    help = 'Generates test users and clients'

    def handle(self, *args, **kwargs):
        self.stdout.write('Generating test users and clients...')
        
        # Создаем группы если их нет
        client_group, _ = Group.objects.get_or_create(name='Клиенты')
        staff_group, _ = Group.objects.get_or_create(name='Сотрудники')
        
        # Создаем тестового админа если его нет
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin'
            )
            self.stdout.write(self.style.SUCCESS(f'Created admin user: {admin_user.username}'))
        
        # Список имен и фамилий для генерации
        first_names = ['Александр', 'Иван', 'Петр', 'Михаил', 'Сергей', 'Андрей', 'Дмитрий', 
                      'Анна', 'Мария', 'Елена', 'Ольга', 'Татьяна', 'Наталья', 'Екатерина']
        last_names = ['Иванов', 'Петров', 'Сидоров', 'Смирнов', 'Кузнецов', 'Попов', 'Васильев',
                     'Иванова', 'Петрова', 'Сидорова', 'Смирнова', 'Кузнецова', 'Попова', 'Васильева']
        
        # Создаем тестовых пользователей и клиентов
        for i in range(10):  # Создаем 10 пользователей
            # Генерируем случайное имя и фамилию
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            if first_name[-1] == 'а':  # Если имя женское
                last_name = last_name + 'а'  # Добавляем окончание для фамилии
                
            username = f'user{i}'
            email = f'user{i}@example.com'
            
            # Создаем пользователя
            user = User.objects.create_user(
                username=username,
                email=email,
                password='password123',
                first_name=first_name,
                last_name=last_name
            )
            
            # Добавляем пользователя в группу клиентов
            user.groups.add(client_group)
            
            # Генерируем случайную дату рождения (от 18 до 70 лет)
            age = random.randint(18, 70)
            birth_date = timezone.now().date() - timedelta(days=age*365)
            
            # Создаем клиента
            client = Client.objects.create(
                user=user,
                phone_number=f'+375 (29) {random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(10, 99)}',
                address=f'ул. Примерная, д. {random.randint(1, 100)}, кв. {random.randint(1, 100)}',
                birth_date=birth_date,
                passport_number=f'MP{random.randint(1000000, 9999999)}'
            )
            
            self.stdout.write(self.style.SUCCESS(f'Created user and client: {user.username}'))
        
        self.stdout.write(self.style.SUCCESS('Successfully generated all test users and clients')) 