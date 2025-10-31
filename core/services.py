
from django.db import models
from typing import List, Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .models import Disease, Symptom

from dataclasses import dataclass
from .models import (
    AnimalType, FeedType, FeedingRecommendation, Livestock
)






@dataclass
class FeedingResult:
    """Data class for feeding recommendation results"""
    feed_type: FeedType
    daily_amount_kg: float
    feeding_frequency: int
    cost_per_day: float
    notes: str
    recommendation_source: str


@dataclass
class AnimalInput:
    """Data class for animal input parameters"""
    animal_type_id: int
    age_months: Optional[int] = None
    weight_kg: Optional[float] = None
    purpose: Optional[str] = None
    livestock_id: Optional[int] = None  # If recommendations for existing livestock


class FeedingRecommendationService:
    """
    Service class to handle feeding recommendation logic
    """
    
    def get_recommendations(self, animal_input: AnimalInput) -> List[FeedingResult]:
        """
        Get feeding recommendations based on animal parameters
        
        Args:
            animal_input: AnimalInput object with animal details
            
        Returns:
            List of FeedingResult objects with recommendations
        """
        try:
            animal_type = AnimalType.objects.get(id=animal_input.animal_type_id)
        except AnimalType.DoesNotExist:
            return []
        
        # If livestock_id provided, get data from existing livestock
        if animal_input.livestock_id:
            try:
                livestock = Livestock.objects.get(id=animal_input.livestock_id)
                animal_input.age_months = livestock.age_months
                animal_input.weight_kg = float(livestock.current_weight_kg or 0)
                animal_input.purpose = livestock.purpose
            except Livestock.DoesNotExist:
                pass
        
        # Get base recommendations from database
        base_recommendations = self._get_base_recommendations(animal_type, animal_input)
        
        # Apply intelligent adjustments
        adjusted_recommendations = self._apply_intelligent_adjustments(base_recommendations, animal_input)
        
        # Convert to FeedingResult objects
        results = []
        for rec in adjusted_recommendations:
            cost_per_day = self._calculate_daily_cost(rec['feed_type'], rec['daily_amount_kg'])
            
            result = FeedingResult(
                feed_type=rec['feed_type'],
                daily_amount_kg=rec['daily_amount_kg'],
                feeding_frequency=rec['feeding_frequency'],
                cost_per_day=cost_per_day,
                notes=rec['notes'],
                recommendation_source=rec['source']
            )
            results.append(result)
        
        # Sort by priority (cost-effectiveness and nutritional value)
        results.sort(key=lambda x: (x.cost_per_day, -x.feed_type.protein_percentage))
        
        return results[:5]  # Return top 5 recommendations
    
    def _get_base_recommendations(self, animal_type: AnimalType, animal_input: AnimalInput) -> List[Dict]:
        """Get base recommendations from database"""
        recommendations = FeedingRecommendation.objects.filter(
            animal_type=animal_type
        )
        
        # Filter by age if provided
        if animal_input.age_months is not None:
            recommendations = recommendations.filter(
                min_age_months__lte=animal_input.age_months
            ).filter(
                models.Q(max_age_months__gte=animal_input.age_months) | 
                models.Q(max_age_months__isnull=True)
            )
        
        # Filter by weight if provided
        if animal_input.weight_kg is not None:
            recommendations = recommendations.filter(
                min_weight_kg__lte=animal_input.weight_kg
            ).filter(
                models.Q(max_weight_kg__gte=animal_input.weight_kg) |
                models.Q(max_weight_kg__isnull=True)
            )
        
        # Filter by purpose if provided
        if animal_input.purpose:
            recommendations = recommendations.filter(
                models.Q(purpose=animal_input.purpose) |
                models.Q(purpose='')
            )
        
        # Convert to dict format for processing
        base_recs = []
        for rec in recommendations:
            base_recs.append({
                'feed_type': rec.feed_type,
                'daily_amount_kg': float(rec.daily_amount_kg),
                'feeding_frequency': rec.feeding_frequency,
                'notes': rec.notes or '',
                'source': 'Database Recommendation'
            })
        
        return base_recs
    
    def _apply_intelligent_adjustments(self, base_recommendations: List[Dict], animal_input: AnimalInput) -> List[Dict]:
        """Apply intelligent adjustments based on animal specifics"""
        adjusted_recs = []
        
        for rec in base_recommendations:
            adjusted_rec = rec.copy()
            
            # Weight-based adjustments
            if animal_input.weight_kg:
                weight_factor = self._calculate_weight_factor(animal_input.weight_kg, animal_input.animal_type_id)
                adjusted_rec['daily_amount_kg'] *= weight_factor
                
                if weight_factor != 1.0:
                    adjusted_rec['notes'] += f" Amount adjusted by {weight_factor:.2f}x for weight."
                    adjusted_rec['source'] = 'Smart Recommendation (Weight Adjusted)'
            
            # Age-based adjustments
            if animal_input.age_months:
                age_factor = self._calculate_age_factor(animal_input.age_months, animal_input.animal_type_id)
                adjusted_rec['daily_amount_kg'] *= age_factor
                
                if age_factor != 1.0:
                    adjusted_rec['notes'] += f" Amount adjusted by {age_factor:.2f}x for age."
                    if 'Smart Recommendation' not in adjusted_rec['source']:
                        adjusted_rec['source'] = 'Smart Recommendation (Age Adjusted)'
            
            # Purpose-based adjustments
            if animal_input.purpose:
                purpose_factor = self._calculate_purpose_factor(animal_input.purpose)
                adjusted_rec['daily_amount_kg'] *= purpose_factor
                
                if purpose_factor != 1.0:
                    adjusted_rec['notes'] += f" Amount adjusted by {purpose_factor:.2f}x for {animal_input.purpose.lower()} purpose."
                    if 'Smart Recommendation' not in adjusted_rec['source']:
                        adjusted_rec['source'] = 'Smart Recommendation (Purpose Adjusted)'
            
            # Round to reasonable precision
            adjusted_rec['daily_amount_kg'] = round(adjusted_rec['daily_amount_kg'], 2)
            
            adjusted_recs.append(adjusted_rec)
        
        # Add emergency/backup recommendations if no base recommendations found
        if not adjusted_recs:
            adjusted_recs = self._get_emergency_recommendations(animal_input)
        
        return adjusted_recs
    
    def _calculate_weight_factor(self, weight_kg: float, animal_type_id: int) -> float:
        """Calculate adjustment factor based on weight"""
        # Basic weight-based scaling
        # These are simplified rules - in reality, would be more complex
        
        animal_type = AnimalType.objects.get(id=animal_type_id)
        
        if animal_type.name == 'Cattle':
            if weight_kg < 100:
                return 0.6  # Young cattle need less
            elif weight_kg < 300:
                return 0.8  # Growing cattle
            elif weight_kg > 600:
                return 1.2  # Large cattle need more
        elif animal_type.name in ['Goats', 'Sheep']:
            if weight_kg < 20:
                return 0.7  # Young animals
            elif weight_kg > 70:
                return 1.1  # Large animals
        elif animal_type.name == 'Poultry':
            if weight_kg < 1:
                return 0.8  # Young birds
            elif weight_kg > 3:
                return 1.1  # Large birds
        
        return 1.0  # No adjustment needed
    
    def _calculate_age_factor(self, age_months: int, animal_type_id: int) -> float:
        """Calculate adjustment factor based on age"""
        animal_type = AnimalType.objects.get(id=animal_type_id)
        
        if animal_type.name == 'Cattle':
            if age_months < 6:
                return 0.5  # Calves need less solid feed
            elif age_months < 12:
                return 0.8  # Young cattle
            elif age_months > 60:
                return 1.1  # Older cattle may need more
        elif animal_type.name in ['Goats', 'Sheep']:
            if age_months < 3:
                return 0.6  # Very young
            elif age_months < 8:
                return 0.9  # Growing
        elif animal_type.name == 'Poultry':
            if age_months < 2:
                return 0.7  # Young birds
            elif age_months > 12:
                return 1.05  # Older birds
        
        return 1.0
    
    def _calculate_purpose_factor(self, purpose: str) -> float:
        """Calculate adjustment factor based on animal purpose"""
        purpose_factors = {
            'MILK': 1.3,      # Dairy animals need more nutrition
            'EGGS': 1.2,      # Laying birds need more nutrition  
            'BREEDING': 1.25, # Breeding animals need extra nutrition
            'MEAT': 1.1,      # Meat animals need good nutrition for growth
            'MIXED': 1.15,    # Mixed purpose - moderate increase
        }
        
        return purpose_factors.get(purpose, 1.0)
    
    def _get_emergency_recommendations(self, animal_input: AnimalInput) -> List[Dict]:
        """Provide basic recommendations when no database matches found"""
        try:
            animal_type = AnimalType.objects.get(id=animal_input.animal_type_id)
        except AnimalType.DoesNotExist:
            return []
        
        # Get any suitable feeds for this animal type
        suitable_feeds = FeedType.objects.filter(suitable_for=animal_type)
        
        emergency_recs = []
        for feed in suitable_feeds[:3]:  # Top 3 suitable feeds
            # Basic amounts based on animal type
            if animal_type.name == 'Cattle':
                base_amount = 15.0
            elif animal_type.name in ['Goats', 'Sheep']:
                base_amount = 2.5
            elif animal_type.name == 'Poultry':
                base_amount = 0.15
            else:
                base_amount = 5.0
            
            emergency_recs.append({
                'feed_type': feed,
                'daily_amount_kg': base_amount,
                'feeding_frequency': 2,
                'notes': 'Basic recommendation - please consult with veterinarian for specific needs.',
                'source': 'Emergency Recommendation'
            })
        
        return emergency_recs
    
    def _calculate_daily_cost(self, feed_type: FeedType, daily_amount_kg: float) -> float:
        """Calculate daily feeding cost"""
        if feed_type.cost_per_kg:
            return float(feed_type.cost_per_kg) * daily_amount_kg
        return 0.0
    
    def get_feeding_summary_for_livestock(self, livestock_id: int) -> Dict:
        """Get feeding summary for a specific livestock animal"""
        try:
            livestock = Livestock.objects.get(id=livestock_id)
        except Livestock.DoesNotExist:
            return {'error': 'Livestock not found'}
        
        animal_input = AnimalInput(
            animal_type_id=livestock.animal_type.id,
            livestock_id=livestock_id
        )
        
        recommendations = self.get_recommendations(animal_input)
        
        total_daily_cost = sum(rec.cost_per_day for rec in recommendations)
        
        return {
            'livestock': livestock,
            'recommendations': recommendations,
            'total_daily_cost': total_daily_cost,
            'monthly_cost_estimate': total_daily_cost * 30,
            'summary': {
                'animal_info': f"{livestock.animal_type.name} - {livestock.name or livestock.tag_number}",
                'age_months': livestock.age_months,
                'weight_kg': livestock.current_weight_kg,
                'purpose': livestock.get_purpose_display(),
                'recommendation_count': len(recommendations)
            }
        }





