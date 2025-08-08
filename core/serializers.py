from rest_framework import serializers
from .models import (
    AnimalType, Breed, Livestock, FeedType, FeedingRecommendation,
    Disease, Symptom, HealthRecord, MarketPrice, FarmerProfile,
    PriceAlert, SaleRecord, CostRecord
)


class AnimalTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnimalType
        fields = ['id', 'name', 'description']


class BreedSerializer(serializers.ModelSerializer):
    animal_type = AnimalTypeSerializer(read_only=True)
    animal_type_name = serializers.CharField(source='animal_type.name', read_only=True)
    
    class Meta:
        model = Breed
        fields = ['id', 'name', 'animal_type', 'animal_type_name', 'description', 
                 'average_weight_kg', 'maturity_months']


class FeedTypeSerializer(serializers.ModelSerializer):
    suitable_for = AnimalTypeSerializer(many=True, read_only=True)
    
    class Meta:
        model = FeedType
        fields = ['id', 'name', 'category', 'description', 'protein_percentage',
                 'energy_mj_per_kg', 'cost_per_kg', 'suitable_for']


class LivestockSerializer(serializers.ModelSerializer):
    animal_type = AnimalTypeSerializer(read_only=True)
    breed = BreedSerializer(read_only=True)
    farmer_username = serializers.CharField(source='farmer.username', read_only=True)
    age_months = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Livestock
        fields = ['id', 'tag_number', 'name', 'animal_type', 'breed', 'gender',
                 'date_of_birth', 'current_weight_kg', 'purpose', 'status',
                 'farmer_username', 'age_months', 'notes']


class FeedingRecommendationInputSerializer(serializers.Serializer):
    """Serializer for feeding recommendation input data"""
    animal_type_id = serializers.IntegerField()
    age_months = serializers.IntegerField(required=False, allow_null=True, min_value=0)
    weight_kg = serializers.FloatField(required=False, allow_null=True, min_value=0)
    purpose = serializers.ChoiceField(
        choices=Livestock.PURPOSE_CHOICES,
        required=False,
        allow_blank=True
    )
    livestock_id = serializers.IntegerField(required=False, allow_null=True)
    
    def validate_animal_type_id(self, value):
        """Validate that animal type exists"""
        try:
            AnimalType.objects.get(id=value)
        except AnimalType.DoesNotExist:
            raise serializers.ValidationError("Animal type not found")
        return value
    
    def validate_livestock_id(self, value):
        """Validate that livestock exists if provided"""
        if value is not None:
            try:
                Livestock.objects.get(id=value)
            except Livestock.DoesNotExist:
                raise serializers.ValidationError("Livestock not found")
        return value


class FeedingResultSerializer(serializers.Serializer):
    """Serializer for feeding recommendation results"""
    feed_type = FeedTypeSerializer(read_only=True)
    daily_amount_kg = serializers.FloatField()
    feeding_frequency = serializers.IntegerField()
    cost_per_day = serializers.FloatField()
    notes = serializers.CharField()
    recommendation_source = serializers.CharField()


class FeedingSummarySerializer(serializers.Serializer):
    """Serializer for feeding summary response"""
    livestock = LivestockSerializer(read_only=True)
    recommendations = FeedingResultSerializer(many=True, read_only=True)
    total_daily_cost = serializers.FloatField()
    monthly_cost_estimate = serializers.FloatField()
    summary = serializers.DictField()


class FeedingRecommendationSerializer(serializers.ModelSerializer):
    """Serializer for database feeding recommendations"""
    animal_type = AnimalTypeSerializer(read_only=True)
    feed_type = FeedTypeSerializer(read_only=True)
    
    class Meta:
        model = FeedingRecommendation
        fields = ['id', 'animal_type', 'feed_type', 'min_age_months', 'max_age_months',
                 'min_weight_kg', 'max_weight_kg', 'purpose', 'daily_amount_kg',
                 'feeding_frequency', 'notes']


# Additional serializers for other modules (disease, pricing)

class SymptomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Symptom
        fields = ['id', 'name', 'description']


class DiseaseSerializer(serializers.ModelSerializer):
    affected_animals = AnimalTypeSerializer(many=True, read_only=True)
    symptoms = SymptomSerializer(many=True, read_only=True)
    
    class Meta:
        model = Disease
        fields = ['id', 'name', 'description', 'affected_animals', 'severity',
                 'is_contagious', 'prevention_measures', 'treatment_advice',
                 'vet_required', 'symptoms']


class HealthRecordSerializer(serializers.ModelSerializer):
    livestock = LivestockSerializer(read_only=True)
    symptoms = SymptomSerializer(many=True, read_only=True)
    suspected_disease = DiseaseSerializer(read_only=True)
    
    class Meta:
        model = HealthRecord
        fields = ['id', 'livestock', 'date_recorded', 'symptoms', 'suspected_disease',
                 'diagnosis', 'treatment_given', 'veterinarian_consulted',
                 'recovery_status', 'notes']


