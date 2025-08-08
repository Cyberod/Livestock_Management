from django.urls import path
from . import api_views, views

app_name = 'core'

urlpatterns = [
    # Frontend Views
    path('feeding/', views.feeding_guide, name='feeding-guide'),
    path('disease/', views.disease_monitor, name='disease-monitor'),
    path('pricing/', views.pricing_guide, name='pricing-guide'),
    
    # Feeding Module APIs
    path('api/feeding/recommendations/', api_views.get_feeding_recommendations, name='feeding-recommendations'),
    path('api/feeding/livestock/<int:livestock_id>/summary/', api_views.get_livestock_feeding_summary, name='livestock-feeding-summary'),
    
    # Reference/Lookup APIs
    path('api/animal-types/', api_views.AnimalTypeListView.as_view(), name='animal-types'),
    path('api/breeds/', api_views.BreedListView.as_view(), name='breeds'),
    path('api/feed-types/', api_views.FeedTypeListView.as_view(), name='feed-types'),
    path('api/user/livestock/', api_views.UserLivestockListView.as_view(), name='user-livestock'),
    
    # Disease Module APIs
    path('api/diseases/', api_views.DiseaseListView.as_view(), name='diseases'),
    path('api/symptoms/', api_views.SymptomListView.as_view(), name='symptoms'),
    path('api/disease/analyze-symptoms/', api_views.analyze_symptoms, name='analyze-symptoms'),
    path('api/disease/critical-alerts/', api_views.get_critical_alerts, name='critical-alerts'),
    path('api/disease/prevention/', api_views.get_prevention_recommendations, name='prevention-recommendations'),
    path('api/disease/symptom-suggestions/', api_views.get_symptom_suggestions, name='symptom-suggestions'),
    path('api/disease/health-record/', api_views.create_health_record, name='create-health-record'),
    
    # Pricing Module APIs
    path('api/pricing/analyze-market/', api_views.analyze_market_price, name='analyze-market-price'),
    path('api/pricing/livestock/<int:livestock_id>/profitability/', api_views.analyze_livestock_profitability, name='analyze-livestock-profitability'),
    path('api/pricing/selling-recommendations/', api_views.get_selling_recommendations, name='selling-recommendations'),
    path('api/pricing/market-prices/', api_views.get_market_prices, name='get-market-prices'),
]
