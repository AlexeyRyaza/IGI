from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, RegexValidator, MaxValueValidator
from datetime import date
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from decimal import Decimal
from django.core.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
import re

class ServiceType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Тип услуги"
        verbose_name_plural = "Типы услуг"

class Service(models.Model):
    name = models.CharField(max_length=200)
    service_type = models.ForeignKey(ServiceType, on_delete=models.CASCADE, related_name='services')
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    duration = models.DurationField(help_text="Примерная длительность оказания услуги")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.service_type})"

    class Meta:
        verbose_name = "Услуга"
        verbose_name_plural = "Услуги"

class DeviceType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Тип устройства"
        verbose_name_plural = "Типы устройств"

class Device(models.Model):
    device_type = models.ForeignKey(DeviceType, on_delete=models.CASCADE, related_name='devices')
    brand = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    serial_number = models.CharField(max_length=100, unique=True)
    description = models.TextField()

    def __str__(self):
        return f"{self.brand} {self.model}"

    class Meta:
        verbose_name = "Устройство"
        verbose_name_plural = "Устройства"

class PartType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Тип запчасти"
        verbose_name_plural = "Типы запчастей"

class Part(models.Model):
    part_type = models.ForeignKey(PartType, on_delete=models.CASCADE, related_name='parts')
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    quantity_in_stock = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.part_type})"

    class Meta:
        verbose_name = "Запчасть"
        verbose_name_plural = "Запчасти"

class Specialization(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Специализация"
        verbose_name_plural = "Специализации"

def validate_age(birth_date, min_age=18):
    """Validate that person is at least min_age years old"""
    if birth_date > date.today():
        raise ValidationError('Дата рождения не может быть в будущем')
    
    age = relativedelta(date.today(), birth_date).years
    if age < min_age:
        raise ValidationError(f'Возраст должен быть не менее {min_age} лет')

def validate_passport_number(passport_number):
    """Validate passport number format (2 uppercase letters followed by 7 digits)"""
    if not re.match(r'^[A-Z]{2}\d{7}$', passport_number):
        raise ValidationError('Неверный формат номера паспорта. Должно быть 2 заглавные буквы и 7 цифр')

class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    specializations = models.ManyToManyField(Specialization, related_name='employees')
    phone_regex = RegexValidator(
        regex=r'^\+375 \((?:29|33|44|25)\) [0-9]{3}-[0-9]{2}-[0-9]{2}$',
        message="Номер телефона должен быть в формате: '+375 (29) XXX-XX-XX'"
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=19)
    birth_date = models.DateField()
    passport_number = models.CharField(
        'Номер паспорта',
        max_length=9,
        unique=True,
        validators=[validate_passport_number]
    )
    hire_date = models.DateField()

    def clean(self):
        super().clean()
        validate_age(self.birth_date)

    def __str__(self):
        return f"{self.user.get_full_name()} - {', '.join(s.name for s in self.specializations.all())}"

    class Meta:
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"

class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_regex = RegexValidator(
        regex=r'^\+375 \((?:29|33|44|25)\) [0-9]{3}-[0-9]{2}-[0-9]{2}$',
        message="Номер телефона должен быть в формате: '+375 (29) XXX-XX-XX'"
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=19)
    address = models.TextField()
    birth_date = models.DateField()
    passport_number = models.CharField(
        'Номер паспорта',
        max_length=9,
        unique=True,
        validators=[validate_passport_number]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        super().clean()
        validate_age(self.birth_date)

    def __str__(self):
        return self.user.get_full_name()

    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'В ожидании'),
        ('in_progress', 'В работе'),
        ('completed', 'Завершен'),
        ('cancelled', 'Отменен'),
    ]

    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='orders')
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    services = models.ManyToManyField(Service, through='OrderService')
    parts = models.ManyToManyField(Part, through='OrderPart')
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    visit_date = models.DateField(default=timezone.now, help_text="Дата визита в сервисный центр")
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    description = models.TextField(blank=True)

    def calculate_employee_earnings(self):
        """Вычисляет заработок сотрудника с заказа"""
        # Процент от услуг (30%)
        services_earnings = sum(
            service.price_at_time * service.quantity * Decimal('0.3')
            for service in self.orderservice_set.all()
        )
        
        # Процент от запчастей (10%)
        parts_earnings = sum(
            part.price_at_time * part.quantity * Decimal('0.1')
            for part in self.orderpart_set.all()
        )
        
        return services_earnings + parts_earnings

    def calculate_total_cost(self):
        """Вычисляет общую стоимость заказа"""
        # Стоимость услуг
        services_cost = sum(
            service.price_at_time * service.quantity
            for service in self.orderservice_set.all()
        )
        
        # Стоимость запчастей
        parts_cost = sum(
            part.price_at_time * part.quantity
            for part in self.orderpart_set.all()
        )
        
        return services_cost + parts_cost

    def save(self, *args, **kwargs):
        if not self._state.adding:  # Если это обновление существующего заказа
            self.total_cost = self.calculate_total_cost()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Заказ #{self.id} - {self.client}"

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

class OrderService(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price_at_time = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.service.name} x{self.quantity} для заказа #{self.order.id}"

    class Meta:
        verbose_name = "Услуга в заказе"
        verbose_name_plural = "Услуги в заказе"