class MarketPriceSerializer(serializers.ModelSerializer):
    animal_type = AnimalTypeSerializer(read_only=True)
    breed = BreedSerializer(read_only=True)
    
    class Meta:
        model = MarketPrice
        fields = ['id', 'animal_type', 'breed', 'location', 'date_recorded',
                 'price_per_kg', 'min_weight_kg', 'max_weight_kg', 'quality_grade',
                 'source', 'notes']


class FarmerProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = FarmerProfile
        fields = ['id', 'username', 'email', 'phone_number', 'location',
                 'farm_size_acres', 'experience_years']


# Quick lookup serializers (minimal data for dropdowns/selects)
class AnimalTypeSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnimalType
        fields = ['id', 'name']


class BreedSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Breed
        fields = ['id', 'name', 'animal_type']


class FeedTypeSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedType
        fields = ['id', 'name', 'category', 'cost_per_kg']


class LivestockSimpleSerializer(serializers.ModelSerializer):
    animal_type_name = serializers.CharField(source='animal_type.name', read_only=True)
    
    class Meta:
        model = Livestock
        fields = ['id', 'tag_number', 'name', 'animal_type_name', 'current_weight_kg']


# Disease Monitoring Serializers

class SymptomAnalysisInputSerializer(serializers.Serializer):
    """Serializer for symptom analysis input"""
    animal_type_id = serializers.IntegerField()
    symptoms = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1,
        help_text="List of symptom IDs"
    )
    livestock_id = serializers.IntegerField(required=False, allow_null=True)
    
    def validate_animal_type_id(self, value):
        """Validate that animal type exists"""
        try:
            AnimalType.objects.get(id=value)
        except AnimalType.DoesNotExist:
            raise serializers.ValidationError("Animal type not found")
        return value
    
    def validate_symptoms(self, value):
        """Validate that all symptom IDs exist"""
        existing_symptoms = Symptom.objects.filter(id__in=value).count()
        if existing_symptoms != len(value):
            raise serializers.ValidationError("One or more symptom IDs are invalid")
        return value
    
    def validate_livestock_id(self, value):
        """Validate that livestock exists if provided"""
        if value is not None:
            try:
                Livestock.objects.get(id=value)
            except Livestock.DoesNotExist:
                raise serializers.ValidationError("Livestock not found")
        return value


class DiseaseResultSerializer(serializers.Serializer):
    """Serializer for disease analysis results"""
    disease = DiseaseSerializer(read_only=True)
    confidence_score = serializers.FloatField()
    matching_symptoms = SymptomSerializer(many=True, read_only=True)
    missing_symptoms = SymptomSerializer(many=True, read_only=True)
    severity_level = serializers.CharField()
    requires_vet = serializers.BooleanField()
    recommendations = serializers.CharField()
    prevention_tips = serializers.CharField()


class SymptomAnalysisResponseSerializer(serializers.Serializer):
    """Serializer for symptom analysis response"""
    animal_info = serializers.DictField()
    input_symptoms = SymptomSerializer(many=True, read_only=True)
    disease_results = DiseaseResultSerializer(many=True, read_only=True)
    critical_alerts = DiseaseResultSerializer(many=True, read_only=True)
    total_diseases_found = serializers.IntegerField()
    highest_confidence = serializers.FloatField()


class HealthRecordCreateSerializer(serializers.Serializer):
    """Serializer for creating health records"""
    livestock_id = serializers.IntegerField()
    symptom_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1
    )
    suspected_disease_id = serializers.IntegerField(required=False, allow_null=True)
    notes = serializers.CharField(required=False, allow_blank=True, max_length=1000)
    
    def validate_livestock_id(self, value):
        try:
            Livestock.objects.get(id=value)
        except Livestock.DoesNotExist:
            raise serializers.ValidationError("Livestock not found")
        return value
    
    def validate_symptom_ids(self, value):
        existing_symptoms = Symptom.objects.filter(id__in=value).count()
        if existing_symptoms != len(value):
            raise serializers.ValidationError("One or more symptom IDs are invalid")
        return value
    
    def validate_suspected_disease_id(self, value):
        if value is not None:
            try:
                Disease.objects.get(id=value)
            except Disease.DoesNotExist:
                raise serializers.ValidationError("Disease not found")
        return value


class PreventionRecommendationSerializer(serializers.Serializer):
    """Serializer for prevention recommendations"""
    animal_type = serializers.CharField()
    prevention_tips = serializers.ListField(child=serializers.DictField())
    critical_diseases_to_watch = serializers.ListField(child=serializers.DictField())
    general_recommendations = serializers.ListField(child=serializers.CharField())


class SymptomSuggestionSerializer(serializers.Serializer):
    """Serializer for symptom suggestions"""
    id = serializers.IntegerField()
    name = serializers.CharField()
    description = serializers.CharField()
    related_diseases_count = serializers.IntegerField()
    severity_levels = serializers.ListField(child=serializers.CharField())


# Pricing Module Serializers

