# Django LMS - Learning Management System

A simple, clean, and professional Learning Management System built with Django.

## Features

- **Authentication**: User registration, login, logout, profile management
- **Roles**: Admin, Instructor, Student
- **Course Management**: Categories, courses with lessons
- **Lesson Tracking**: Mark lessons complete, track progress
- **Certificates**: Download PDF certificates on course completion
- **Enrollment**: Free and paid course enrollment
- **Shopping Cart**: Add multiple courses to cart
- **Payment**: SSLCommerz integration for Bangladesh
- **API**: REST API with DRF for programmatic access
- **Responsive UI**: Clean design with Tailwind CSS + Dark Mode

## Tech Stack

- Django 4.2
- Django REST Framework
- SQLite
- Tailwind CSS (CDN)
- SSLCommerz Payment Gateway
- Chart.js (for progress charts)
- WeasyPrint (for PDF certificates)

## Quick Start (Local Development)

### 1. Clone and Setup Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file with your settings:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
SSLCOMMERZ_STORE_ID=your_store_id
SSLCOMMERZ_STORE_PASSWORD=your_store_password
SSLCOMMERZ_SANDBOX=True
BASE_URL=http://localhost:8000
```

### 3. Run Migrations

```bash
python manage.py migrate
```

### 4. Create Superuser

```bash
python manage.py createsuperuser
```

### 5. Run Development Server

```bash
python manage.py runserver
```

Visit `http://localhost:8000` in your browser.

## Deployment to PythonAnywhere

### Step 1: Upload Code
Upload your project to PythonAnywhere via:
- Git clone: `git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git`
- Or manual file upload

### Step 2: Set Up Virtual Environment

```bash
cd ~/lms_ai
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 3: Configure Environment

Create `.env` file:
```bash
nano .env
```

```env
SECRET_KEY=generate-a-secure-random-key
DEBUG=False
SSLCOMMERZ_STORE_ID=your_store_id
SSLCOMMERZ_STORE_PASSWORD=your_password
SSLCOMMERZ_SANDBOX=True
BASE_URL=https://yourusername.pythonanywhere.com
```

### Step 4: Run Migrations & Collect Static Files

```bash
python manage.py migrate
python manage.py collectstatic
python manage.py createsuperuser
```

### Step 5: Configure WSGI File

Go to **Web** tab → Edit WSGI configuration file:

```python
import os
import sys

path = '/home/YOUR_USERNAME/lms_ai'
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'lms_ai.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

### Step 6: Configure Static Files

In the **Web** tab, add static files:
- URL: `/static/` → Directory: `/home/YOUR_USERNAME/lms_ai/staticfiles`
- URL: `/media/` → Directory: `/home/YOUR_USERNAME/lms_ai/media`

### Step 7: Reload Web App

Click the **Reload Web App** button.

---

## SSLCommerz Setup

### Sandbox Mode (Testing)

1. Register at [SSLCommerz Sandbox](https://sandbox.sslcommerz.com/)
2. Get your Store ID and Store Password
3. Set in `.env`:
   ```
   SSLCOMMERZ_SANDBOX=True
   SSLCOMMERZ_STORE_ID=test
   SSLCOMMERZ_STORE_PASSWORD=qwerty
   ```

### Production Mode

1. Register at [SSLCommerz](https://www.sslcommerz.com/)
2. Get your Store ID and Store Password
3. Set in `.env`:
   ```
   SSLCOMMERZ_SANDBOX=False
   SSLCOMMERZ_STORE_ID=your_real_store_id
   SSLCOMMERZ_STORE_PASSWORD=your_real_password
   ```

## API Endpoints

### Authentication
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/register/` | POST | Register new user |
| `/api/auth/login/` | POST | Login and get token |

### Profile
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/profile/` | GET/PUT | Get or update profile |

### Courses
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/courses/` | GET | List all published courses |
| `/api/courses/<slug>/` | GET | Course details |
| `/api/courses/<id>/lessons/` | GET | Lessons for a course |
| `/api/courses/<id>/enroll/` | POST | Enroll in free course |

### My Courses
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/my-courses/` | GET | User's enrolled courses |

### Payments
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/payments/<transaction_id>/status/` | GET | Payment status |

### Categories
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/categories/` | GET | List all categories |

### API Authentication

For authenticated requests, include the token:
```
Authorization: Token your-token-here
```

## Instructor Guide

### Becoming an Instructor

1. Log into admin panel at `/admin/`
2. Go to **Profiles**
3. Edit your profile and change role to "instructor"

### Creating a Course

1. Go to **Instructor Panel** from the navbar
2. Click **Create Course**
3. Fill in course details:
   - Title, Category, Description
   - Price (or mark as free)
   - Thumbnail image
   - Publish when ready
4. Add lessons to your course
5. Students can now enroll and learn!

## Student Guide

### Enrolling in Courses

1. Browse courses at `/courses/`
2. Click on a course to view details
3. For free courses: Click "Enroll for Free"
4. For paid courses: Add to cart or buy directly

### Learning

1. Go to **My Courses** from navbar
2. Click on a course to start learning
3. Mark lessons as complete
4. Download certificate when all lessons are done

## Project Structure

```
lms_ai/
├── lms_ai/          # Django project settings
├── accounts/         # User authentication and profiles
├── courses/          # Course, lesson, enrollment models
├── payments/         # SSLCommerz payment integration
├── cart/             # Shopping cart functionality
├── api/              # REST API endpoints
├── core/             # Home and dashboard views
├── templates/        # HTML templates
├── requirements.txt
├── .env.example
└── deploy.sh
```

## Testing

```bash
python manage.py test
```

## License

MIT License
# LMS_project