class OrderPart(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    part = models.ForeignKey(Part, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price_at_time = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.part.name} x{self.quantity} для заказа #{self.order.id}"

    class Meta:
        verbose_name = "Запчасть в заказе"
        verbose_name_plural = "Запчасти в заказе"

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    birth_date = models.DateField()

    def __str__(self):
        return f"Профиль пользователя {self.user.username}"

    class Meta:
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance, birth_date=date.today())  # временная дата для существующих пользователей

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        instance.profile.save()
    except Profile.DoesNotExist:
        Profile.objects.create(user=instance, birth_date=date.today())  # временная дата для существующих пользователей

class Article(models.Model):
    title = models.CharField('Заголовок', max_length=200)
    content = models.TextField('Содержание')
    short_description = models.CharField('Краткое описание', max_length=300)
    image = models.ImageField('Изображение', upload_to='articles/', null=True, blank=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    is_published = models.BooleanField('Опубликовано', default=True)

    def clean(self):
        super().clean()
        if not self.title:
            raise ValidationError({'title': 'Заголовок не может быть пустым'})
        if not self.content:
            raise ValidationError({'content': 'Содержание не может быть пустым'})
        if len(self.short_description) > 300:
            raise ValidationError({'short_description': 'Краткое описание не может быть длиннее 300 символов'})

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Статья'
        verbose_name_plural = 'Статьи'

class CompanyInfo(models.Model):
    title = models.CharField('Заголовок', max_length=200)
    content = models.TextField('Содержание')
    year = models.IntegerField('Год основания', null=True, blank=True)
    logo = models.ImageField('Логотип', upload_to='company/', null=True, blank=True)
    video_url = models.URLField('URL видео', null=True, blank=True)
    order = models.IntegerField('Порядок', default=0)

    def clean(self):
        super().clean()
        if not self.title:
            raise ValidationError({'title': 'Заголовок не может быть пустым'})
        if not self.content:
            raise ValidationError({'content': 'Содержание не может быть пустым'})
        if self.year and self.year > timezone.now().year:
            raise ValidationError({'year': 'Год не может быть больше текущего'})

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['order', 'title']
        verbose_name = 'Информация о компании'
        verbose_name_plural = 'Информация о компании'

class FAQ(models.Model):
    ENTRY_TYPE_CHOICES = [
        ('term', 'Термин словаря'),
        ('question', 'Вопрос-ответ'),
    ]
    
    title = models.CharField(max_length=200, verbose_name='Заголовок', default='')
    content = models.TextField(verbose_name='Содержание', default='')
    entry_type = models.CharField(
        max_length=10,
        choices=ENTRY_TYPE_CHOICES,
        default='term',
        verbose_name='Тип записи'
    )
    order = models.IntegerField(default=0, verbose_name='Порядок отображения')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = 'FAQ/Словарь'
        verbose_name_plural = 'FAQ/Словарь'
        ordering = ['order', 'title']

    def __str__(self):
        return f"{self.get_entry_type_display()}: {self.title}"

class ContactEmployee(models.Model):
    name = models.CharField(max_length=100, verbose_name="ФИО")
    position = models.CharField(max_length=100, verbose_name="Должность")
    description = models.TextField(verbose_name="Описание обязанностей")
    photo = models.ImageField(upload_to='employees/', verbose_name="Фото", null=True, blank=True)
    email = models.EmailField(verbose_name="Email")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    order = models.IntegerField(default=0, verbose_name="Порядок отображения")

    def __str__(self):
        return f"{self.name} - {self.position}"

    class Meta:
        verbose_name = "Сотрудник для контактов"
        verbose_name_plural = "Сотрудники для контактов"
        ordering = ['order']

class Dictionary(models.Model):
    question = models.CharField(max_length=255, verbose_name="Вопрос")
    answer = models.TextField(verbose_name="Ответ")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")

    def __str__(self):
        return self.question

    class Meta:
        verbose_name = "Термин словаря"
        verbose_name_plural = "Словарь терминов"
        ordering = ['-created_at']

class Vacancy(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название вакансии")
    description = models.TextField(verbose_name="Описание")
    requirements = models.TextField(verbose_name="Требования")
    salary_from = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Зарплата от", null=True, blank=True)
    salary_to = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Зарплата до", null=True, blank=True)
    is_active = models.BooleanField(default=True, verbose_name="Активна")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Вакансия"
        verbose_name_plural = "Вакансии"
        ordering = ['-created_at']

class Review(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, verbose_name="Пользователь")
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Оценка"
    )
    text = models.TextField(verbose_name="Текст отзыва")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    is_published = models.BooleanField(default=False, verbose_name="Опубликован")

    def __str__(self):
        return f"Отзыв от {self.user.get_full_name()} ({self.rating}★)"

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        ordering = ['-created_at']

class Promo(models.Model):
    code = models.CharField('Промокод', max_length=20, unique=True)
    description = models.TextField('Описание')
    discount = models.IntegerField('Скидка (%)')
    valid_from = models.DateTimeField('Действует с')
    valid_to = models.DateTimeField('Действует до')
    is_active = models.BooleanField('Активен', default=True)

    def clean(self):
        super().clean()
        if self.discount < 0 or self.discount > 100:
            raise ValidationError({'discount': 'Скидка должна быть от 0 до 100%'})
        if self.valid_to <= self.valid_from:
            raise ValidationError({'valid_to': 'Дата окончания должна быть позже даты начала'})

    @property
    def is_valid(self):
        now = timezone.now()
        return (
            self.is_active and
            self.valid_from <= now <= self.valid_to
        )

    def __str__(self):
        return f"{self.code} ({self.discount}%)"

    class Meta:
        verbose_name = 'Промокод'
        verbose_name_plural = 'Промокоды'
        ordering = ['-valid_from'] 