class PriceAnalysisInputSerializer(serializers.Serializer):
    """Serializer for price analysis input"""
    animal_type_id = serializers.IntegerField()
    breed_id = serializers.IntegerField(required=False, allow_null=True)
    location = serializers.CharField(required=False, allow_blank=True, max_length=100)
    weight_kg = serializers.FloatField(required=False, allow_null=True, min_value=0)
    quality_grade = serializers.ChoiceField(
        choices=[('PREMIUM', 'Premium'), ('GOOD', 'Good'), ('AVERAGE', 'Average'), ('POOR', 'Poor')],
        required=False,
        allow_blank=True
    )
    
    def validate_animal_type_id(self, value):
        try:
            AnimalType.objects.get(id=value)
        except AnimalType.DoesNotExist:
            raise serializers.ValidationError("Animal type not found")
        return value
    
    def validate_breed_id(self, value):
        if value is not None:
            try:
                Breed.objects.get(id=value)
            except Breed.DoesNotExist:
                raise serializers.ValidationError("Breed not found")
        return value


class PriceRecommendationSerializer(serializers.Serializer):
    """Serializer for price recommendation results"""
    current_price = serializers.FloatField()
    price_trend = serializers.CharField()
    trend_percentage = serializers.FloatField()
    recommendation = serializers.CharField()
    confidence_level = serializers.CharField()
    factors = serializers.ListField(child=serializers.CharField())
    optimal_selling_period = serializers.CharField()
    profit_estimate = serializers.FloatField(required=False, allow_null=True)


class MarketAnalysisSerializer(serializers.Serializer):
    """Serializer for market analysis results"""
    average_price = serializers.FloatField()
    min_price = serializers.FloatField()
    max_price = serializers.FloatField()
    price_variance = serializers.FloatField()
    market_locations = serializers.ListField(child=serializers.CharField())
    best_location = serializers.CharField()
    price_history = serializers.ListField(child=serializers.DictField())
    seasonal_trends = serializers.DictField()


class ProfitAnalysisInputSerializer(serializers.Serializer):
    """Serializer for profit analysis input"""
    livestock_id = serializers.IntegerField()
    sale_price_per_kg = serializers.FloatField(min_value=0)
    sale_weight_kg = serializers.FloatField(min_value=0)
    
    def validate_livestock_id(self, value):
        try:
            Livestock.objects.get(id=value)
        except Livestock.DoesNotExist:
            raise serializers.ValidationError("Livestock not found")
        return value


class ProfitAnalysisSerializer(serializers.Serializer):
    """Serializer for profit analysis results"""
    livestock_info = serializers.DictField()
    revenue = serializers.DictField()
    costs = serializers.DictField()
    profit_analysis = serializers.DictField()


class PriceAlertSerializer(serializers.ModelSerializer):
    """Serializer for price alerts"""
    animal_type = AnimalTypeSerializer(read_only=True)
    breed = BreedSerializer(read_only=True)
    farmer_username = serializers.CharField(source='farmer.username', read_only=True)
    
    class Meta:
        model = PriceAlert
        fields = ['id', 'animal_type', 'breed', 'location', 'target_price',
                 'alert_type', 'is_active', 'triggered_at', 'farmer_username']


class SaleRecordSerializer(serializers.ModelSerializer):
    """Serializer for sale records"""
    livestock = LivestockSerializer(read_only=True)
    farmer_username = serializers.CharField(source='farmer.username', read_only=True)
    
    class Meta:
        model = SaleRecord
        fields = ['id', 'livestock', 'sale_date', 'sale_price_per_kg', 'total_weight_kg',
                 'total_amount', 'buyer_name', 'location', 'transportation_cost',
                 'commission_cost', 'net_profit', 'farmer_username']


class CostRecordSerializer(serializers.ModelSerializer):
    """Serializer for cost records"""
    livestock = LivestockSerializer(read_only=True)
    farmer_username = serializers.CharField(source='farmer.username', read_only=True)
    
    class Meta:
        model = CostRecord
        fields = ['id', 'livestock', 'category', 'description', 'amount',
                 'date_incurred', 'notes', 'farmer_username']


# Pricing Analysis Serializers

class PriceAnalysisResultSerializer(serializers.Serializer):
    """Serializer for price analysis results"""
    current_price_per_kg = serializers.FloatField()
    price_trend = serializers.CharField()
    trend_percentage = serializers.FloatField()
    market_recommendation = serializers.CharField()
    confidence_level = serializers.CharField()
    historical_data = serializers.ListField(child=serializers.DictField())
    location = serializers.CharField()
    date_analyzed = serializers.CharField()


class ProfitabilityResultSerializer(serializers.Serializer):
    """Serializer for profitability analysis results"""
    livestock_id = serializers.IntegerField()
    current_market_value = serializers.FloatField()
    total_investment = serializers.FloatField()
    estimated_profit = serializers.FloatField()
    profit_margin_percentage = serializers.FloatField()
    break_even_price = serializers.FloatField()
    recommendation = serializers.CharField()
    cost_breakdown = serializers.DictField()


class SellingRecommendationSerializer(serializers.Serializer):
    """Serializer for selling recommendations"""
    livestock = LivestockSerializer(read_only=True)
    profitability = ProfitabilityResultSerializer()
    action_priority = serializers.IntegerField()
    optimal_selling_time = serializers.CharField()
