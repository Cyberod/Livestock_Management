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
    LivestockSimpleSerializer, SymptomAnalysisInputSerializer, DiseaseResultSerializer,
    SymptomAnalysisResponseSerializer, HealthRecordCreateSerializer, 
    PreventionRecommendationSerializer, SymptomSuggestionSerializer,
    PriceAnalysisInputSerializer, PriceAnalysisResultSerializer, 
    ProfitabilityResultSerializer, SellingRecommendationSerializer
)
from .services import FeedingRecommendationService, AnimalInput, DiseaseMonitoringService, SymptomInput
from .pricing_service import PricingAnalysisService, PriceAnalysisInput


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


# Disease Monitoring API Views

@swagger_auto_schema(
    method='post',
    operation_description="Analyze symptoms and get possible disease diagnoses",
    request_body=SymptomAnalysisInputSerializer,
    responses={
        200: SymptomAnalysisResponseSerializer,
        400: "Bad Request - Invalid input parameters"
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def analyze_symptoms(request):
    """
    Analyze symptoms and return possible diseases with confidence scores
    """
    serializer = SymptomAnalysisInputSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # Create symptom input object
    symptom_input = SymptomInput(
        animal_type_id=serializer.validated_data['animal_type_id'],
        symptoms=serializer.validated_data['symptoms'],
        livestock_id=serializer.validated_data.get('livestock_id')
    )
    
    # Analyze symptoms using the service
    service = DiseaseMonitoringService()
    disease_results = service.analyze_symptoms(symptom_input)
    critical_alerts = service.get_critical_alerts(symptom_input)
    
    # Get animal and symptom info
    animal_type = get_object_or_404(AnimalType, id=symptom_input.animal_type_id)
    input_symptoms = Symptom.objects.filter(id__in=symptom_input.symptoms)
    
    # Prepare response data
    response_data = {
        'animal_info': {
            'animal_type': animal_type.name,
            'animal_type_id': animal_type.id,
            'livestock_id': symptom_input.livestock_id
        },
        'input_symptoms': SymptomSerializer(input_symptoms, many=True).data,
        'disease_results': DiseaseResultSerializer(disease_results, many=True).data,
        'critical_alerts': DiseaseResultSerializer(critical_alerts, many=True).data,
        'total_diseases_found': len(disease_results),
        'highest_confidence': disease_results[0].confidence_score if disease_results else 0.0,
        'has_critical_alerts': len(critical_alerts) > 0
    }
    
    return Response(response_data, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='get',
    operation_description="Get critical disease alerts for specific symptoms",
    manual_parameters=[
        openapi.Parameter('animal_type_id', openapi.IN_QUERY, description="Animal type ID", type=openapi.TYPE_INTEGER, required=True),
        openapi.Parameter('symptoms', openapi.IN_QUERY, description="Comma-separated symptom IDs", type=openapi.TYPE_STRING, required=True),
    ],
    responses={200: DiseaseResultSerializer(many=True)}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_critical_alerts(request):
    """
    Get critical disease alerts that require immediate attention
    """
    animal_type_id = request.query_params.get('animal_type_id')
    symptoms_str = request.query_params.get('symptoms', '')
    
    if not animal_type_id or not symptoms_str:
        return Response(
            {'error': 'animal_type_id and symptoms parameters are required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        animal_type_id = int(animal_type_id)
        symptom_ids = [int(s.strip()) for s in symptoms_str.split(',') if s.strip()]
    except ValueError:
        return Response(
            {'error': 'Invalid parameter format'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Create symptom input and get critical alerts
    symptom_input = SymptomInput(animal_type_id=animal_type_id, symptoms=symptom_ids)
    service = DiseaseMonitoringService()
    critical_alerts = service.get_critical_alerts(symptom_input)
    
    serializer = DiseaseResultSerializer(critical_alerts, many=True)
    
    return Response({
        'critical_alerts': serializer.data,
        'count': len(critical_alerts),
        'requires_immediate_attention': len(critical_alerts) > 0
    }, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='get',
    operation_description="Get prevention recommendations for an animal type",
    manual_parameters=[
        openapi.Parameter('animal_type_id', openapi.IN_QUERY, description="Animal type ID", type=openapi.TYPE_INTEGER, required=True),
    ],
    responses={200: PreventionRecommendationSerializer}
)
@api_view(['GET'])
@permission_classes([AllowAny])
def get_prevention_recommendations(request):
    """
    Get prevention recommendations for a specific animal type
    """
    animal_type_id = request.query_params.get('animal_type_id')
    
    if not animal_type_id:
        return Response(
            {'error': 'animal_type_id parameter is required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        animal_type_id = int(animal_type_id)
    except ValueError:
        return Response(
            {'error': 'Invalid animal_type_id format'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    service = DiseaseMonitoringService()
    recommendations = service.get_prevention_recommendations(animal_type_id)
    
    if 'error' in recommendations:
        return Response(recommendations, status=status.HTTP_404_NOT_FOUND)
    
    serializer = PreventionRecommendationSerializer(recommendations)
    return Response(serializer.data, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='get',
    operation_description="Get symptom suggestions for an animal type",
    manual_parameters=[
        openapi.Parameter('animal_type_id', openapi.IN_QUERY, description="Animal type ID", type=openapi.TYPE_INTEGER, required=True),
    ],
    responses={200: SymptomSuggestionSerializer(many=True)}
)
@api_view(['GET'])
@permission_classes([AllowAny])
def get_symptom_suggestions(request):
    """
    Get symptom suggestions based on animal type
    """
    animal_type_id = request.query_params.get('animal_type_id')
    
    if not animal_type_id:
        return Response(
            {'error': 'animal_type_id parameter is required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        animal_type_id = int(animal_type_id)
    except ValueError:
        return Response(
            {'error': 'Invalid animal_type_id format'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    service = DiseaseMonitoringService()
    suggestions = service.get_symptom_suggestions(animal_type_id)
    
    serializer = SymptomSuggestionSerializer(suggestions, many=True)
    
    return Response({
        'suggestions': serializer.data,
        'count': len(suggestions)
    }, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='post',
    operation_description="Create a health record for livestock based on symptoms",
    request_body=HealthRecordCreateSerializer,
    responses={
        201: openapi.Response(
            description="Health record created successfully",
            examples={
                "application/json": {
                    "health_record_id": 1,
                    "livestock": "TAG001",
                    "symptoms_count": 3,
                    "suspected_disease": "Mastitis",
                    "requires_vet_attention": True
                }
            }
        ),
        400: "Bad Request - Invalid input parameters"
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_health_record(request):
    """
    Create a health record for livestock based on observed symptoms
    """
    serializer = HealthRecordCreateSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # Verify livestock belongs to user
    livestock = get_object_or_404(
        Livestock, 
        id=serializer.validated_data['livestock_id'],
        farmer=request.user
    )
    
    # Create health record using service
    service = DiseaseMonitoringService()
    result = service.create_health_record(
        livestock_id=serializer.validated_data['livestock_id'],
        symptom_ids=serializer.validated_data['symptom_ids'],
        suspected_disease_id=serializer.validated_data.get('suspected_disease_id')
    )
    
    if 'error' in result:
        return Response(result, status=status.HTTP_400_BAD_REQUEST)
    
    return Response(result, status=status.HTTP_201_CREATED)


# ======================= PRICING MODULE API VIEWS =======================

@swagger_auto_schema(
    method='post',
    operation_description="Analyze market prices and trends for livestock",
    request_body=PriceAnalysisInputSerializer,
    responses={
        200: openapi.Response(
            description="Market price analysis results",
            schema=PriceAnalysisResultSerializer
        ),
        400: "Bad Request - Invalid input parameters"
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def analyze_market_price(request):
    """
    Analyze market prices and trends for specific livestock types
    """
    serializer = PriceAnalysisInputSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # Use pricing service to analyze market
    from .pricing_service import PricingAnalysisService, PriceAnalysisInput
    
    price_input = PriceAnalysisInput(
        animal_type_id=serializer.validated_data['animal_type_id'],
        breed_id=serializer.validated_data.get('breed_id'),
        location=serializer.validated_data.get('location', ''),
        weight_kg=serializer.validated_data.get('weight_kg'),
        quality_grade=serializer.validated_data.get('quality_grade', 'AVERAGE')
    )
    
    service = PricingAnalysisService()
    result = service.analyze_market_price(price_input)
    
    # Serialize the result
    result_serializer = PriceAnalysisResultSerializer(result)
    
    return Response(result_serializer.data, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='get',
    operation_description="Analyze profitability of a specific livestock animal",
    manual_parameters=[
        openapi.Parameter(
            'livestock_id',
            openapi.IN_PATH,
            description="ID of the livestock to analyze",
            type=openapi.TYPE_INTEGER,
            required=True
        )
    ],
    responses={
        200: openapi.Response(
            description="Profitability analysis results",
            schema=ProfitabilityResultSerializer
        ),
        404: "Livestock not found",
        403: "Not authorized to access this livestock"
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def analyze_livestock_profitability(request, livestock_id):
    """
    Analyze profitability of a specific livestock animal
    """
    # Verify livestock belongs to user
    livestock = get_object_or_404(
        Livestock, 
        id=livestock_id,
        farmer=request.user
    )
    
    # Use pricing service to analyze profitability
    from .pricing_service import PricingAnalysisService
    
    service = PricingAnalysisService()
    result = service.analyze_livestock_profitability(livestock_id)
    
    if result is None:
        return Response(
            {'error': 'Unable to analyze profitability for this livestock'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Serialize the result
    result_serializer = ProfitabilityResultSerializer(result)
    
    return Response(result_serializer.data, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='get',
    operation_description="Get selling recommendations for all farmer's livestock",
    responses={
        200: openapi.Response(
            description="Selling recommendations for livestock",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'recommendations': openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(type=openapi.TYPE_OBJECT)
                    ),
                    'total_livestock': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'high_priority_count': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'total_potential_profit': openapi.Schema(type=openapi.TYPE_NUMBER)
                }
            )
        )
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_selling_recommendations(request):
    """
    Get selling recommendations for all farmer's livestock
    """
    from .pricing_service import PricingAnalysisService
    
    service = PricingAnalysisService()
    recommendations = service.get_selling_recommendations(request.user.id)
    
    # Calculate summary statistics
    high_priority_count = sum(1 for rec in recommendations if rec['action_priority'] >= 4)
    total_potential_profit = sum(rec['profitability'].estimated_profit for rec in recommendations)
    
    # Serialize recommendations
    recommendations_serializer = SellingRecommendationSerializer(recommendations, many=True)
    
    response_data = {
        'recommendations': recommendations_serializer.data,
        'total_livestock': len(recommendations),
        'high_priority_count': high_priority_count,
        'total_potential_profit': round(total_potential_profit, 2)
    }
    
    return Response(response_data, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='get',
    operation_description="Get recent market prices for livestock",
    manual_parameters=[
        openapi.Parameter(
            'animal_type_id',
            openapi.IN_QUERY,
            description="Filter by animal type ID",
            type=openapi.TYPE_INTEGER
        ),
        openapi.Parameter(
            'location',
            openapi.IN_QUERY,
            description="Filter by location",
            type=openapi.TYPE_STRING
        ),
        openapi.Parameter(
            'days',
            openapi.IN_QUERY,
            description="Number of days back to fetch (default: 30)",
            type=openapi.TYPE_INTEGER,
            default=30
        )
    ],
    responses={
        200: openapi.Response(
            description="Recent market prices",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'prices': openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(type=openapi.TYPE_OBJECT)
                    ),
                    'count': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'average_price': openapi.Schema(type=openapi.TYPE_NUMBER),
                    'date_range': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'from': openapi.Schema(type=openapi.TYPE_STRING),
                            'to': openapi.Schema(type=openapi.TYPE_STRING)
                        }
                    )
                }
            )
        )
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_market_prices(request):
    """
    Get recent market prices for livestock
    """
    from datetime import date, timedelta
    from .models import MarketPrice
    
    # Get query parameters
    animal_type_id = request.GET.get('animal_type_id')
    location = request.GET.get('location')
    days = int(request.GET.get('days', 30))
    
    # Filter prices
    queryset = MarketPrice.objects.all()
    
    if animal_type_id:
        queryset = queryset.filter(animal_type_id=animal_type_id)
    
    if location:
        queryset = queryset.filter(location__icontains=location)
    
    # Filter by date range
    start_date = date.today() - timedelta(days=days)
    queryset = queryset.filter(date_recorded__gte=start_date).order_by('-date_recorded')
    
    # Serialize results
    prices_serializer = MarketPriceSerializer(queryset, many=True)
    
    # Calculate statistics
    prices = queryset.values_list('price_per_kg', flat=True)
    average_price = sum(prices) / len(prices) if prices else 0
    
    response_data = {
        'prices': prices_serializer.data,
        'count': queryset.count(),
        'average_price': round(average_price, 2),
        'date_range': {
            'from': start_date.strftime('%Y-%m-%d'),
            'to': date.today().strftime('%Y-%m-%d')
        }
    }
    
    return Response(response_data, status=status.HTTP_200_OK)
