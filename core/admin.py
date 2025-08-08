from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import (
    FarmerProfile, AnimalType, Breed, Livestock, FeedType, 
    FeedingRecommendation, Disease, Symptom, HealthRecord, MarketPrice
)


class FarmerProfileInline(admin.StackedInline):
    model = FarmerProfile
    can_delete = False
    verbose_name_plural = 'Farmer Profile'


class CustomUserAdmin(UserAdmin):
    inlines = (FarmerProfileInline,)


# Unregister the original User admin and register our custom one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(AnimalType)
class AnimalTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at']
    search_fields = ['name']
    ordering = ['name']


@admin.register(Breed)
class BreedAdmin(admin.ModelAdmin):
    list_display = ['name', 'animal_type', 'average_weight_kg', 'maturity_months']
    list_filter = ['animal_type']
    search_fields = ['name', 'animal_type__name']
    ordering = ['animal_type', 'name']


@admin.register(Livestock)
class LivestockAdmin(admin.ModelAdmin):
    list_display = ['tag_number', 'name', 'animal_type', 'breed', 'gender', 'status', 'farmer', 'age_months']
    list_filter = ['animal_type', 'breed', 'gender', 'status', 'purpose']
    search_fields = ['tag_number', 'name', 'farmer__username']
    ordering = ['animal_type', 'tag_number']
    readonly_fields = ['age_months', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('farmer', 'animal_type', 'breed', 'tag_number', 'name')
        }),
        ('Physical Details', {
            'fields': ('gender', 'date_of_birth', 'current_weight_kg')
        }),
        ('Purpose & Status', {
            'fields': ('purpose', 'status')
        }),
        ('Purchase Information', {
            'fields': ('purchase_date', 'purchase_price')
        }),
        ('Additional Information', {
            'fields': ('notes',)
        }),
        ('System Information', {
            'fields': ('age_months', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(FeedType)
class FeedTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'protein_percentage', 'energy_mj_per_kg', 'cost_per_kg']
    list_filter = ['category']
    search_fields = ['name']
    filter_horizontal = ['suitable_for']
    ordering = ['category', 'name']


@admin.register(FeedingRecommendation)
class FeedingRecommendationAdmin(admin.ModelAdmin):
    list_display = ['animal_type', 'feed_type', 'purpose', 'daily_amount_kg', 'feeding_frequency']
    list_filter = ['animal_type', 'feed_type', 'purpose']
    search_fields = ['animal_type__name', 'feed_type__name']
    ordering = ['animal_type', 'feed_type']


@admin.register(Disease)
class DiseaseAdmin(admin.ModelAdmin):
    list_display = ['name', 'severity', 'is_contagious', 'vet_required']
    list_filter = ['severity', 'is_contagious', 'vet_required', 'affected_animals']
    search_fields = ['name']
    filter_horizontal = ['affected_animals']
    ordering = ['name']


@admin.register(Symptom)
class SymptomAdmin(admin.ModelAdmin):
    list_display = ['name', 'get_related_diseases']
    search_fields = ['name']
    filter_horizontal = ['diseases']
    ordering = ['name']
    
    def get_related_diseases(self, obj):
        return ", ".join([disease.name for disease in obj.diseases.all()[:3]])
    get_related_diseases.short_description = 'Related Diseases (first 3)'


@admin.register(HealthRecord)
class HealthRecordAdmin(admin.ModelAdmin):
    list_display = ['livestock', 'date_recorded', 'suspected_disease', 'recovery_status', 'veterinarian_consulted']
    list_filter = ['recovery_status', 'veterinarian_consulted', 'suspected_disease']
    search_fields = ['livestock__tag_number', 'livestock__name']
    filter_horizontal = ['symptoms']
    ordering = ['-date_recorded']
    readonly_fields = ['date_recorded']


@admin.register(MarketPrice)
class MarketPriceAdmin(admin.ModelAdmin):
    list_display = ['animal_type', 'breed', 'location', 'date_recorded', 'price_per_kg', 'quality_grade']
    list_filter = ['animal_type', 'breed', 'quality_grade', 'location']
    search_fields = ['animal_type__name', 'location']
    ordering = ['-date_recorded', 'animal_type']
    readonly_fields = ['created_at']


# Customize admin site header and title
admin.site.site_header = "Livestock Management Admin"
admin.site.site_title = "Livestock Admin"
admin.site.index_title = "Welcome to Livestock Management Administration"
