from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from datetime import date
from .models import Profile, Order, OrderService, Service, Employee, Device, Part, Client, Review, validate_passport_number

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        help_text='Обязательное поле. Введите действующий адрес электронной почты.'
    )
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    birth_date = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        help_text='Обязательное поле. Вам должно быть не менее 18 лет.'
    )
    phone_number = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text='Введите номер телефона в формате: +375 (29) XXX-XX-XX'
    )
    address = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        help_text='Введите ваш адрес'
    )
    passport_number = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text='Введите номер паспорта'
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'birth_date', 'phone_number', 'address', 'passport_number', 'password1', 'password2')

    def clean_birth_date(self):
        birth_date = self.cleaned_data.get('birth_date')
        if birth_date:
            age = (date.today() - birth_date).days / 365.25
            if age < 18:
                raise ValidationError('Вам должно быть не менее 18 лет для регистрации.')
        return birth_date

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('Пользователь с таким email уже существует.')
        return email

    def clean_passport_number(self):
        passport_number = self.cleaned_data.get('passport_number')
        try:
            validate_passport_number(passport_number)
        except ValidationError as e:
            raise forms.ValidationError(str(e))
            
        # Проверяем уникальность номера паспорта
        if Client.objects.filter(passport_number=passport_number).exists():
            raise forms.ValidationError('Пользователь с таким номером паспорта уже существует.')
            
        return passport_number.upper()  # Преобразуем в верхний регистр для единообразия

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            # Создаем или обновляем профиль пользователя
            Profile.objects.update_or_create(
                user=user,
                defaults={'birth_date': self.cleaned_data['birth_date']}
            )
            # Создаем или обновляем профиль клиента
            Client.objects.update_or_create(
                user=user,
                defaults={
                    'phone_number': self.cleaned_data['phone_number'],
                    'address': self.cleaned_data['address'],
                    'birth_date': self.cleaned_data['birth_date'],
                    'passport_number': self.cleaned_data['passport_number']
                }
            )
        return user

class UserProfileForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    birth_date = forms.DateField(required=True, widget=forms.DateInput(attrs={'type': 'date'}))
    phone_number = forms.CharField(required=True)
    address = forms.CharField(required=True, widget=forms.Textarea(attrs={'rows': 3}))

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.id:
            try:
                self.fields['birth_date'].initial = self.instance.profile.birth_date
                self.fields['phone_number'].initial = self.instance.client.phone_number
                self.fields['address'].initial = self.instance.client.address
            except (Profile.DoesNotExist, Client.DoesNotExist):
                pass

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            # Обновляем профиль
            Profile.objects.update_or_create(
                user=user,
                defaults={'birth_date': self.cleaned_data['birth_date']}
            )
            # Обновляем данные клиента
            Client.objects.update_or_create(
                user=user,
                defaults={
                    'phone_number': self.cleaned_data['phone_number'],
                    'address': self.cleaned_data['address'],
                    'birth_date': self.cleaned_data['birth_date']
                }
            )
        return user

class OrderForm(forms.ModelForm):
    service = forms.ModelChoiceField(
        queryset=Service.objects.all(),
        label='Услуга',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    device_type = forms.CharField(
        max_length=100,
        label='Тип устройства',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    device_model = forms.CharField(
        max_length=100,
        label='Модель устройства',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    description = forms.CharField(
        label='Описание проблемы',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )
    parts = forms.ModelMultipleChoiceField(
        queryset=Part.objects.all(),
        label='Необходимые запчасти',
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'})
    )
    employee = forms.ModelChoiceField(
        queryset=Employee.objects.all(),
        label='Мастер',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    visit_date = forms.DateField(
        label='Дата визита',
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        help_text='Укажите желаемую дату визита в сервисный центр'
    )

    class Meta:
        model = Order
        fields = ['service', 'device_type', 'device_model', 'description', 'parts', 'employee', 'visit_date']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Фильтруем сотрудников по специализации выбранной услуги
        if 'service' in self.data:
            try:
                service_id = int(self.data.get('service'))
                service = Service.objects.get(id=service_id)
                self.fields['employee'].queryset = Employee.objects.filter(
                    specializations__service_types=service.service_type
                )
            except (ValueError, Service.DoesNotExist):
                pass 

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'text'] 