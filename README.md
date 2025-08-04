# Livestock Management System

A web-based decision support system for small-scale livestock farmers, providing guidance on feeding, disease monitoring, and pricing for cattle, goats, sheep, and poultry.

## 🎯 Project Goal
Develop a minimal viable product (MVP) to support small-scale livestock farmers in critical decision-making areas for better livestock sustainability.

## 🚀 Sprint 1 - Project Foundation ✅

### Completed Features
- ✅ Django project setup with virtual environment
- ✅ SQLite database configuration
- ✅ Bootstrap 5 frontend with responsive design
- ✅ User authentication (login/register/logout)
- ✅ Swagger UI API documentation
- ✅ Basic project structure

### Tech Stack
- **Backend**: Django 5.2.4 with Django REST Framework
- **Database**: SQLite3
- **Frontend**: HTML, CSS, JavaScript with Bootstrap 5
- **API Documentation**: Swagger UI (drf-yasg)

### Installation & Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Livestock_Management
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv livestock_env
   livestock_env\Scripts\activate  # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**
   ```bash
   python manage.py migrate
   ```

5. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

6. **Start development server**
   ```bash
   python manage.py runserver
   ```

### 🔗 Key URLs
- **Homepage**: http://127.0.0.1:8000/
- **Admin Panel**: http://127.0.0.1:8000/admin/
- **API Documentation**: http://127.0.0.1:8000/api/swagger/
- **API Health Check**: http://127.0.0.1:8000/api/health/

### Default Credentials
- **Admin User**: admin / admin123

## 📋 Upcoming Sprints

### Sprint 2: Core Models & Database
- Design livestock, feed, disease, and pricing models
- Set up Django admin interface
- Seed database with initial data

### Sprint 3: Feeding Module
- Build feeding recommendation logic
- Create API endpoints
- Develop frontend interface

### Sprint 4: Disease Monitoring Module  
- Implement symptom checking logic
- Create disease monitoring APIs
- Build frontend for health tracking

### Sprint 5: Pricing Module
- Develop market pricing estimation
- Create pricing APIs
- Build pricing interface

### Sprint 6: Integration & Polish
- Integrate all modules
- End-to-end testing
- UI improvements and deployment

## 🏗️ Architecture

```
livestock_management/
├── accounts/           # User authentication
├── livestock_management/  # Main project settings
├── static/            # CSS, JS, images
├── templates/         # HTML templates
├── db.sqlite3         # SQLite database
└── manage.py          # Django management
```

## 📝 API Documentation

The project includes comprehensive API documentation available at `/api/swagger/` with interactive testing capabilities.

Current API endpoints:
- `GET /api/health/` - Check API health status
- `GET /api/system-info/` - Get system information

## 🧪 Testing

```bash
python manage.py test
python manage.py check
```
