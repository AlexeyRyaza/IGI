from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.custom_logout, name='logout'),
    
    # Сервисные страницы
    path('services/', views.services_list, name='services'),
    path('orders/create/<int:service_id>/', views.create_order, name='create_order'),
    path('orders/client/', views.client_orders, name='client_orders'),
    path('orders/employee/', views.employee_orders, name='employee_orders'),
    path('statistics/', views.statistics_page, name='statistics'),
    
    # Информационные страницы
    path('about/', views.AboutView.as_view(), name='about'),
    path('news/', views.NewsListView.as_view(), name='news'),
    path('news/<int:pk>/', views.ArticleDetailView.as_view(), name='article_detail'),
    path('faq/', views.FAQListView.as_view(), name='faq'),
    path('contacts/', views.ContactsView.as_view(), name='contacts'),
    path('privacy/', views.PrivacyView.as_view(), name='privacy'),
    path('vacancies/', views.VacancyListView.as_view(), name='vacancies'),
    path('reviews/', views.ReviewListView.as_view(), name='reviews'),
    path('promos/', views.PromoListView.as_view(), name='promos'),
    
    # Профиль пользователя
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/delete/', views.delete_profile, name='delete_profile'),
] 