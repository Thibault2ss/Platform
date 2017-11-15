"""
Django settings for part_management project.

Generated by 'django-admin startproject' using Django 1.11.2.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'n^+xf77tb6$z2bp$)+nsng2in2#ummrfr)+&4agwf%#0f$xuz*'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = [
    'localhost',
    '192.168.0.112',
    "spare-part-3d.com",
    "www.spare-parts-3d.com",
    "hub.spare-parts-3d.com",
    "account.spare-parts-3d.com",
    "jb.spare-parts-3d.com",
    "digital.spare-parts-3d.com",
    'sp3d-cloud-env.hrfhveptmc.ap-southeast-1.elasticbeanstalk.com',
]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.sites',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.linkedin_oauth2',
    'address',
    'storages',

    'users',
    'notifications',
    'jb',
    'hub',
    'digital',
]
RESTRICTION_LIST = {
            'STAFF':[],
            'HUB':['/admin', '/jb', '/digital', '/inbox'],
            'CLIENT':['/admin', '/jb', '/hub', '/inbox']
            }
SITE_ID = 2

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'users.middleware.RestrictionMiddleware'
]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
    # 'sp3d.authBackends.jbAuthBackend'
    ]
# AUTHENTICATION_BACKENDS = ['django.contrib.auth.backends.ModelBackend', 'sp3d.authBackends.jbAuthBackend']

ROOT_URLCONF = 'sp3d.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR,'users', 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'sp3d.wsgi.application'

AUTH_USER_MODEL = 'users.CustomUser'
# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases


# ACTIVATE DB ROUTERS FOR SPECIAL DB ROUTING
# DATABASE_ROUTERS = ['sp3d.dbRouters.jbRouter']
if DEBUG:
    default_db = {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'SP3D_USERS',
        'USER': 'user01',
        'PASSWORD': 'SpareParts3D#',
        'HOST': '192.168.0.20',   # Or an IP Address that your DB is hosted on
        'PORT': '3306',
    }
else:
    default_db = {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'SP3D_CLOUD',
        'USER': 'sp3dadmin',
        'PASSWORD': 'SpareParts3D#',
        'HOST': 'sp3dclouddb.csgmjvodxypo.ap-southeast-1.rds.amazonaws.com',   # Or an IP Address that your DB is hosted on
        'PORT': '3306',
    }

DATABASES = {
# ACTIVATE THE DEFAULT DB BELOW FOR PROD
    'default':default_db,
# ACTIVATE ONLY IF SEPARATES DB AND ACTIVATE THE DB ROUTER
    # 'jb_db': {
    #     'ENGINE': 'django.db.backends.mysql',
    #     'NAME': 'SP3D_JB',
    #     'USER': 'user01',
    #     'PASSWORD': 'SpareParts3D#',
    #     'HOST': '192.168.0.20',   # Or an IP Address that your DB is hosted on
    #     'PORT': '3306',
    # },
}


# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# login redirection
# LOGIN_REDIRECT_URL = '/jb/'
LOGOUT_REDIRECT_URL = 'http://spare-parts-3d.com'
LOGIN_REDIRECT_URL_LIST = {'STAFF':'/jb/', 'HUB':'/hub/', 'CLIENT':'/digital/'}

LOGIN_URL = '/account/login/'

MEDIA_ROOT='/home/user01/SpareParts_Database/root/'
MEDIA_URL='/media/'
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT=os.path.join(BASE_DIR,'static/')
# Add these new lines
# STATICFILES_DIRS = (
#     os.path.join(BASE_DIR, 'users', 'static'),
# )
#
# STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
# STATICFILES_FINDERS = (
#     'django.contrib.staticfiles.finders.FileSystemFinder',
#     'django.contrib.staticfiles.finders.AppDirectoriesFinder',
# )

# NOTIFICATION APP
NOTIFICATIONS_USE_JSONFIELD=True
NOTIFICATIONS_SOFT_DELETE=True

# ALL AUTH APP
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True  # default already True
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = True # default already True
ACCOUNT_EMAIL_VERIFICATION = "optional" #default as "optional"
ACCOUNT_ADAPTER = "users.adapter.AccountAdapter"
ACCOUNT_FORMS = {'signup':'users.forms.SignupForm', 'login': 'users.forms.LoginForm'}
# ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
# LOGIN_ON_EMAIL_CONFIRMATION = False
# SOCIALACCOUNT_ADAPTER = "users.socialadapter.SocialAccountAdapter"
SOCIALACCOUNT_FORMS = {'signup':'users.forms.SocialSignupForm'}
SOCIALACCOUNT_AUTO_SIGNUP = False



# email backend setup
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'thibault.de-saint-sernin@sp3d.co'
EMAIL_HOST_PASSWORD = 'nwqxbhbipjiuoetb'

# GOOGLE MAPS
GOOGLE_API_KEY = 'AIzaSyDyZ4782IXg8US1yrhugnzFLrB6IIBsXmo'

############################################################################################################################################################
# STORAGE TO S3
# AWS S3 STORAGE
AWS_ACCESS_KEY_ID = 'AKIAJQUVRVZZ4ZTEA5OQ' # OR os.environ['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = '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'
AWS_STORAGE_BUCKET_NAME = 'sp3d-default'
AWS_S3_CUSTOM_DOMAIN = 's3-ap-southeast-1.amazonaws.com/%s' % AWS_STORAGE_BUCKET_NAME
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}


##################ACTIVATE THIS FOR PROD################
#if you want static files on S3:
# AWS_STATIC_LOCATION = 'static'
# STATICFILES_STORAGE = 'sp3d.storage_backends.StaticStorage'
# STATIC_URL = 'https://%s/%s/' % (AWS_S3_CUSTOM_DOMAIN, AWS_STATIC_LOCATION)

#############ACTIVATE THIS FOR PROD#####################
AWS_PUBLIC_MEDIA_LOCATION = 'media/public'
DEFAULT_FILE_STORAGE = 'sp3d.storage_backends.PublicMediaStorage'

AWS_PRIVATE_MEDIA_LOCATION = 'media/private'
PRIVATE_FILE_STORAGE = 'sp3d.storage_backends.PrivateMediaStorage'
AWS_QUERYSTRING_EXPIRE = 259200 #in seconds. 72h
#################################################################
FILE_UPLOAD_MAX_MEMORY_SIZE = 2621440
DATA_UPLOAD_MAX_MEMORY_SIZE = 2621440  #will raise suspicious error
# 2.5MB - 2621440
# 5MB - 5242880
# 10MB - 10485760
# 20MB - 20971520
# 50MB - 5242880
# 100MB 104857600
# 250MB - 214958080
# 500MB - 429916160
############################################################################################################################################################
