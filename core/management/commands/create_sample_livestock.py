from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from datetime import date, timedelta
from core.models import AnimalType, Breed, Livestock, FarmerProfile


class Command(BaseCommand):
    help = 'Create sample livestock for existing users'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='Create livestock for specific username only',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing sample livestock before creating new ones',
        )

    def handle(self, *args, **options):
        username = options.get('username')
        clear_existing = options.get('clear', False)
        
        self.stdout.write(self.style.SUCCESS('Creating sample livestock...'))
        
        # Get users
        if username:
            try:
                users = [User.objects.get(username=username)]
                self.stdout.write(f'Creating livestock for user: {username}')
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'User "{username}" not found'))
                return
        else:
            users = User.objects.all()
            if not users.exists():
                self.stdout.write(self.style.ERROR('No users found in the system'))
                return
        
        # Clear existing sample livestock if requested
        if clear_existing:
            deleted_count = Livestock.objects.filter(
                notes__contains='Sample livestock created for testing'
            ).delete()[0]
            self.stdout.write(f'Deleted {deleted_count} existing sample livestock')
        
        # Check if required data exists
        if not self.check_required_data():
            self.stdout.write(
                self.style.ERROR(
                    'Required animal types and breeds not found. '
                    'Please run "python manage.py seed_data" first.'
                )
            )
            return
        
        # Create livestock for users
        for user in users:
            self.create_livestock_for_user(user)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Sample livestock creation completed for {len(users)} user(s)!'
            )
        )

    def check_required_data(self):
        """Check if required animal types and breeds exist"""
        required_animals = ['Cattle', 'Goats', 'Sheep', 'Poultry']
        required_breeds = ['Holstein', 'Angus', 'Boer', 'Nubian', 'Dorper', 'Rhode Island Red']
        
        existing_animals = AnimalType.objects.filter(name__in=required_animals).count()
        existing_breeds = Breed.objects.filter(name__in=required_breeds).count()
        
        return existing_animals >= 4 and existing_breeds >= 6

    def create_livestock_for_user(self, user):
        """Create sample livestock for a specific user"""
        
        # Create farmer profile if it doesn't exist
        farmer_profile, profile_created = FarmerProfile.objects.get_or_create(
            user=user,
            defaults={
                'location': 'Sample Farm Location',
                'farm_size_acres': 50.0,
                'experience_years': 5
            }
        )
        
        if profile_created:
            self.stdout.write(f'Created farmer profile for: {user.username}')
        
        # Get animal types and breeds
        try:
            cattle = AnimalType.objects.get(name='Cattle')
            goats = AnimalType.objects.get(name='Goats')
            sheep = AnimalType.objects.get(name='Sheep')
            poultry = AnimalType.objects.get(name='Poultry')
            
            holstein = Breed.objects.get(name='Holstein', animal_type=cattle)
            angus = Breed.objects.get(name='Angus', animal_type=cattle)
            boer = Breed.objects.get(name='Boer', animal_type=goats)
            nubian = Breed.objects.get(name='Nubian', animal_type=goats)
            dorper = Breed.objects.get(name='Dorper', animal_type=sheep)
            rhode_island = Breed.objects.get(name='Rhode Island Red', animal_type=poultry)
        except (AnimalType.DoesNotExist, Breed.DoesNotExist) as e:
            self.stdout.write(self.style.ERROR(f'Required data not found: {e}'))
            return
        
        # Sample livestock data
        sample_livestock = [
            # Cattle
            {
                'animal_type': cattle, 'breed': holstein, 'tag_number': 'C001', 
                'name': 'Bessie', 'gender': 'F', 'purpose': 'MILK', 
                'weight': 450, 'age_days': 720, 'purchase_price': 1200
            },
            {
                'animal_type': cattle, 'breed': angus, 'tag_number': 'C002', 
                'name': 'Thunder', 'gender': 'M', 'purpose': 'MEAT', 
                'weight': 380, 'age_days': 540, 'purchase_price': 900
            },
            {
                'animal_type': cattle, 'breed': holstein, 'tag_number': 'C003', 
                'name': 'Daisy', 'gender': 'F', 'purpose': 'MILK', 
                'weight': 420, 'age_days': 650, 'purchase_price': 1100
            },
            
            # Goats
            {
                'animal_type': goats, 'breed': boer, 'tag_number': 'G001', 
                'name': 'Billy', 'gender': 'M', 'purpose': 'MEAT', 
                'weight': 45, 'age_days': 365, 'purchase_price': 150
            },
            {
                'animal_type': goats, 'breed': nubian, 'tag_number': 'G002', 
                'name': 'Nanny', 'gender': 'F', 'purpose': 'MILK', 
                'weight': 55, 'age_days': 450, 'purchase_price': 200
            },
            {
                'animal_type': goats, 'breed': boer, 'tag_number': 'G003', 
                'name': 'Kid', 'gender': 'F', 'purpose': 'BREEDING', 
                'weight': 35, 'age_days': 240, 'purchase_price': 180
            },
            
            # Sheep
            {
                'animal_type': sheep, 'breed': dorper, 'tag_number': 'S001', 
                'name': 'Woolly', 'gender': 'F', 'purpose': 'MEAT', 
                'weight': 60, 'age_days': 300, 'purchase_price': 120
            },
            {
                'animal_type': sheep, 'breed': dorper, 'tag_number': 'S002', 
                'name': 'Ram', 'gender': 'M', 'purpose': 'BREEDING', 
                'weight': 75, 'age_days': 600, 'purchase_price': 200
            },
            
            # Poultry
            {
                'animal_type': poultry, 'breed': rhode_island, 'tag_number': 'P001', 
                'name': 'Henrietta', 'gender': 'F', 'purpose': 'EGGS', 
                'weight': 2.2, 'age_days': 120, 'purchase_price': 15
            },
            {
                'animal_type': poultry, 'breed': rhode_island, 'tag_number': 'P002', 
                'name': 'Rooster', 'gender': 'M', 'purpose': 'BREEDING', 
                'weight': 3.0, 'age_days': 180, 'purchase_price': 25
            },
        ]
        
        created_count = 0
        
        for livestock_data in sample_livestock:
            # Make tag number unique per user
            unique_tag = f"{user.id}_{livestock_data['tag_number']}"
            
            # Skip if livestock with this tag already exists for this user
            if Livestock.objects.filter(farmer=user, tag_number=unique_tag).exists():
                continue
            
            # Calculate birth date
            birth_date = date.today() - timedelta(days=livestock_data['age_days'])
            purchase_date = birth_date + timedelta(days=30)  # Assume purchased 30 days after birth
            
            livestock = Livestock.objects.create(
                farmer=user,
                animal_type=livestock_data['animal_type'],
                breed=livestock_data['breed'],
                tag_number=unique_tag,
                name=livestock_data['name'],
                gender=livestock_data['gender'],
                date_of_birth=birth_date,
                current_weight_kg=livestock_data['weight'],
                purpose=livestock_data['purpose'],
                status='HEALTHY',
                purchase_date=purchase_date,
                purchase_price=livestock_data['purchase_price'],
                notes=f'Sample livestock created for testing - {livestock_data["name"]}'
            )
            
            created_count += 1
            self.stdout.write(f'Created livestock for {user.username}: {livestock.name} ({livestock.tag_number})')
        
        if created_count == 0:
            self.stdout.write(f'No new livestock created for {user.username} (all already exist)')
        else:
            self.stdout.write(self.style.SUCCESS(f'Created {created_count} livestock for {user.username}'))
