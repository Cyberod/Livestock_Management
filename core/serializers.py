from rest_framework import serializers
from .models import (
    AnimalType, Breed, Livestock, FeedType, FeedingRecommendation,
    Disease, Symptom, HealthRecord, MarketPrice, FarmerProfile
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
