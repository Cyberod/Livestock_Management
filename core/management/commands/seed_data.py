from django.core.management.base import BaseCommand
from datetime import date, timedelta
from core.models import (
    AnimalType, Breed, FeedType, FeedingRecommendation, 
    Disease, Symptom, MarketPrice
)


class Command(BaseCommand):
    help = 'Seed database with initial livestock management data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting data seeding...'))
        
        # Create Animal Types
        self.create_animal_types()
        
        # Create Breeds
        self.create_breeds()
        
        # Create Feed Types
        self.create_feed_types()
        
        # Create Feeding Recommendations
        self.create_feeding_recommendations()
        
        # Create Diseases and Symptoms
        self.create_diseases_and_symptoms()
        
        # Create Sample Market Prices
        self.create_market_prices()
        
        self.stdout.write(self.style.SUCCESS('Data seeding completed successfully!'))

    def create_animal_types(self):
        animal_types = [
            {
                'name': 'Cattle',
                'description': 'Domesticated bovine animals raised for meat, milk, and other dairy products'
            },
            {
                'name': 'Goats', 
                'description': 'Small ruminants raised for meat, milk, and fiber'
            },
            {
                'name': 'Sheep',
                'description': 'Woolly ruminants raised for meat, wool, and milk'
            },
            {
                'name': 'Poultry',
                'description': 'Domesticated birds raised for eggs, meat, and feathers'
            },
        ]
        
        for animal_data in animal_types:
            animal_type, created = AnimalType.objects.get_or_create(
                name=animal_data['name'],
                defaults={'description': animal_data['description']}
            )
            if created:
                self.stdout.write(f'Created animal type: {animal_type.name}')

    def create_breeds(self):
        breeds_data = {
            'Cattle': [
                {'name': 'Holstein', 'avg_weight': 650, 'maturity': 24},
                {'name': 'Angus', 'avg_weight': 550, 'maturity': 20},
                {'name': 'Brahman', 'avg_weight': 500, 'maturity': 22},
                {'name': 'Jersey', 'avg_weight': 400, 'maturity': 20},
            ],
            'Goats': [
                {'name': 'Boer', 'avg_weight': 70, 'maturity': 8},
                {'name': 'Nubian', 'avg_weight': 65, 'maturity': 10},
                {'name': 'Saanen', 'avg_weight': 60, 'maturity': 9},
                {'name': 'Kiko', 'avg_weight': 55, 'maturity': 7},
            ],
            'Sheep': [
                {'name': 'Dorper', 'avg_weight': 80, 'maturity': 8},
                {'name': 'Merino', 'avg_weight': 65, 'maturity': 9},
                {'name': 'Suffolk', 'avg_weight': 90, 'maturity': 8},
                {'name': 'Romney', 'avg_weight': 70, 'maturity': 9},
            ],
            'Poultry': [
                {'name': 'Rhode Island Red', 'avg_weight': 3, 'maturity': 5},
                {'name': 'Leghorn', 'avg_weight': 2.5, 'maturity': 4},
                {'name': 'Broiler', 'avg_weight': 2.8, 'maturity': 2},
                {'name': 'Sussex', 'avg_weight': 3.2, 'maturity': 5},
            ],
        }
        
        for animal_name, breeds in breeds_data.items():
            animal_type = AnimalType.objects.get(name=animal_name)
            for breed_data in breeds:
                breed, created = Breed.objects.get_or_create(
                    animal_type=animal_type,
                    name=breed_data['name'],
                    defaults={
                        'average_weight_kg': breed_data['avg_weight'],
                        'maturity_months': breed_data['maturity']
                    }
                )
                if created:
                    self.stdout.write(f'Created breed: {animal_type.name} - {breed.name}')

    def create_feed_types(self):
        feed_types = [
            # Hay
            {'name': 'Alfalfa Hay', 'category': 'HAY', 'protein': 18.0, 'energy': 8.5, 'cost': 0.25},
            {'name': 'Timothy Hay', 'category': 'HAY', 'protein': 12.0, 'energy': 7.8, 'cost': 0.20},
            {'name': 'Grass Hay', 'category': 'HAY', 'protein': 10.0, 'energy': 7.2, 'cost': 0.18},
            
            # Grains
            {'name': 'Corn', 'category': 'GRAIN', 'protein': 9.0, 'energy': 14.2, 'cost': 0.15},
            {'name': 'Barley', 'category': 'GRAIN', 'protein': 12.0, 'energy': 13.8, 'cost': 0.18},
            {'name': 'Wheat', 'category': 'GRAIN', 'protein': 14.0, 'energy': 13.5, 'cost': 0.22},
            
            # Pellets
            {'name': 'Cattle Pellets', 'category': 'PELLETS', 'protein': 16.0, 'energy': 11.5, 'cost': 0.35},
            {'name': 'Goat Pellets', 'category': 'PELLETS', 'protein': 14.0, 'energy': 10.8, 'cost': 0.40},
            {'name': 'Sheep Pellets', 'category': 'PELLETS', 'protein': 13.0, 'energy': 10.5, 'cost': 0.38},
            {'name': 'Poultry Feed', 'category': 'PELLETS', 'protein': 18.0, 'energy': 12.2, 'cost': 0.45},
            
            # Pasture
            {'name': 'Fresh Pasture', 'category': 'PASTURE', 'protein': 15.0, 'energy': 9.5, 'cost': 0.05},
            
            # Supplements
            {'name': 'Mineral Mix', 'category': 'SUPPLEMENT', 'protein': 0.0, 'energy': 0.0, 'cost': 1.20},
            {'name': 'Vitamin Supplement', 'category': 'SUPPLEMENT', 'protein': 0.0, 'energy': 0.0, 'cost': 2.50},
        ]
        
        # Get animal types for suitable_for relationships
        cattle = AnimalType.objects.get(name='Cattle')
        goats = AnimalType.objects.get(name='Goats')
        sheep = AnimalType.objects.get(name='Sheep')
        poultry = AnimalType.objects.get(name='Poultry')
        
        suitable_mapping = {
            'Alfalfa Hay': [cattle, goats, sheep],
            'Timothy Hay': [cattle, goats, sheep],
            'Grass Hay': [cattle, goats, sheep],
            'Corn': [cattle, goats, sheep, poultry],
            'Barley': [cattle, goats, sheep, poultry],
            'Wheat': [cattle, goats, sheep, poultry],
            'Cattle Pellets': [cattle],
            'Goat Pellets': [goats],
            'Sheep Pellets': [sheep],
            'Poultry Feed': [poultry],
            'Fresh Pasture': [cattle, goats, sheep],
            'Mineral Mix': [cattle, goats, sheep],
            'Vitamin Supplement': [cattle, goats, sheep, poultry],
        }
        
        for feed_data in feed_types:
            feed_type, created = FeedType.objects.get_or_create(
                name=feed_data['name'],
                defaults={
                    'category': feed_data['category'],
                    'protein_percentage': feed_data['protein'],
                    'energy_mj_per_kg': feed_data['energy'],
                    'cost_per_kg': feed_data['cost']
                }
            )
            
            if created:
                # Add suitable_for relationships
                if feed_data['name'] in suitable_mapping:
                    feed_type.suitable_for.set(suitable_mapping[feed_data['name']])
                self.stdout.write(f'Created feed type: {feed_type.name}')

    def create_feeding_recommendations(self):
        # Get required objects
        cattle = AnimalType.objects.get(name='Cattle')
        goats = AnimalType.objects.get(name='Goats')
        sheep = AnimalType.objects.get(name='Sheep')
        poultry = AnimalType.objects.get(name='Poultry')
        
        alfalfa = FeedType.objects.get(name='Alfalfa Hay')
        cattle_pellets = FeedType.objects.get(name='Cattle Pellets')
        goat_pellets = FeedType.objects.get(name='Goat Pellets')
        sheep_pellets = FeedType.objects.get(name='Sheep Pellets')
        poultry_feed = FeedType.objects.get(name='Poultry Feed')
        pasture = FeedType.objects.get(name='Fresh Pasture')
        
        recommendations = [
            # Cattle recommendations
            {'animal': cattle, 'feed': alfalfa, 'min_age': 0, 'max_age': 6, 'min_weight': 0, 'max_weight': 150, 'purpose': 'MILK', 'amount': 5.0, 'frequency': 2},
            {'animal': cattle, 'feed': cattle_pellets, 'min_age': 6, 'max_age': 24, 'min_weight': 150, 'max_weight': 500, 'purpose': 'MEAT', 'amount': 8.0, 'frequency': 2},
            {'animal': cattle, 'feed': pasture, 'min_age': 3, 'max_age': None, 'min_weight': 100, 'max_weight': None, 'purpose': '', 'amount': 25.0, 'frequency': 1},
            
            # Goat recommendations
            {'animal': goats, 'feed': alfalfa, 'min_age': 0, 'max_age': 12, 'min_weight': 0, 'max_weight': 30, 'purpose': 'MILK', 'amount': 1.5, 'frequency': 2},
            {'animal': goats, 'feed': goat_pellets, 'min_age': 3, 'max_age': None, 'min_weight': 15, 'max_weight': None, 'purpose': 'MEAT', 'amount': 1.0, 'frequency': 2},
            {'animal': goats, 'feed': pasture, 'min_age': 2, 'max_age': None, 'min_weight': 10, 'max_weight': None, 'purpose': '', 'amount': 3.0, 'frequency': 1},
            
            # Sheep recommendations
            {'animal': sheep, 'feed': alfalfa, 'min_age': 0, 'max_age': 8, 'min_weight': 0, 'max_weight': 40, 'purpose': 'MEAT', 'amount': 2.0, 'frequency': 2},
            {'animal': sheep, 'feed': sheep_pellets, 'min_age': 4, 'max_age': None, 'min_weight': 20, 'max_weight': None, 'purpose': 'MEAT', 'amount': 1.2, 'frequency': 2},
            {'animal': sheep, 'feed': pasture, 'min_age': 2, 'max_age': None, 'min_weight': 15, 'max_weight': None, 'purpose': '', 'amount': 4.0, 'frequency': 1},
            
            # Poultry recommendations
            {'animal': poultry, 'feed': poultry_feed, 'min_age': 0, 'max_age': 2, 'min_weight': 0, 'max_weight': 1, 'purpose': 'EGGS', 'amount': 0.12, 'frequency': 2},
            {'animal': poultry, 'feed': poultry_feed, 'min_age': 2, 'max_age': None, 'min_weight': 1, 'max_weight': None, 'purpose': 'MEAT', 'amount': 0.15, 'frequency': 3},
        ]
        
        for rec_data in recommendations:
            recommendation, created = FeedingRecommendation.objects.get_or_create(
                animal_type=rec_data['animal'],
                feed_type=rec_data['feed'],
                min_age_months=rec_data['min_age'],
                max_age_months=rec_data['max_age'],
                min_weight_kg=rec_data['min_weight'],
                max_weight_kg=rec_data['max_weight'],
                purpose=rec_data['purpose'],
                defaults={
                    'daily_amount_kg': rec_data['amount'],
                    'feeding_frequency': rec_data['frequency']
                }
            )
            
            if created:
                self.stdout.write(f'Created feeding recommendation: {rec_data["animal"].name} - {rec_data["feed"].name}')

    def create_diseases_and_symptoms(self):
        # Create diseases
        diseases_data = [
            {
                'name': 'Foot and Mouth Disease',
                'description': 'Highly contagious viral disease affecting cloven-hoofed animals',
                'animals': ['Cattle', 'Goats', 'Sheep'],
                'severity': 'CRITICAL',
                'contagious': True,
                'vet_required': True,
                'prevention': 'Vaccination, quarantine new animals, proper sanitation',
                'treatment': 'Supportive care, isolation, veterinary supervision'
            },
            {
                'name': 'Mastitis',
                'description': 'Inflammation of the mammary gland, common in dairy animals',
                'animals': ['Cattle', 'Goats', 'Sheep'],
                'severity': 'MEDIUM',
                'contagious': False,
                'vet_required': True,
                'prevention': 'Proper milking hygiene, dry cow treatment',
                'treatment': 'Antibiotics, anti-inflammatory drugs, improved hygiene'
            },
            {
                'name': 'Newcastle Disease',
                'description': 'Viral disease affecting poultry respiratory and nervous systems',
                'animals': ['Poultry'],
                'severity': 'HIGH',
                'contagious': True,
                'vet_required': True,
                'prevention': 'Vaccination, biosecurity measures',
                'treatment': 'Supportive care, isolation of affected birds'
            },
            {
                'name': 'Parasitic Worms',
                'description': 'Internal parasites affecting digestive system',
                'animals': ['Cattle', 'Goats', 'Sheep'],
                'severity': 'MEDIUM',
                'contagious': False,
                'vet_required': False,
                'prevention': 'Regular deworming, pasture rotation, fecal testing',
                'treatment': 'Anthelmintic medications, improved nutrition'
            },
            {
                'name': 'Coccidiosis',
                'description': 'Parasitic disease affecting the intestinal tract',
                'animals': ['Poultry', 'Goats', 'Sheep'],
                'severity': 'MEDIUM',
                'contagious': True,
                'vet_required': False,
                'prevention': 'Clean water, dry bedding, proper sanitation',
                'treatment': 'Anticoccidial drugs, supportive care'
            }
        ]
        
        created_diseases = {}
        for disease_data in diseases_data:
            disease, created = Disease.objects.get_or_create(
                name=disease_data['name'],
                defaults={
                    'description': disease_data['description'],
                    'severity': disease_data['severity'],
                    'is_contagious': disease_data['contagious'],
                    'vet_required': disease_data['vet_required'],
                    'prevention_measures': disease_data['prevention'],
                    'treatment_advice': disease_data['treatment']
                }
            )
            
            if created:
                # Add affected animals
                animal_types = AnimalType.objects.filter(name__in=disease_data['animals'])
                disease.affected_animals.set(animal_types)
                created_diseases[disease_data['name']] = disease
                self.stdout.write(f'Created disease: {disease.name}')
        
        # Create symptoms
        symptoms_data = [
            {'name': 'Fever', 'diseases': ['Foot and Mouth Disease', 'Newcastle Disease']},
            {'name': 'Loss of Appetite', 'diseases': ['Foot and Mouth Disease', 'Newcastle Disease', 'Parasitic Worms', 'Coccidiosis']},
            {'name': 'Lameness', 'diseases': ['Foot and Mouth Disease']},
            {'name': 'Blisters on mouth/feet', 'diseases': ['Foot and Mouth Disease']},
            {'name': 'Swollen udder', 'diseases': ['Mastitis']},
            {'name': 'Abnormal milk', 'diseases': ['Mastitis']},
            {'name': 'Respiratory distress', 'diseases': ['Newcastle Disease']},
            {'name': 'Diarrhea', 'diseases': ['Parasitic Worms', 'Coccidiosis']},
            {'name': 'Weight loss', 'diseases': ['Parasitic Worms', 'Coccidiosis']},
            {'name': 'Pale mucous membranes', 'diseases': ['Parasitic Worms']},
            {'name': 'Blood in droppings', 'diseases': ['Coccidiosis']},
            {'name': 'Sudden death', 'diseases': ['Newcastle Disease', 'Coccidiosis']},
        ]
        
        for symptom_data in symptoms_data:
            symptom, created = Symptom.objects.get_or_create(
                name=symptom_data['name']
            )
            
            if created:
                # Link to diseases
                related_diseases = Disease.objects.filter(name__in=symptom_data['diseases'])
                symptom.diseases.set(related_diseases)
                self.stdout.write(f'Created symptom: {symptom.name}')

    def create_market_prices(self):
        # Create sample market prices for the last 30 days
        base_date = date.today() - timedelta(days=30)
        
        animal_types = AnimalType.objects.all()
        locations = ['Local Market', 'Regional Market', 'Premium Market']
        
        base_prices = {
            'Cattle': 4.50,
            'Goats': 6.00,
            'Sheep': 5.25,
            'Poultry': 8.50
        }
        
        for animal_type in animal_types:
            base_price = base_prices.get(animal_type.name, 5.00)
            
            for i in range(0, 30, 5):  # Every 5 days
                price_date = base_date + timedelta(days=i)
                
                for location in locations:
                    # Add some price variation
                    import random
                    price_variation = random.uniform(0.8, 1.2)
                    location_multiplier = 1.0
                    
                    if location == 'Premium Market':
                        location_multiplier = 1.15
                    elif location == 'Regional Market':
                        location_multiplier = 1.05
                    
                    price = round(base_price * price_variation * location_multiplier, 2)
                    
                    market_price, created = MarketPrice.objects.get_or_create(
                        animal_type=animal_type,
                        location=location,
                        date_recorded=price_date,
                        defaults={
                            'price_per_kg': price,
                            'quality_grade': 'GOOD',
                            'source': 'Sample Data'
                        }
                    )
                    
                    if created:
                        self.stdout.write(f'Created market price: {animal_type.name} - {location} - ${price}/kg')
