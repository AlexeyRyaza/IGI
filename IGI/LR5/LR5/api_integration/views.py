from django.shortcuts import render
from django.utils import timezone
import requests
from calendar import HTMLCalendar
from datetime import datetime
from .models import Joke, CatFact
from django.http import JsonResponse
from django.views import View
from django.views.generic import DetailView, ListView
from django.core.serializers import serialize
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from core.models import Service, Order, Device
import json

def fun_page(request):
    # Get current time in user's timezone
    current_time = timezone.localtime()
    
    # Create calendar
    cal = HTMLCalendar().formatmonth(current_time.year, current_time.month)
    
    # Fetch a random joke
    joke_response = requests.get('https://official-joke-api.appspot.com/random_joke')
    joke = None
    if joke_response.status_code == 200:
        joke_data = joke_response.json()
        joke = Joke.objects.create(
            setup=joke_data['setup'],
            punchline=joke_data['punchline'],
            type=joke_data['type']
        )

    # Fetch a cat fact
    cat_response = requests.get('https://catfact.ninja/fact')
    cat_fact = None
    if cat_response.status_code == 200:
        fact_data = cat_response.json()
        cat_fact = CatFact.objects.create(
            fact=fact_data['fact'],
            length=fact_data['length']
        )

    context = {
        'current_time_local': current_time.strftime('%d/%m/%Y %H:%M:%S'),
        'current_time_utc': timezone.now().strftime('%d/%m/%Y %H:%M:%S'),
        'calendar': cal,
        'joke': joke,
        'cat_fact': cat_fact,
        'timezone_name': current_time.tzname(),
    }
    
    return render(request, 'api_integration/fun_page.html', context)

class JSONResponseMixin:
    """Mixin to convert model data to JSON response"""
    def render_to_json_response(self, context, **response_kwargs):
        return JsonResponse(
            self.get_data(context),
            safe=False,
            **response_kwargs
        )

    def get_data(self, context):
        if isinstance(context, (list, tuple)):
            return json.loads(serialize('json', context))
        return json.loads(serialize('json', [context]))[0]

class ServiceListView(JSONResponseMixin, ListView):
    model = Service
    
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if 'search' in request.GET:
            search_query = request.GET['search']
            queryset = queryset.filter(name__icontains=search_query) | \
                      queryset.filter(description__icontains=search_query)
        return self.render_to_json_response(queryset)

class ServiceDetailView(JSONResponseMixin, DetailView):
    model = Service
    
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return self.render_to_json_response(self.object)

class OrderListView(LoginRequiredMixin, JSONResponseMixin, ListView):
    model = Order
    
    def get_queryset(self):
        return Order.objects.filter(client__user=self.request.user)
    
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        return self.render_to_json_response(queryset)

class OrderDetailView(LoginRequiredMixin, JSONResponseMixin, DetailView):
    model = Order
    
    def get_queryset(self):
        return Order.objects.filter(client__user=self.request.user)
    
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return self.render_to_json_response(self.object)

@method_decorator(csrf_exempt, name='dispatch')
class OrderCreateView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            order = Order.objects.create(
                client=request.user.client,
                device_id=data['device'],
                description=data.get('description', '')
            )
            
            # Add services
            if 'services' in data:
                for service_id in data['services']:
                    order.services.add(service_id)
            
            return JsonResponse({'id': order.id}, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

class DeviceListView(JSONResponseMixin, ListView):
    model = Device
    
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if 'search' in request.GET:
            search_query = request.GET['search']
            queryset = queryset.filter(brand__icontains=search_query) | \
                      queryset.filter(model__icontains=search_query) | \
                      queryset.filter(description__icontains=search_query)
        return self.render_to_json_response(queryset)

class DeviceDetailView(JSONResponseMixin, DetailView):
    model = Device
    
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return self.render_to_json_response(self.object)
