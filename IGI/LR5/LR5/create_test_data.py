from core.models import *
from django.contrib.auth.models import User
import random
from datetime import datetime, timedelta, date
from django.utils import timezone
from decimal import Decimal

def create_test_data():
    # Создаем информацию о компании
    CompanyInfo.objects.create(
        title="Сервисный центр TechSupport",
        content="""Мы предоставляем профессиональные услуги по ремонту и обслуживанию компьютерной техники с 2010 года.
        Наша команда состоит из опытных специалистов, которые постоянно совершенствуют свои навыки.
        Мы используем только оригинальные запчасти и современное оборудование для диагностики и ремонта.""",
        year=2010,
        video_url="https://www.youtube.com/embed/dQw4w9WgXcQ"
    )

    # Создаем новости
    articles = [
        {
            "title": "Новые методы ремонта iPhone 15",
            "content": """Наши специалисты прошли обучение по ремонту новейших моделей iPhone 15. 
            Теперь мы можем предложить полный спектр услуг по ремонту этих устройств, включая замену экрана, 
            батареи и других компонентов.""",
            "short_description": "Освоены новые технологии ремонта iPhone 15",
            "image": "articles/iphone_repair.jpg",
            "is_published": True,
            "created_at": timezone.now() - timedelta(days=2)
        },
        {
            "title": "Скидки на ремонт ноутбуков",
            "content": """В течение всего марта действуют специальные цены на диагностику и ремонт ноутбуков. 
            Приносите свои устройства и получите профессиональную консультацию бесплатно.""",
            "short_description": "Весенние скидки на ремонт ноутбуков",
            "image": "articles/laptop_repair.jpg",
            "is_published": True,
            "created_at": timezone.now() - timedelta(days=5)
        },
        {
            "title": "Расширение спектра услуг",
            "content": """Мы рады сообщить о запуске нового направления - ремонт игровых консолей. 
            Теперь вы можете обратиться к нам за профессиональным ремонтом PlayStation, Xbox и Nintendo Switch.""",
            "short_description": "Новая услуга - ремонт игровых консолей",
            "image": "articles/console_repair.jpg",
            "is_published": True,
            "created_at": timezone.now() - timedelta(days=7)
        },
        {
            "title": "Открытие нового филиала",
            "content": """Спешим сообщить об открытии нового филиала нашего сервисного центра в южном районе города. 
            Теперь наши услуги стали еще доступнее для вас.""",
            "short_description": "Открыт новый филиал сервисного центра",
            "image": "articles/new_office.jpg",
            "is_published": True,
            "created_at": timezone.now() - timedelta(days=10)
        }
    ]

    for article_data in articles:
        Article.objects.create(**article_data)

    # Создаем словарь терминов
    terms = [
        {
            "question": "SSD",
            "answer": "Твердотельный накопитель (Solid State Drive) - устройство для хранения данных, не имеющее движущихся механических частей и обеспечивающее более высокую скорость работы по сравнению с традиционными жесткими дисками.",
            "order": 1
        },
        {
            "question": "Материнская плата",
            "answer": "Основная печатная плата компьютера, объединяющая все компоненты системы и обеспечивающая их взаимодействие.",
            "order": 2
        },
        {
            "question": "Оперативная память (RAM)",
            "answer": "Временное хранилище данных, необходимое для работы запущенных программ. Очищается при выключении компьютера.",
            "order": 3
        },
        {
            "question": "Процессор (CPU)",
            "answer": "Центральный обрабатывающий блок компьютера, выполняющий основные вычислительные операции.",
            "order": 4
        },
        {
            "question": "Видеокарта (GPU)",
            "answer": "Устройство, отвечающее за обработку графической информации и вывод изображения на экран.",
            "order": 5
        },
        {
            "question": "BIOS",
            "answer": "Базовая система ввода-вывода, обеспечивающая загрузку операционной системы и настройку оборудования.",
            "order": 6
        },
        {
            "question": "Драйвер",
            "answer": "Программное обеспечение, обеспечивающее взаимодействие операционной системы с аппаратным обеспечением.",
            "order": 7
        },
        {
            "question": "Тачскрин",
            "answer": "Сенсорный экран, позволяющий управлять устройством путем прикосновений к экрану.",
            "order": 8
        },
        {
            "question": "Термопаста",
            "answer": "Теплопроводящий материал, используемый для улучшения теплового контакта между процессором и системой охлаждения.",
            "order": 9
        },
        {
            "question": "Флешка (USB-накопитель)",
            "answer": "Портативное устройство для хранения и переноса данных, подключаемое через USB-порт.",
            "order": 10
        }
    ]

    for term_data in terms:
        FAQ.objects.create(**term_data)

    # Создаем вакансии
    vacancies = [
        {
            "title": "Мастер по ремонту смартфонов",
            "description": """Требуется опытный мастер по ремонту мобильных устройств.
            Обязанности:
            - Диагностика неисправностей
            - Ремонт смартфонов различных производителей
            - Замена комплектующих
            - Консультация клиентов""",
            "requirements": """- Опыт работы от 2 лет
            - Знание устройства современных смартфонов
            - Умение работать с паяльным оборудованием
            - Ответственность и аккуратность""",
            "salary_from": Decimal("1500.00"),
            "salary_to": Decimal("3000.00"),
            "is_active": True
        },
        {
            "title": "Мастер по ремонту ноутбуков",
            "description": """Ищем специалиста по ремонту ноутбуков в нашу команду.
            Обязанности:
            - Диагностика неисправностей
            - Модульный и компонентный ремонт
            - Замена матриц, клавиатур, разъемов
            - Чистка и профилактика""",
            "requirements": """- Опыт работы от 1 года
            - Знание устройства ноутбуков разных производителей
            - Навыки пайки BGA компонентов
            - Умение работать с сервисной документацией""",
            "salary_from": Decimal("1200.00"),
            "salary_to": Decimal("2500.00"),
            "is_active": True
        },
        {
            "title": "Администратор сервисного центра",
            "description": """Требуется администратор для работы с клиентами.
            Обязанности:
            - Прием и оформление заказов
            - Консультирование клиентов
            - Ведение документации
            - Работа с кассой""",
            "requirements": """- Опыт работы в сфере обслуживания
            - Знание ПК на уровне уверенного пользователя
            - Грамотная речь
            - Стрессоустойчивость""",
            "salary_from": Decimal("1000.00"),
            "salary_to": Decimal("1500.00"),
            "is_active": True
        }
    ]

    for vacancy_data in vacancies:
        Vacancy.objects.create(**vacancy_data)

    # Создаем контактных сотрудников
    contacts = [
        {
            "name": "Иванов Иван Иванович",
            "position": "Генеральный директор",
            "description": "Управление компанией и стратегическое развитие",
            "email": "ivanov@techsupport.com",
            "phone": "+375 (29) 123-45-67",
            "photo": "employees/director.jpg",
            "order": 1
        },
        {
            "name": "Петрова Анна Михайловна",
            "position": "Менеджер по работе с клиентами",
            "description": "Консультация клиентов и координация работы сервисного центра",
            "email": "petrova@techsupport.com",
            "phone": "+375 (29) 234-56-78",
            "photo": "employees/manager.jpg",
            "order": 2
        },
        {
            "name": "Сидоров Петр Алексеевич",
            "position": "Главный инженер",
            "description": "Техническая экспертиза и контроль качества ремонта",
            "email": "sidorov@techsupport.com",
            "phone": "+375 (29) 345-67-89",
            "photo": "employees/engineer.jpg",
            "order": 3
        }
    ]

    for contact_data in contacts:
        ContactEmployee.objects.create(**contact_data)

    # Создаем промокоды
    now = timezone.now()
    
    # Активные промокоды
    active_promos = [
        {
            "code": "WELCOME2024",
            "description": "Скидка для новых клиентов",
            "discount": 15,
            "valid_from": now,
            "valid_to": now + timedelta(days=30),
            "is_active": True
        },
        {
            "code": "SPRING2024",
            "description": "Весенняя акция на все услуги",
            "discount": 10,
            "valid_from": now,
            "valid_to": now + timedelta(days=60),
            "is_active": True
        }
    ]

    # Архивные промокоды
    archived_promos = [
        {
            "code": "WINTER2023",
            "description": "Зимняя акция",
            "discount": 20,
            "valid_from": now - timedelta(days=60),
            "valid_to": now - timedelta(days=1),
            "is_active": False
        },
        {
            "code": "NEWYEAR2024",
            "description": "Новогодняя акция",
            "discount": 25,
            "valid_from": now - timedelta(days=30),
            "valid_to": now - timedelta(days=1),
            "is_active": False
        }
    ]

    for promo_data in active_promos + archived_promos:
        Promo.objects.create(**promo_data)

    # Создаем типы услуг
    service_types = [
        ServiceType.objects.create(name='Ремонт смартфонов', description='Ремонт и обслуживание мобильных телефонов'),
        ServiceType.objects.create(name='Ремонт ноутбуков', description='Ремонт и обслуживание ноутбуков'),
        ServiceType.objects.create(name='Ремонт планшетов', description='Ремонт и обслуживание планшетов'),
        ServiceType.objects.create(name='Ремонт ПК', description='Ремонт и обслуживание компьютеров'),
        ServiceType.objects.create(name='Ремонт мониторов', description='Ремонт и обслуживание мониторов'),
        ServiceType.objects.create(name='Ремонт принтеров', description='Ремонт и обслуживание принтеров'),
        ServiceType.objects.create(name='Ремонт МФУ', description='Ремонт и обслуживание МФУ'),
        ServiceType.objects.create(name='Настройка ПО', description='Установка и настройка программного обеспечения'),
        ServiceType.objects.create(name='Восстановление данных', description='Восстановление утерянных данных'),
        ServiceType.objects.create(name='Диагностика', description='Диагностика неисправностей')
    ]

    # Создаем услуги
    services = []
    for st in service_types:
        services.extend([
            Service.objects.create(
                name=f'Базовый {st.name.lower()}',
                description=f'Базовое обслуживание - {st.description.lower()}',
                price=random.randint(1000, 3000),
                duration=timedelta(minutes=random.randint(30, 120)),  # Длительность от 30 до 120 минут
                service_type=st
            ),
            Service.objects.create(
                name=f'Сложный {st.name.lower()}',
                description=f'Сложный ремонт - {st.description.lower()}',
                price=random.randint(3000, 7000),
                duration=timedelta(minutes=random.randint(120, 360)),  # Длительность от 2 до 6 часов
                service_type=st
            )
        ])

    # Создаем типы устройств
    device_types = [
        DeviceType.objects.create(name='Смартфон'),
        DeviceType.objects.create(name='Ноутбук'),
        DeviceType.objects.create(name='Планшет'),
        DeviceType.objects.create(name='Компьютер'),
        DeviceType.objects.create(name='Монитор'),
        DeviceType.objects.create(name='Принтер'),
        DeviceType.objects.create(name='МФУ'),
        DeviceType.objects.create(name='Сервер'),
        DeviceType.objects.create(name='Роутер'),
        DeviceType.objects.create(name='Сетевое оборудование')
    ]

    # Создаем типы запчастей
    part_types = [
        PartType.objects.create(name='Дисплей'),
        PartType.objects.create(name='Аккумулятор'),
        PartType.objects.create(name='Материнская плата'),
        PartType.objects.create(name='Процессор'),
        PartType.objects.create(name='Оперативная память'),
        PartType.objects.create(name='Жесткий диск'),
        PartType.objects.create(name='Блок питания'),
        PartType.objects.create(name='Клавиатура'),
        PartType.objects.create(name='Корпус'),
        PartType.objects.create(name='Разъемы')
    ]

    # Создаем запчасти
    parts = []
    for pt in part_types:
        parts.extend([
            Part.objects.create(
                name=f'{pt.name} тип A',
                description=f'Базовая модель {pt.name.lower()}',
                price=random.randint(500, 2000),
                quantity_in_stock=random.randint(5, 20),
                part_type=pt
            ),
            Part.objects.create(
                name=f'{pt.name} тип B',
                description=f'Улучшенная модель {pt.name.lower()}',
                price=random.randint(2000, 5000),
                quantity_in_stock=random.randint(3, 10),
                part_type=pt
            )
        ])

    # Создаем специализации
    specializations = [
        Specialization.objects.create(name='Мастер по смартфонам'),
        Specialization.objects.create(name='Мастер по ноутбукам'),
        Specialization.objects.create(name='Мастер по планшетам'),
        Specialization.objects.create(name='Системный администратор'),
        Specialization.objects.create(name='Специалист по сетям'),
        Specialization.objects.create(name='Мастер по принтерам'),
        Specialization.objects.create(name='Специалист по восстановлению данных'),
        Specialization.objects.create(name='Мастер по ремонту ПК'),
        Specialization.objects.create(name='Специалист по диагностике'),
        Specialization.objects.create(name='Универсальный мастер')
    ]

    # Создаем сотрудников
    employees = []
    for i in range(10):
        birth_date = date.today() - timedelta(days=random.randint(6570, 18250))  # От 18 до 50 лет
        user = User.objects.create_user(
            username=f'employee{i}',
            password='employee123',
            first_name=f'Имя{i}',
            last_name=f'Фамилия{i}',
            email=f'employee{i}@example.com'
        )
        # Обновляем профиль пользователя
        user.profile.birth_date = birth_date
        user.profile.save()

        employee = Employee.objects.create(
            user=user,
            phone_number=f'+375 (29) {random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(10, 99)}',
            birth_date=birth_date,
            passport_number=f'MP{random.randint(1000000, 9999999)}',
            hire_date=date.today() - timedelta(days=random.randint(0, 3650))  # До 10 лет стажа
        )
        # Добавляем 2-3 специализации каждому сотруднику
        for spec in random.sample(list(specializations), random.randint(2, 3)):
            employee.specializations.add(spec)
        employees.append(employee)

    # Создаем клиентов
    clients = []
    for i in range(10):
        birth_date = date.today() - timedelta(days=random.randint(6570, 25000))  # От 18 до ~68 лет
        user = User.objects.create_user(
            username=f'client{i}',
            password='client123',
            first_name=f'Клиент{i}',
            last_name=f'Фамилия{i}',
            email=f'client{i}@example.com'
        )
        # Обновляем профиль пользователя
        user.profile.birth_date = birth_date
        user.profile.save()
        
        client = Client.objects.create(
            user=user,
            phone_number=f'+375 (29) {random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(10, 99)}',
            address=f'ул. Клиентская, д. {i}',
            birth_date=birth_date,
            passport_number=f'MP{random.randint(1000000, 9999999)}'
        )
        clients.append(client)

    # Создаем устройства для клиентов
    devices = []
    for client in clients:
        for _ in range(2):  # 2 устройства для каждого клиента
            device_type = random.choice(device_types)
            device = Device.objects.create(
                device_type=device_type,
                brand=random.choice(['Apple', 'Samsung', 'Xiaomi', 'Huawei']),
                model=f'Model {random.randint(1, 10)}',
                serial_number=f'SN{random.randint(10000, 99999)}',
                description='Описание устройства'
            )
            devices.append(device)

    # Создаем заказы
    for client in clients:
        # Создаем случайное устройство для клиента
        device_type = random.choice(device_types)
        device = Device.objects.create(
            device_type=device_type,
            brand=random.choice(['Apple', 'Samsung', 'Xiaomi', 'Huawei']),
            model=f'Model {random.randint(1, 10)}',
            serial_number=f'SN{random.randint(10000, 99999)}',
            description='Описание устройства'
        )
        
        # Создаем заказ
        order = Order.objects.create(
            client=client,
            device=device,
            employee=random.choice(employees) if random.random() > 0.3 else None,
            status=random.choice(['pending', 'in_progress', 'completed', 'cancelled']),
            visit_date=timezone.now() + timedelta(days=random.randint(-30, 30)),
            total_cost=Decimal(random.randint(50, 500)),
            description=f'Заказ на ремонт {device.brand} {device.model}'
        )
        
        # Добавляем 1-3 услуги к заказу
        for service in random.sample(services, random.randint(1, 3)):
            OrderService.objects.create(
                order=order,
                service=service,
                quantity=1,
                price_at_time=service.price
            )
        
        # Добавляем 1-3 запчасти к заказу
        for part in random.sample(parts, random.randint(1, 3)):
            OrderPart.objects.create(
                order=order,
                part=part,
                quantity=random.randint(1, 3),
                price_at_time=part.price
            )

    # Создаем отзывы (автоматически одобренные)
    reviews = [
        {
            "rating": 5,
            "text": "Отличный сервис! Быстро починили мой ноутбук, очень доволен качеством работы.",
            "is_published": True  # Автоматически одобряем отзыв
        },
        {
            "rating": 4,
            "text": "Хороший сервисный центр, профессиональный подход к работе.",
            "is_published": True
        },
        {
            "rating": 5,
            "text": "Спасибо за оперативный ремонт телефона! Рекомендую всем.",
            "is_published": True
        }
    ]

    # Создаем тестового пользователя для отзывов
    user = User.objects.create_user(
        username='reviewer',
        password='reviewer123',
        first_name='Тестовый',
        last_name='Пользователь'
    )

    for review_data in reviews:
        Review.objects.create(user=user, **review_data)

    print('Тестовые данные успешно созданы!')

if __name__ == '__main__':
    create_test_data() 