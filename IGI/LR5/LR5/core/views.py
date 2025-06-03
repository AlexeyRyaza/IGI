from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q, Sum, F
from decimal import Decimal
from .forms import CustomUserCreationForm, OrderForm, UserProfileForm, ReviewForm
from .models import (
    Service, ServiceType, Order, OrderService, Device, DeviceType, OrderPart, Employee,
    Article, CompanyInfo, FAQ, ContactEmployee, Vacancy, Review, Promo, Client
)
from django.views.generic import ListView, TemplateView, DetailView
from django.utils import timezone
from .statistics import get_client_age_stats, get_service_stats, get_monthly_orders_chart

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация успешно завершена!')
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, 'Вы успешно вошли в систему!')
            return redirect('home')
        else:
            messages.error(request, 'Неверное имя пользователя или пароль.')
    
    return render(request, 'registration/login.html')

@login_required
def custom_logout(request):
    logout(request)
    messages.success(request, 'Вы успешно вышли из системы!')
    return redirect('home')

def services_list(request):
    services = Service.objects.all().select_related('service_type')
    service_types = ServiceType.objects.all()
    
    # Фильтр по типу услуги
    service_type_id = request.GET.get('service_type')
    if service_type_id:
        services = services.filter(service_type_id=service_type_id)
    
    # Фильтр по цене
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    
    if min_price:
        try:
            min_price = Decimal(min_price)
            services = services.filter(price__gte=min_price)
        except:
            pass
            
    if max_price:
        try:
            max_price = Decimal(max_price)
            services = services.filter(price__lte=max_price)
        except:
            pass
    
    # Поиск по названию или описанию
    search_query = request.GET.get('search')
    if search_query:
        services = services.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    context = {
        'services': services,
        'service_types': service_types,
        'current_type': service_type_id,
        'min_price': min_price,
        'max_price': max_price,
        'search_query': search_query,
    }
    return render(request, 'services.html', context)

@login_required
def create_order(request, service_id):
    service = Service.objects.get(pk=service_id)
    
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.client = request.user.client
            order.status = 'pending'
            
            # Получаем или создаем тип устройства
            device_type, _ = DeviceType.objects.get_or_create(
                name=form.cleaned_data['device_type'],
                defaults={'description': f'Тип устройства: {form.cleaned_data["device_type"]}'}
            )
            
            # Создаем или получаем устройство
            device, _ = Device.objects.get_or_create(
                device_type=device_type,
                model=form.cleaned_data['device_model'],
                defaults={
                    'brand': 'Не указано',
                    'serial_number': f'SN-{request.user.username}-{form.cleaned_data["device_model"]}',
                    'description': form.cleaned_data.get('description', '')
                }
            )
            
            order.device = device
            order.visit_date = form.cleaned_data['visit_date']
            order.save()
            
            # Создаем связь заказа с услугой
            OrderService.objects.create(
                order=order,
                service=service,
                price_at_time=service.price,
                quantity=1
            )
            
            # Добавляем выбранные запчасти
            for part in form.cleaned_data['parts']:
                OrderPart.objects.create(
                    order=order,
                    part=part,
                    price_at_time=part.price,
                    quantity=1
                )
            
            # Обновляем общую стоимость заказа
            order.total_cost = order.calculate_total_cost()
            order.save()
            
            messages.success(request, 'Заказ успешно создан!')
            return redirect('client_orders')
    else:
        form = OrderForm(initial={'service': service})
    
    return render(request, 'create_order.html', {
        'form': form,
        'service': service
    })

@login_required
def client_orders(request):
    if request.user.is_staff:
        messages.error(request, 'Администраторы не имеют доступа к заказам клиентов')
        return redirect('home')
        
    orders = Order.objects.filter(client=request.user.client).prefetch_related(
        'orderservice_set__service',
        'parts'
    ).select_related('employee')
    
    return render(request, 'client_orders.html', {'orders': orders})

@login_required
def employee_orders(request):
    try:
        employee = request.user.employee
    except Employee.DoesNotExist:
        messages.error(request, 'У вас нет прав для просмотра этой страницы')
        return redirect('home')
    
    # Получаем все заказы сотрудника
    orders = Order.objects.filter(employee=employee).select_related(
        'client__user',
        'device__device_type'
    ).prefetch_related(
        'orderservice_set__service',
        'orderpart_set__part'
    ).order_by('-created_at')
    
    # Подсчитываем общую сумму заработка
    total_earnings = sum(order.calculate_employee_earnings() for order in orders)
    
    context = {
        'orders': orders,
        'total_earnings': total_earnings,
        'employee': employee
    }
    return render(request, 'employee_orders.html', context)

class HomeView(ListView):
    template_name = 'info/home.html'
    context_object_name = 'latest_article'
    model = Article

    def get_queryset(self):
        return Article.objects.filter(is_published=True).order_by('-created_at').first()

class AboutView(TemplateView):
    template_name = 'info/about.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['company_info'] = CompanyInfo.objects.order_by('order').first()
        return context

class NewsListView(ListView):
    template_name = 'info/news.html'
    context_object_name = 'articles'
    model = Article
    paginate_by = 10

    def get_queryset(self):
        return Article.objects.filter(is_published=True).order_by('-created_at')

