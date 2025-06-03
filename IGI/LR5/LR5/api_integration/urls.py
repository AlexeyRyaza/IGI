from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    # Fun page URL
    path('fun/', views.fun_page, name='fun_page'),
    
    # Service URLs
    path('services/', views.ServiceListView.as_view(), name='service-list'),
    path('services/<int:pk>/', views.ServiceDetailView.as_view(), name='service-detail'),
    
    # Order URLs
    path('orders/', views.OrderListView.as_view(), name='order-list'),
    path('orders/<int:pk>/', views.OrderDetailView.as_view(), name='order-detail'),
    path('orders/create/', views.OrderCreateView.as_view(), name='order-create'),
    
    # Device URLs
    path('devices/', views.DeviceListView.as_view(), name='device-list'),
    path('devices/<int:pk>/', views.DeviceDetailView.as_view(), name='device-detail'),
] 