# SweetSpot API

Django REST API for SweetSpot - Delivering Delight to Your Doorstep

## TODO :
- [x] Streamlit UI Implementation
- [x] Google Maps Tracking
- [x] Email Notifications
- [x] Payment Page and Order Page
- [ ] Store Page with Auth Token

### API Documentation
- [Here](APIs.md)

### Screenshots

| Home Page | Cakes Collection | Cakes at Store | Login Page |
|-----------|------------------|----------------|------------|
| ![Home Page](screenshots/Home%20Page.png) | ![Cakes Collection](screenshots/Cakes%20Collection.png) | ![Cakes at Store](screenshots/Cakes%20at%20Store1.png) | ![Login](screenshots/Login.png) |

| Stores Page | Profile Page | Customize Cake | Checkout Page |
|-------------|-------------|----------------|--------------|
| ![Stores](screenshots/Stores.png) | ![Profile](screenshots/Profile.png) | ![Customize](screenshots/Customize.png) | ![Checkout](screenshots/Checkout.png) |

> _All screenshots are directly rendered from the `/screenshots` folder in this repository._

### Prerequisites

- Python 3.x
- PostgreSQL
- pip (Python package manager)

### Local Setup

#### 1. Clone the Repository

```bash
git clone -b Your repo
cd API-development-of-SweetSpot-Deliverin-Delight-to-Your-Doorstep_oct_2024
```

#### 2. Create and Activate Virtual Environment

For Linux/macOS:
```bash
python3 -m venv venv
source venv/bin/activate
```
For Windows:
```bash
python3 -m venv venv
venv\Scripts\activate
```

#### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

#### 4. Database and Email Configuration

1. Install and start PostgreSQL server
2. Create a new PostgreSQL database 
3. Update the database configuration in `sweetspot_pro/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres', #add your db name
        'USER': 'postgres', #add your db user
        'PASSWORD': 'password', #add your db password
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```
In the same `sweetspot_pro/settings.py` file add email config or leave in the defaults

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = #your email
EMAIL_HOST_PASSWORD = #your generated password
EMAIL_USE_SSL = False
```

#### 5. Run Migrations and create a super user

```bash
python3 manage.py makemigrations
python3 manage.py migrate
python manage.py createsuperuser
```
Go to `http://localhost:8000/admin` for adding sample data (like cakes)

#### 6. Start Development Server

```bash
python3 manage.py runserver 
```

The API will be available at `http://localhost:8000`

## API Documentation

- Swagger UI: `http://localhost:8000/docs/`
- ReDoc: `http://localhost:8000/redoc/`

## Requirements

Main dependencies:
- Django
- Django REST Framework
- psycopg2-binary
- drf-yasg (for Swagger/OpenAPI documentation)

For a complete list of dependencies, see `requirements.txt`

## Development

1. Create new models in `api/models.py`
2. Create serializers in `api/serializers.py`
3. Create views in `api/views.py`
4. Add URL patterns in `api/urls.py`

## License

This project is licensed under the MIT License - see the LICENSE file for details