class FAQListView(ListView):
    template_name = 'info/faq.html'
    context_object_name = 'entries'
    model = FAQ
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['terms'] = FAQ.objects.filter(entry_type='term').order_by('order', 'title')
        context['questions'] = FAQ.objects.filter(entry_type='question').order_by('order', 'title')
        return context

class ContactsView(ListView):
    template_name = 'info/contacts.html'
    context_object_name = 'contacts'
    model = ContactEmployee
    ordering = ['order']

class PrivacyView(TemplateView):
    template_name = 'info/privacy.html'

class VacancyListView(ListView):
    template_name = 'info/vacancies.html'
    context_object_name = 'vacancies'
    model = Vacancy
    paginate_by = 10

    def get_queryset(self):
        return Vacancy.objects.filter(is_active=True).order_by('-created_at')

class ReviewListView(ListView):
    template_name = 'info/reviews.html'
    context_object_name = 'reviews'
    model = Review
    paginate_by = 10

    def get_queryset(self):
        return Review.objects.filter(is_published=True).order_by('-created_at')

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        rating = request.POST.get('rating')
        text = request.POST.get('text')
        
        if rating and text:
            Review.objects.create(
                user=request.user,
                rating=rating,
                text=text,
                is_published=False
            )
            messages.success(request, 'Спасибо за ваш отзыв! Он будет опубликован после проверки модератором.')
        
        return redirect('reviews')

class PromoListView(ListView):
    template_name = 'info/promos.html'
    model = Promo

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        context['active_promos'] = Promo.objects.filter(
            valid_from__lte=now,
            valid_to__gte=now,
            is_active=True
        ).order_by('valid_to')
        context['archived_promos'] = Promo.objects.filter(
            valid_to__lt=now
        ).order_by('-valid_to')
        return context

class ArticleDetailView(DetailView):
    model = Article
    template_name = 'info/article_detail.html'
    context_object_name = 'article'

    def get_queryset(self):
        return Article.objects.filter(is_published=True)

def home(request):
    return render(request, 'home.html')

def about(request):
    company_info = CompanyInfo.objects.first()
    return render(request, 'info/about.html', {'company_info': company_info})

def news(request):
    articles = Article.objects.filter(is_published=True).order_by('-created_at')
    return render(request, 'news/news_list.html', {'articles': articles})

def article_detail(request, article_id):
    article = get_object_or_404(Article, id=article_id, is_published=True)
    return render(request, 'news/article_detail.html', {'article': article})

def faq(request):
    faqs = FAQ.objects.all().order_by('order')
    return render(request, 'info/faq.html', {'faqs': faqs})

def contacts(request):
    contacts = ContactEmployee.objects.all().order_by('order')
    return render(request, 'info/contacts.html', {'contacts': contacts})

def privacy(request):
    return render(request, 'info/privacy.html')

def vacancies(request):
    vacancies = Vacancy.objects.filter(is_active=True).order_by('-created_at')
    return render(request, 'info/vacancies.html', {'vacancies': vacancies})

def reviews(request):
    reviews = Review.objects.filter(is_published=True).order_by('-created_at')
    return render(request, 'info/reviews.html', {'reviews': reviews})

@login_required
def add_review(request):
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.is_published = True  # Автоматически одобряем отзыв
            review.save()
            messages.success(request, 'Спасибо за ваш отзыв!')
            return redirect('reviews')
    else:
        form = ReviewForm()
    return render(request, 'info/add_review.html', {'form': form})

def promos(request):
    promos = Promo.objects.filter(is_active=True).order_by('-valid_from')
    return render(request, 'info/promos.html', {'promos': promos})

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлен!')
            return redirect('edit_profile')
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, 'profile/edit_profile.html', {'form': form})

@login_required
def delete_profile(request):
    if request.method == 'POST':
        user = request.user
        # Выход пользователя из системы
        logout(request)
        # Удаление пользователя
        user.delete()
        messages.success(request, 'Ваш аккаунт был успешно удален.')
        return redirect('home')
    return redirect('edit_profile')

def is_staff(user):
    return user.is_staff

@login_required
@user_passes_test(is_staff)
def statistics_page(request):
    # Получаем все заказы и клиентов с предварительной загрузкой связанных данных
    orders = Order.objects.all().prefetch_related(
        'orderservice_set__service'
    )
    clients = Client.objects.all().select_related('user')
    
    # Получаем статистику по возрасту клиентов
    age_stats = get_client_age_stats(clients)
    
    # Получаем статистику по услугам и графики
    popularity_chart, revenue_chart, revenue_stats = get_service_stats(orders)
    
    # Получаем график динамики заказов по месяцам
    monthly_chart = get_monthly_orders_chart(orders)
    
    # Получаем список клиентов в алфавитном порядке
    clients_list = clients.order_by('user__last_name', 'user__first_name')
    
    context = {
        'age_stats': age_stats,
        'revenue_stats': revenue_stats,
        'popularity_chart': popularity_chart,
        'revenue_chart': revenue_chart,
        'monthly_chart': monthly_chart,
        'clients_list': clients_list,
    }
    
    return render(request, 'core/statistics.html', context)
