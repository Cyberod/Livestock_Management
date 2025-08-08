from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class FarmerProfile(models.Model):
    """
    Extended user profile for farmers with livestock management specific fields
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='farmer_profile')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    farm_size_acres = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    experience_years = models.PositiveIntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Farm Profile"
    
    class Meta:
        verbose_name = "Farmer Profile"
        verbose_name_plural = "Farmer Profiles"


class AnimalType(models.Model):
    """
    Different types of livestock (cattle, goats, sheep, poultry)
    """
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Animal Type"
        verbose_name_plural = "Animal Types"


class Breed(models.Model):
    """
    Specific breeds for each animal type
    """
    animal_type = models.ForeignKey(AnimalType, on_delete=models.CASCADE, related_name='breeds')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    average_weight_kg = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    maturity_months = models.PositiveIntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.animal_type.name} - {self.name}"
    
    class Meta:
        unique_together = ['animal_type', 'name']
        verbose_name = "Breed"
        verbose_name_plural = "Breeds"


class Livestock(models.Model):
    """
    Individual livestock animals owned by farmers
    """
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]
    
    PURPOSE_CHOICES = [
        ('MEAT', 'Meat Production'),
        ('MILK', 'Milk Production'),
        ('EGGS', 'Egg Production'),
        ('BREEDING', 'Breeding'),
        ('MIXED', 'Mixed Purpose'),
    ]
    
    STATUS_CHOICES = [
        ('HEALTHY', 'Healthy'),
        ('SICK', 'Sick'),
        ('PREGNANT', 'Pregnant'),
        ('QUARANTINE', 'Quarantine'),
        ('SOLD', 'Sold'),
        ('DECEASED', 'Deceased'),
    ]
    
    farmer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='livestock')
    animal_type = models.ForeignKey(AnimalType, on_delete=models.CASCADE)
    breed = models.ForeignKey(Breed, on_delete=models.CASCADE, blank=True, null=True)
    tag_number = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    date_of_birth = models.DateField(blank=True, null=True)
    current_weight_kg = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='HEALTHY')
    purchase_date = models.DateField(blank=True, null=True)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        display_name = self.name if self.name else f"Tag #{self.tag_number}"
        return f"{display_name} ({self.animal_type.name})"
    
    @property
    def age_months(self):
        if self.date_of_birth:
            from datetime import date
            today = date.today()
            return (today.year - self.date_of_birth.year) * 12 + today.month - self.date_of_birth.month
        return None
    
    class Meta:
        verbose_name = "Livestock"
        verbose_name_plural = "Livestock"


class FeedType(models.Model):
    """
    Different types of feed available for livestock
    """
    FEED_CATEGORY_CHOICES = [
        ('HAY', 'Hay'),
        ('GRAIN', 'Grain'),
        ('PELLETS', 'Pellets'),
        ('SILAGE', 'Silage'),
        ('PASTURE', 'Pasture'),
        ('SUPPLEMENT', 'Supplement'),
        ('CONCENTRATE', 'Concentrate'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=20, choices=FEED_CATEGORY_CHOICES)
    description = models.TextField(blank=True)
    protein_percentage = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    energy_mj_per_kg = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    cost_per_kg = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    suitable_for = models.ManyToManyField(AnimalType, related_name='suitable_feeds')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} ({self.category})"
    
    class Meta:
        verbose_name = "Feed Type"
        verbose_name_plural = "Feed Types"


class FeedingRecommendation(models.Model):
    """
    Feeding recommendations based on animal type, age, weight, and purpose
    """
    animal_type = models.ForeignKey(AnimalType, on_delete=models.CASCADE)
    feed_type = models.ForeignKey(FeedType, on_delete=models.CASCADE)
    min_age_months = models.PositiveIntegerField(default=0)
    max_age_months = models.PositiveIntegerField(blank=True, null=True)
    min_weight_kg = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    max_weight_kg = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    purpose = models.CharField(max_length=20, choices=Livestock.PURPOSE_CHOICES, blank=True)
    daily_amount_kg = models.DecimalField(max_digits=6, decimal_places=3)
    feeding_frequency = models.PositiveIntegerField(default=2, help_text="Times per day")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.animal_type.name} - {self.feed_type.name} ({self.daily_amount_kg}kg/day)"
    
    class Meta:
        verbose_name = "Feeding Recommendation"
        verbose_name_plural = "Feeding Recommendations"


class Disease(models.Model):
    """
    Common diseases that affect livestock
    """
    SEVERITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    affected_animals = models.ManyToManyField(AnimalType, related_name='diseases')
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES)
    is_contagious = models.BooleanField(default=False)
    prevention_measures = models.TextField(blank=True)
    treatment_advice = models.TextField(blank=True)
    vet_required = models.BooleanField(default=False, help_text="Requires veterinary attention")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Disease"
        verbose_name_plural = "Diseases"


class Symptom(models.Model):
    """
    Symptoms associated with livestock diseases
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    diseases = models.ManyToManyField(Disease, related_name='symptoms')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Symptom"
        verbose_name_plural = "Symptoms"


class HealthRecord(models.Model):
    """
    Health records for individual livestock
    """
    livestock = models.ForeignKey(Livestock, on_delete=models.CASCADE, related_name='health_records')
    date_recorded = models.DateTimeField(auto_now_add=True)
    symptoms = models.ManyToManyField(Symptom, blank=True)
    suspected_disease = models.ForeignKey(Disease, on_delete=models.SET_NULL, blank=True, null=True)
    diagnosis = models.TextField(blank=True)
    treatment_given = models.TextField(blank=True)
    veterinarian_consulted = models.BooleanField(default=False)
    recovery_status = models.CharField(max_length=20, choices=[
        ('ONGOING', 'Ongoing Treatment'),
        ('RECOVERED', 'Recovered'),
        ('CHRONIC', 'Chronic Condition'),
        ('DECEASED', 'Deceased'),
    ], default='ONGOING')
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.livestock} - {self.date_recorded.strftime('%Y-%m-%d')}"
    
    class Meta:
        verbose_name = "Health Record"
        verbose_name_plural = "Health Records"
        ordering = ['-date_recorded']


class MarketPrice(models.Model):
    """
    Market pricing data for livestock
    """
    animal_type = models.ForeignKey(AnimalType, on_delete=models.CASCADE)
    breed = models.ForeignKey(Breed, on_delete=models.CASCADE, blank=True, null=True)
    location = models.CharField(max_length=100)
    date_recorded = models.DateField()
    price_per_kg = models.DecimalField(max_digits=8, decimal_places=2)
    min_weight_kg = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    max_weight_kg = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    quality_grade = models.CharField(max_length=20, choices=[
        ('PREMIUM', 'Premium'),
        ('GOOD', 'Good'),
        ('AVERAGE', 'Average'),
        ('POOR', 'Poor'),
    ], default='AVERAGE')
    source = models.CharField(max_length=100, blank=True, help_text="Market or data source")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.animal_type.name} - ${self.price_per_kg}/kg ({self.location})"
    
    class Meta:
        verbose_name = "Market Price"
        verbose_name_plural = "Market Prices"
        ordering = ['-date_recorded']
