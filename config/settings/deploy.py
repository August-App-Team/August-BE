from .base import *

DEBUG = False

ALLOWED_HOSTS = [
    '.augustapp.one',
    '127.0.0.1',
]

DEPLOY_DB_NAME = get_secret('DEPLOY_DB_NAME')
DEPLOY_DB_USER = get_secret('DEPLOY_DB_USER')
DEPLOY_DB_PASSWORD = get_secret('DEPLOY_DB_PASSWORD')
DEPLOY_DB_HOST = get_secret('DEPLOY_DB_HOST')
DEPLOY_DB_PORT = get_secret('DEPLOY_DB_PORT')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': DEPLOY_DB_NAME,
        'USER': DEPLOY_DB_USER,
        'PASSWORD': DEPLOY_DB_PASSWORD,
        'HOST': DEPLOY_DB_HOST,
        'PORT': DEPLOY_DB_PORT,
    }
}

STORAGES = {
    'default' : {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "location": "media",
        }
    },
    'staticfiles': {
        "BACKEND": "storages.backends.s3.S3Storage",
    }
}
AWS_STORAGE_BUCKET_NAME = get_secret('AWS_STORAGE_BUCKET_NAME')
AWS_S3_FILE_OVERWRITE = False
AWS_IS_GZIPPED = True
AWS_S3_REGION_NAME = 'us-east-1'
AWS_S3_ACCESS_KEY_ID = get_secret('AWS_S3_ACCESS_KEY_ID')
AWS_S3_SECRET_ACCESS_KEY = get_secret('AWS_S3_SECRET_ACCESS_KEY')
AWS_QUERYSTRING_AUTH = False

DJANGO_APPS += [
    'django.contrib.staticfiles'
]

THIRD_PARTY_APPS += [
    'storages',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

CSRF_TRUSTED_ORIGINS = [
    'https://augustapp.one',
]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "https://augustapp.one",
]

CORS_ALLOW_CREDENTIALS = True