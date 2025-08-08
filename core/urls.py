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
    
    # Pricing Module APIs
    path('api/market-prices/', api_views.MarketPriceListView.as_view(), name='market-prices'),
    path('api/market-prices/latest/', api_views.get_latest_market_prices, name='latest-market-prices'),
]
