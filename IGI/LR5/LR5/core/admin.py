from django.contrib import admin
from .models import (
    ServiceType, Service,
    DeviceType, Device,
    PartType, Part,
    Specialization, Employee,
    Client, Order,
    OrderService, OrderPart,
    Profile, Article, CompanyInfo,
    FAQ, ContactEmployee,
    Vacancy, Review,
    Promo
)

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'is_published')
    search_fields = ('title', 'content')
    list_filter = ('created_at', 'is_published')

@admin.register(CompanyInfo)
class CompanyInfoAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'year')

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('title', 'entry_type', 'order', 'created_at', 'updated_at')
    list_filter = ('entry_type',)
    search_fields = ('title', 'content')
    ordering = ('order', 'title')
    list_editable = ('order',)
    date_hierarchy = 'created_at'

@admin.register(ContactEmployee)
class ContactEmployeeAdmin(admin.ModelAdmin):
    list_display = ('name', 'position', 'email', 'phone', 'order')
    list_editable = ('order',)
    search_fields = ('name', 'position', 'email', 'phone')
    ordering = ('order',)

@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ('title', 'salary_range', 'created_at', 'is_active')
    search_fields = ('title', 'description', 'requirements')
    list_filter = ('created_at', 'is_active')

    def salary_range(self, obj):
        if obj.salary_from and obj.salary_to:
            return f"{obj.salary_from} - {obj.salary_to}"
        elif obj.salary_from:
            return f"от {obj.salary_from}"
        elif obj.salary_to:
            return f"до {obj.salary_to}"
        return "Не указана"
    salary_range.short_description = "Зарплата"

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'rating', 'created_at', 'is_published')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'text')
    list_filter = ('rating', 'created_at', 'is_published')

@admin.register(Promo)
class PromoAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount', 'valid_from', 'valid_to', 'is_active')
    search_fields = ('code', 'description')
    list_filter = ('is_active', 'valid_from', 'valid_to')

@admin.register(ServiceType)
class ServiceTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name', 'description')

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'service_type', 'price', 'duration')
    list_filter = ('service_type', 'created_at')
    search_fields = ('name', 'description')

@admin.register(DeviceType)
class DeviceTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name', 'description')

@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ('device_type', 'brand', 'model', 'serial_number')
    list_filter = ('device_type', 'brand')
    search_fields = ('brand', 'model', 'serial_number')

@admin.register(PartType)
class PartTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name', 'description')

@admin.register(Part)
class PartAdmin(admin.ModelAdmin):
    list_display = ('name', 'part_type', 'price', 'quantity_in_stock')
    list_filter = ('part_type', 'created_at')
    search_fields = ('name', 'description')

@admin.register(Specialization)
class SpecializationAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name', 'description')

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'birth_date', 'hire_date')
    list_filter = ('specializations', 'hire_date')
    search_fields = ('user__username', 'phone_number', 'passport_number')
    filter_horizontal = ('specializations',)

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'birth_date', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'phone_number', 'passport_number', 'address')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'employee', 'status', 'created_at', 'visit_date', 'total_cost')
    list_filter = ('status', 'created_at', 'visit_date')
    search_fields = ('client__user__username', 'employee__user__username', 'description')
    date_hierarchy = 'created_at'

@admin.register(OrderService)
class OrderServiceAdmin(admin.ModelAdmin):
    list_display = ('order', 'service', 'quantity', 'price_at_time')
    list_filter = ('service',)
    search_fields = ('order__id', 'service__name')

@admin.register(OrderPart)
class OrderPartAdmin(admin.ModelAdmin):
    list_display = ('order', 'part', 'quantity', 'price_at_time')
    list_filter = ('part',)
    search_fields = ('order__id', 'part__name')

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'birth_date')
    search_fields = ('user__username', 'user__email')
    list_filter = ('birth_date',) 