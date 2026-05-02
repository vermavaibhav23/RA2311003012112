SECRET_KEY = 'campus-notification-secret-2024'
DEBUG = True
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'api',
]

ROOT_URLCONF = 'notificationapp.urls'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'notifications.db',
    }
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
