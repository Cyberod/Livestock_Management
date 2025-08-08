from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import (
    AnimalType, Breed, Livestock, FeedType, FeedingRecommendation,
    Disease, Symptom, MarketPrice
)
from .serializers import (
    AnimalTypeSerializer, BreedSerializer, LivestockSerializer, FeedTypeSerializer,
    FeedingRecommendationInputSerializer, FeedingResultSerializer, FeedingSummarySerializer,
    DiseaseSerializer, SymptomSerializer, MarketPriceSerializer,
    AnimalTypeSimpleSerializer, BreedSimpleSerializer, FeedTypeSimpleSerializer,
    LivestockSimpleSerializer
)
from .services import FeedingRecommendationService, AnimalInput


# Feeding Module API Views

@swagger_auto_schema(
    method='post',
    operation_description="Get feeding recommendations based on animal parameters",
    request_body=FeedingRecommendationInputSerializer,
    responses={
        200: openapi.Response(
            description="Feeding recommendations",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'recommendations': openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(type=openapi.TYPE_OBJECT)
                    ),
                    'animal_info': openapi.Schema(type=openapi.TYPE_OBJECT),
                    'input_parameters': openapi.Schema(type=openapi.TYPE_OBJECT)
                }
            )
        ),
        400: "Bad Request - Invalid input parameters"
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_feeding_recommendations(request):
    """
    Get feeding recommendations for an animal based on type, age, weight, and purpose
    """
    serializer = FeedingRecommendationInputSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # Create animal input object
    animal_input = AnimalInput(
        animal_type_id=serializer.validated_data['animal_type_id'],
        age_months=serializer.validated_data.get('age_months'),
        weight_kg=serializer.validated_data.get('weight_kg'),
        purpose=serializer.validated_data.get('purpose'),
        livestock_id=serializer.validated_data.get('livestock_id')
    )
    
    # Get recommendations using the service
    service = FeedingRecommendationService()
    recommendations = service.get_recommendations(animal_input)
    
    # Get animal type info
    animal_type = get_object_or_404(AnimalType, id=animal_input.animal_type_id)
    
    # Serialize results
    recommendation_data = FeedingResultSerializer(recommendations, many=True).data
    
    response_data = {
        'recommendations': recommendation_data,
        'animal_info': {
            'animal_type': animal_type.name,
            'age_months': animal_input.age_months,
            'weight_kg': animal_input.weight_kg,
            'purpose': animal_input.purpose
        },
        'input_parameters': serializer.validated_data,
        'total_recommendations': len(recommendations),
        'total_daily_cost': sum(rec.cost_per_day for rec in recommendations),
        'average_cost_per_kg': sum(rec.cost_per_day for rec in recommendations) / len(recommendations) if recommendations else 0
    }
    
    return Response(response_data, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='get',
    operation_description="Get feeding summary for a specific livestock animal",
    responses={
        200: FeedingSummarySerializer,
        404: "Livestock not found"
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_livestock_feeding_summary(request, livestock_id):
    """
    Get comprehensive feeding summary for a specific livestock animal
    """
    # Verify livestock exists and belongs to user
    livestock = get_object_or_404(Livestock, id=livestock_id, farmer=request.user)
    
    # Get feeding summary using service
    service = FeedingRecommendationService()
    summary_data = service.get_feeding_summary_for_livestock(livestock_id)
    
    if 'error' in summary_data:
        return Response({'error': summary_data['error']}, status=status.HTTP_404_NOT_FOUND)
    
    # Serialize the response
    serializer = FeedingSummarySerializer(summary_data)
    
    return Response(serializer.data, status=status.HTTP_200_OK)


# Lookup/Reference API Views

class AnimalTypeListView(generics.ListAPIView):
    """List all animal types (for dropdowns/selects)"""
    queryset = AnimalType.objects.all()
    serializer_class = AnimalTypeSimpleSerializer
    permission_classes = [AllowAny]


class BreedListView(generics.ListAPIView):
    """List breeds, optionally filtered by animal type"""
    serializer_class = BreedSimpleSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = Breed.objects.all().select_related('animal_type')
        animal_type_id = self.request.query_params.get('animal_type', None)
        
        if animal_type_id is not None:
            queryset = queryset.filter(animal_type_id=animal_type_id)
        
        return queryset


class FeedTypeListView(generics.ListAPIView):
    """List feed types, optionally filtered by animal type"""
    serializer_class = FeedTypeSimpleSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = FeedType.objects.all()
        animal_type_id = self.request.query_params.get('animal_type', None)
        
        if animal_type_id is not None:
            queryset = queryset.filter(suitable_for__id=animal_type_id)
        
        return queryset


class UserLivestockListView(generics.ListAPIView):
    """List livestock for the authenticated user"""
    serializer_class = LivestockSimpleSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Livestock.objects.filter(farmer=self.request.user).select_related('animal_type')


# Disease Module API Views (for future sprint)

class DiseaseListView(generics.ListAPIView):
    """List diseases, optionally filtered by animal type"""
    serializer_class = DiseaseSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = Disease.objects.all().prefetch_related('affected_animals', 'symptoms')
        animal_type_id = self.request.query_params.get('animal_type', None)
        
        if animal_type_id is not None:
            queryset = queryset.filter(affected_animals__id=animal_type_id)
        
        return queryset


class SymptomListView(generics.ListAPIView):
    """List all symptoms"""
    queryset = Symptom.objects.all()
    serializer_class = SymptomSerializer
    permission_classes = [AllowAny]


# Pricing Module API Views (for future sprint)

class MarketPriceListView(generics.ListAPIView):
    """List market prices, optionally filtered by animal type and location"""
    serializer_class = MarketPriceSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = MarketPrice.objects.all().select_related('animal_type', 'breed').order_by('-date_recorded')
        
        animal_type_id = self.request.query_params.get('animal_type', None)
        location = self.request.query_params.get('location', None)
        
        if animal_type_id is not None:
            queryset = queryset.filter(animal_type_id=animal_type_id)
        
        if location is not None:
            queryset = queryset.filter(location__icontains=location)
        
        return queryset[:50]  # Limit to recent 50 records


@swagger_auto_schema(
    method='get',
    operation_description="Get latest market prices for an animal type",
    manual_parameters=[
        openapi.Parameter('animal_type_id', openapi.IN_QUERY, description="Animal type ID", type=openapi.TYPE_INTEGER),
        openapi.Parameter('location', openapi.IN_QUERY, description="Market location", type=openapi.TYPE_STRING),
    ],
    responses={200: MarketPriceSerializer(many=True)}
)
@api_view(['GET'])
@permission_classes([AllowAny])
def get_latest_market_prices(request):
    """
    Get latest market prices, optionally filtered by animal type and location
    """
    animal_type_id = request.query_params.get('animal_type_id')
    location = request.query_params.get('location')
    
    queryset = MarketPrice.objects.all().select_related('animal_type', 'breed').order_by('-date_recorded')
    
    if animal_type_id:
        queryset = queryset.filter(animal_type_id=animal_type_id)
    
    if location:
        queryset = queryset.filter(location__icontains=location)
    
    # Get latest prices (last 30 days)
    from datetime import date, timedelta
    recent_date = date.today() - timedelta(days=30)
    queryset = queryset.filter(date_recorded__gte=recent_date)[:20]
    
    serializer = MarketPriceSerializer(queryset, many=True)
    
    return Response({
        'prices': serializer.data,
        'count': queryset.count(),
        'date_range': f"Last 30 days from {date.today()}"
    }, status=status.HTTP_200_OK)