@dataclass
class SymptomInput:
    """Data class for symptom input parameters"""
    animal_type_id: int
    symptoms: List[int]  # List of symptom IDs
    livestock_id: Optional[int] = None


@dataclass
class DiseaseResult:
    """Data class for disease diagnosis results"""
    disease: 'Disease'
    confidence_score: float
    matching_symptoms: List['Symptom']
    missing_symptoms: List['Symptom']
    severity_level: str
    requires_vet: bool
    recommendations: str
    prevention_tips: str


class DiseaseMonitoringService:
    """
    Service class to handle disease monitoring and symptom matching
    """
    
    def analyze_symptoms(self, symptom_input: SymptomInput) -> List[DiseaseResult]:
        """
        Analyze symptoms and return possible diseases with confidence scores
        
        Args:
            symptom_input: SymptomInput object with animal type and symptoms
            
        Returns:
            List of DiseaseResult objects sorted by confidence score
        """
        from .models import AnimalType, Disease, Symptom
        
        try:
            animal_type = AnimalType.objects.get(id=symptom_input.animal_type_id)
        except AnimalType.DoesNotExist:
            return []
        
        # Get input symptoms
        input_symptoms = Symptom.objects.filter(id__in=symptom_input.symptoms)
        if not input_symptoms.exists():
            return []
        
        # Get diseases that affect this animal type
        potential_diseases = Disease.objects.filter(
            affected_animals=animal_type
        ).prefetch_related('symptoms')
        
        # Analyze each disease for symptom matches
        disease_results = []
        for disease in potential_diseases:
            result = self._analyze_disease_match(disease, input_symptoms)
            if result.confidence_score > 0:  # Only include diseases with some symptom match
                disease_results.append(result)
        
        # Sort by confidence score (highest first)
        disease_results.sort(key=lambda x: x.confidence_score, reverse=True)
        
        return disease_results[:10]  # Return top 10 matches
    
    def _analyze_disease_match(self, disease, input_symptoms) -> DiseaseResult:
        """Analyze how well input symptoms match a specific disease"""
        disease_symptoms = disease.symptoms.all()
        
        # Find matching symptoms
        matching_symptoms = list(set(input_symptoms) & set(disease_symptoms))
        
        # Find missing symptoms
        missing_symptoms = list(set(disease_symptoms) - set(matching_symptoms))
        
        # Calculate confidence score
        confidence_score = self._calculate_confidence_score(
            disease, 
            matching_symptoms, 
            missing_symptoms, 
            input_symptoms
        )
        
        return DiseaseResult(
            disease=disease,
            confidence_score=confidence_score,
            matching_symptoms=matching_symptoms,
            missing_symptoms=missing_symptoms,
            severity_level=disease.severity,
            requires_vet=disease.vet_required,
            recommendations=disease.treatment_advice or "Consult with a veterinarian for proper treatment.",
            prevention_tips=disease.prevention_measures or "Follow general livestock health practices."
        )
    
    def _calculate_confidence_score(self, disease, matching_symptoms, missing_symptoms, input_symptoms) -> float:
        """Calculate confidence score for disease match"""
        if not matching_symptoms:
            return 0.0
        
        total_disease_symptoms = len(disease.symptoms.all())
        total_input_symptoms = len(input_symptoms)
        matching_count = len(matching_symptoms)
        
        if total_disease_symptoms == 0:
            return 0.0
        
        # Base score: percentage of disease symptoms that are present
        base_score = matching_count / total_disease_symptoms
        
        # Bonus for high symptom match rate
        match_rate = matching_count / total_input_symptoms if total_input_symptoms > 0 else 0
        
        # Penalty for many unmatched input symptoms (might indicate different disease)
        excess_symptoms = max(0, total_input_symptoms - matching_count)
        excess_penalty = min(0.3, excess_symptoms * 0.1)  # Cap penalty at 30%
        
        # Severity weight (critical diseases get slight boost if symptoms match)
        severity_weight = {
            'CRITICAL': 1.1,
            'HIGH': 1.05,
            'MEDIUM': 1.0,
            'LOW': 0.95
        }.get(disease.severity, 1.0)
        
        # Contagious diseases get slight boost (important to catch early)
        contagious_weight = 1.05 if disease.is_contagious else 1.0
        
        # Calculate final score
        final_score = (base_score * 0.7 + match_rate * 0.3) * severity_weight * contagious_weight - excess_penalty
        
        # Ensure score is between 0 and 1
        return max(0.0, min(1.0, final_score))
    
    def get_critical_alerts(self, symptom_input: SymptomInput) -> List[DiseaseResult]:
        """Get critical disease alerts that require immediate attention"""
        all_results = self.analyze_symptoms(symptom_input)
        
        # Filter for critical and high severity diseases with reasonable confidence
        critical_alerts = [
            result for result in all_results
            if result.severity_level in ['CRITICAL', 'HIGH'] and result.confidence_score > 0.3
        ]
        
        return critical_alerts
    
    def get_prevention_recommendations(self, animal_type_id: int) -> Dict:
        """Get general prevention recommendations for an animal type"""
        from .models import AnimalType, Disease
        
        try:
            animal_type = AnimalType.objects.get(id=animal_type_id)
        except AnimalType.DoesNotExist:
            return {'error': 'Animal type not found'}
        
        # Get common diseases for this animal type
        common_diseases = Disease.objects.filter(
            affected_animals=animal_type
        ).order_by('severity')
        
        prevention_tips = []
        critical_diseases = []
        
        for disease in common_diseases:
            if disease.prevention_measures:
                prevention_tips.append({
                    'disease': disease.name,
                    'prevention': disease.prevention_measures,
                    'severity': disease.severity
                })
            
            if disease.severity in ['CRITICAL', 'HIGH']:
                critical_diseases.append({
                    'name': disease.name,
                    'severity': disease.severity,
                    'is_contagious': disease.is_contagious
                })
        
        return {
            'animal_type': animal_type.name,
            'prevention_tips': prevention_tips,
            'critical_diseases_to_watch': critical_diseases,
            'general_recommendations': [
                'Maintain clean and dry living conditions',
                'Provide fresh, clean water daily',
                'Follow proper feeding schedules and nutrition',
                'Regular health checks and observations',
                'Quarantine new animals before introducing to herd',
                'Keep vaccination schedules up to date',
                'Maintain proper ventilation in housing',
                'Practice good hygiene when handling animals'
            ]
        }
    
    def create_health_record(self, livestock_id: int, symptom_ids: List[int], suspected_disease_id: Optional[int] = None) -> Dict:
        """Create a health record for livestock based on symptoms"""
        from .models import Livestock, Symptom, Disease, HealthRecord
        
        try:
            livestock = Livestock.objects.get(id=livestock_id)
        except Livestock.DoesNotExist:
            return {'error': 'Livestock not found'}
        
        symptoms = Symptom.objects.filter(id__in=symptom_ids)
        suspected_disease = None
        
        if suspected_disease_id:
            try:
                suspected_disease = Disease.objects.get(id=suspected_disease_id)
            except Disease.DoesNotExist:
                pass
        
        # Create health record
        health_record = HealthRecord.objects.create(
            livestock=livestock,
            suspected_disease=suspected_disease,
            diagnosis=f"Symptoms observed: {', '.join([s.name for s in symptoms])}",
            veterinarian_consulted=False,
            recovery_status='ONGOING'
        )
        
        # Add symptoms to the record
        health_record.symptoms.set(symptoms)
        
        return {
            'health_record_id': health_record.id,
            'livestock': livestock.tag_number,
            'symptoms_count': symptoms.count(),
            'suspected_disease': suspected_disease.name if suspected_disease else None,
            'requires_vet_attention': suspected_disease.vet_required if suspected_disease else False
        }
    
    def get_symptom_suggestions(self, animal_type_id: int, partial_symptoms: List[int] = None) -> List[Dict]:
        """Get symptom suggestions based on animal type and partial symptom input"""
        from .models import AnimalType, Symptom
        
        try:
            animal_type = AnimalType.objects.get(id=animal_type_id)
        except AnimalType.DoesNotExist:
            return []
        
        # Get diseases that affect this animal type
        diseases_for_animal = animal_type.diseases.all()
        
        # Get all symptoms related to these diseases
        relevant_symptoms = Symptom.objects.filter(
            diseases__in=diseases_for_animal
        ).distinct().order_by('name')
        
        symptom_suggestions = []
        for symptom in relevant_symptoms:
            # Get related diseases for context
            related_diseases = symptom.diseases.filter(affected_animals=animal_type)
            
            symptom_suggestions.append({
                'id': symptom.id,
                'name': symptom.name,
                'description': symptom.description,
                'related_diseases_count': related_diseases.count(),
                'severity_levels': list(related_diseases.values_list('severity', flat=True).distinct())
            })
        
        return symptom_suggestions
