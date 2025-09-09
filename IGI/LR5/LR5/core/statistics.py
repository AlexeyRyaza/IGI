from django.db.models import Avg, Count, Sum
from django.db.models.functions import ExtractMonth, TruncDate
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.utils
from datetime import datetime, timedelta
import json
import numpy as np

def convert_to_native_types(obj):
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    return obj

def get_client_age_stats(clients):
    ages = [(datetime.now().date() - client.birth_date).days // 365 for client in clients]
    if not ages:
        return None
    
    df = pd.DataFrame(ages, columns=['age'])
    stats = {
        'mean': convert_to_native_types(round(df['age'].mean(), 1)),
        'median': convert_to_native_types(df['age'].median()),
        'min': convert_to_native_types(df['age'].min()),
        'max': convert_to_native_types(df['age'].max())
    }
    return stats

def get_service_stats(orders):
    # Получаем статистику через OrderService
    service_data = orders.values(
        'orderservice__service__name'
    ).annotate(
        total_revenue=Sum('orderservice__price_at_time'),
        count=Count('orderservice__service')
    ).filter(
        orderservice__service__name__isnull=False
    ).order_by('-total_revenue')
    
    if not service_data:
        return None, None, None
    
    # Создаем DataFrame и переименовываем колонку для совместимости
    df_popularity = pd.DataFrame(service_data)
    df_popularity = df_popularity.rename(columns={'orderservice__service__name': 'service_name'})
    
    # Создаем график популярности услуг
    fig_popularity = px.bar(
        df_popularity,
        x='service_name',
        y='count',
        title='Популярность услуг',
        labels={'service_name': 'Услуга', 'count': 'Количество заказов'}
    )
    
    # Создаем график выручки по услугам
    fig_revenue = px.bar(
        df_popularity,
        x='service_name',
        y='total_revenue',
        title='Выручка по услугам',
        labels={'service_name': 'Услуга', 'total_revenue': 'Выручка (руб.)'}
    )
    
    # Статистика по выручке
    revenue_stats = {
        'total': convert_to_native_types(df_popularity['total_revenue'].sum()),
        'mean': convert_to_native_types(round(df_popularity['total_revenue'].mean(), 2)),
        'median': convert_to_native_types(df_popularity['total_revenue'].median()),
    }
    
    # Обработка моды отдельно, так как она может быть пустой
    mode_series = df_popularity['total_revenue'].mode()
    revenue_stats['mode'] = convert_to_native_types(mode_series.iloc[0]) if not mode_series.empty else None
    
    return (
        fig_popularity.to_json(),
        fig_revenue.to_json(),
        revenue_stats
    )

def get_monthly_orders_chart(orders):
    # Получаем статистику по дням
    daily_orders = orders.annotate(
        date=TruncDate('created_at')
    ).values('date').annotate(
        count=Count('id'),
        revenue=Sum('total_cost')
    ).order_by('date')
    
    if not daily_orders:
        return None
    
    # Преобразуем QuerySet в список словарей и форматируем даты
    data_list = []
    for order in daily_orders:
        data_list.append({
            'date': order['date'].strftime('%d/%m/%Y'),
            'count': order['count'],
            'revenue': float(order['revenue']) if order['revenue'] else 0
        })
    
    df = pd.DataFrame(data_list)
    
    # Создаем график динамики заказов по дням
    fig = go.Figure()
    
    # Добавляем линию для количества заказов
    fig.add_trace(go.Scatter(
        x=df['date'].tolist(),
        y=df['count'].tolist(),
        name='Количество заказов',
        yaxis='y',
        mode='lines+markers'  # Добавляем точки на линии для лучшей визуализации
    ))
    
    # Добавляем линию для выручки
    fig.add_trace(go.Scatter(
        x=df['date'].tolist(),
        y=df['revenue'].tolist(),
        name='Выручка',
        yaxis='y2',
        mode='lines+markers'  # Добавляем точки на линии для лучшей визуализации
    ))
    
    # Настраиваем макет с двумя осями Y
    fig.update_layout(
        title='Динамика заказов и выручки по дням',
        xaxis=dict(
            title='Дата',
            tickangle=45,  # Наклоняем подписи дат для лучшей читаемости
            tickmode='array',
            ticktext=df['date'].tolist(),
            tickvals=list(range(len(df))),
        ),
        yaxis=dict(
            title='Количество заказов',
            side='left',
            gridcolor='lightgray'
        ),
        yaxis2=dict(
            title='Выручка (руб.)',
            side='right',
            overlaying='y',
            gridcolor='lightgray'
        ),
        hovermode='x unified',
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(b=100),  # Увеличиваем нижний отступ для подписей дат
    )
    
    return fig.to_json() 