from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, Avg
from django.core.serializers.json import DjangoJSONEncoder
from .models import Livestock, HealthRecord, AnimalType, MarketPrice
from datetime import date, timedelta
import json


@login_required
def feeding_guide(request):
    """
    Display the feeding guide interface
    """
    context = {
        'page_title': 'Feeding Guide',
        'page_description': 'Get personalized feeding recommendations for your livestock'
    }
    return render(request, 'feeding/feeding_guide.html', context)


@login_required
def disease_monitor(request):
    """
    Display the disease monitoring interface (for future sprint)
    """
    context = {
        'page_title': 'Disease Monitor',
        'page_description': 'Monitor symptoms and track animal health'
    }
    return render(request, 'disease/disease_monitor.html', context)


@login_required
def pricing_guide(request):
    """
    Display the pricing guide interface (for future sprint)
    """
    context = {
        'page_title': 'Pricing Guide',
        'page_description': 'Get market pricing estimates and selling advice'
    }
    return render(request, 'pricing/pricing_guide.html', context)


def dashboard(request):
    """
    Enhanced dashboard view with integrated data from all modules
    """
    context = {
        'page_title': 'Dashboard - Livestock Management System',
    }
    
    if request.user.is_authenticated:
        # Get user's livestock data
        livestock_data = get_livestock_summary(request.user)
        health_data = get_health_summary(request.user)
        market_data = get_market_summary()
        
        context.update({
            'livestock_data': livestock_data,
            'health_data': health_data,
            'market_data': market_data,
            'livestock_data_json': json.dumps(livestock_data, cls=DjangoJSONEncoder),
        })
    
    return render(request, 'dashboard.html', context)


def get_livestock_summary(user):
    """Get comprehensive livestock summary for dashboard"""
    livestock = Livestock.objects.filter(farmer=user)
    
    # Basic counts by animal type
    animal_counts = livestock.values('animal_type__name').annotate(
        count=Count('id')
    ).order_by('animal_type__name')
    
    # Status distribution
    status_counts = livestock.values('status').annotate(
        count=Count('id')
    ).order_by('status')
    
    # Purpose distribution
    purpose_counts = livestock.values('purpose').annotate(
        count=Count('id')
    ).order_by('purpose')
    
    # Age distribution (young, adult, mature)
    today = date.today()
    young_count = 0
    adult_count = 0
    mature_count = 0
    
    for animal in livestock:
        if animal.age_months:
            if animal.age_months < 6:
                young_count += 1
            elif animal.age_months < 24:
                adult_count += 1
            else:
                mature_count += 1
    
    # Financial summary
    total_investment = livestock.aggregate(
        total=Sum('purchase_price')
    )['total'] or 0
    
    # Convert to float for calculations
    total_investment = float(total_investment)
    
    # Estimated current value (simplified calculation)
    estimated_value = 0.0
    for animal in livestock:
        if animal.current_weight_kg:
            base_price = 8.0  # Default price per kg
            estimated_value += float(animal.current_weight_kg) * base_price
    
    return {
        'total_count': livestock.count(),
        'animal_counts': list(animal_counts),
        'status_counts': list(status_counts),
        'purpose_counts': list(purpose_counts),
        'age_distribution': {
            'young': young_count,
            'adult': adult_count,
            'mature': mature_count
        },
        'financial': {
            'total_investment': round(total_investment, 2),
            'estimated_value': round(estimated_value, 2),
            'estimated_profit': round(estimated_value - total_investment, 2)
        }
    }


def get_health_summary(user):
    """Get health summary for dashboard"""
    livestock = Livestock.objects.filter(farmer=user)
    
    # Recent health records
    recent_records = HealthRecord.objects.filter(
        livestock__farmer=user,
        date_recorded__gte=date.today() - timedelta(days=30)
    ).order_by('-date_recorded')[:5]
    
    # Health status overview
    healthy_count = livestock.filter(status='HEALTHY').count()
    sick_count = livestock.filter(status='SICK').count()
    quarantine_count = livestock.filter(status='QUARANTINE').count()
    
    # Critical alerts (animals needing attention)
    critical_alerts = []
    for animal in livestock:
        if animal.status in ['SICK', 'QUARANTINE']:
            critical_alerts.append({
                'animal': animal,
                'issue': animal.get_status_display(),
                'priority': 'HIGH' if animal.status == 'QUARANTINE' else 'MEDIUM'
            })
    
    return {
        'recent_records': recent_records,
        'health_overview': {
            'healthy': healthy_count,
            'sick': sick_count,
            'quarantine': quarantine_count,
            'total': livestock.count()
        },
        'critical_alerts': critical_alerts[:3],  # Top 3 alerts
        'health_percentage': round((healthy_count / livestock.count() * 100) if livestock.count() > 0 else 100, 1)
    }


def get_market_summary():
    """Get market summary for dashboard"""
    # Get recent market prices
    recent_prices = MarketPrice.objects.filter(
        date_recorded__gte=date.today() - timedelta(days=7)
    ).order_by('-date_recorded')
    
    # Average prices by animal type
    price_averages = []
    for animal_type in AnimalType.objects.all():
        avg_price = recent_prices.filter(animal_type=animal_type).aggregate(
            avg=Avg('price_per_kg')
        )['avg']
        
        if avg_price:
            price_averages.append({
                'animal_type': animal_type.name,
                'avg_price': round(avg_price, 2)
            })
    
    # Market trends (simplified)
    market_trends = []
    for animal_type in AnimalType.objects.all():
        current_week = recent_prices.filter(
            animal_type=animal_type,
            date_recorded__gte=date.today() - timedelta(days=7)
        ).aggregate(avg=Avg('price_per_kg'))['avg']
        
        previous_week = MarketPrice.objects.filter(
            animal_type=animal_type,
            date_recorded__gte=date.today() - timedelta(days=14),
            date_recorded__lt=date.today() - timedelta(days=7)
        ).aggregate(avg=Avg('price_per_kg'))['avg']
        
        trend = 'STABLE'
        percentage = 0
        
        if current_week and previous_week:
            percentage = ((current_week - previous_week) / previous_week) * 100
            if percentage > 2:
                trend = 'RISING'
            elif percentage < -2:
                trend = 'FALLING'
        
        market_trends.append({
            'animal_type': animal_type.name,
            'trend': trend,
            'percentage': round(percentage, 1)
        })
    
    return {
        'price_averages': price_averages,
        'market_trends': market_trends,
        'last_updated': recent_prices.first().date_recorded if recent_prices.exists() else None
    }
