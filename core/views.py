from django.shortcuts import render
from django.contrib.auth.decorators import login_required


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
