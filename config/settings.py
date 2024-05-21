"""
Django settings for config project.

Generated by 'django-admin startproject' using Django 4.2.8.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path
from environs import Env

env = Env()
env.read_env()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("DJANGO_SECRET_KEY")
SECURE_SSL_REDIRECT = env.bool("DJANGO_SECURE_SSL_REDIRECT", default=False)

# HSTS
SECURE_HSTS_SECONDS = env.int("DJANGO_SECURE_HSTS_SECONDS", default=2592000)
SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool("DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS", default=True)
SECURE_HSTS_PRELOAD = env.bool("DJANGO_SECURE_HSTS_PRELOAD", default=True)

# https-, secure-cookie
SESSION_COOKIE_SECURE = env.bool("DJANGO_SESSION_COOKIE_SECURE", default=True)
CSRF_COOKIE_SECURE = env.bool("DJANGO_CSRF_COOKIE_SECURE", default=True)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool("DJANGO_DEBUG", False)
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'webapp']

# для добавления локалхоста и ip хоста в список доверенных хостов - 
# чтобы посредник csrf не ругался. Добавлять также домен или ip того хоста, на котором будет крутиться сайт
# приходит строка с ip и хостами, разделенными запятыми - кривой docker-compose не передает нормально списки
CSRF_TRUSTED_ORIGINS=[]
csrf_trusted_hosts = env("CSRF_TRUSTED_HOSTS").split(",")
for host in csrf_trusted_hosts:
    CSRF_TRUSTED_ORIGINS.append("http://" + host)
    CSRF_TRUSTED_ORIGINS.append("https://" + host)
print("CSRF_TRUSTED_ORIGINS", CSRF_TRUSTED_ORIGINS)


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    # Third-party
    # 'crispy_forms',
    # 'crispy_bootstrap4',
    'allauth',
    'allauth.account',
    # 'debug_toolbar',

    # local
    'users',
    'pages',
    'dbeve_universe',
    'dbeve_social',
    'dbeve_items',
    'requests_to_esi',
    'compensation',
]

MIDDLEWARE = [
    # 'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'allauth.account.middleware.AccountMiddleware',
    # 'debug_toolbar.middleware.DebugToolbarMiddleware',

    # 'django.middleware.cache.FetchFromCacheMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [str(BASE_DIR.joinpath('templates')),],
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

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'postgres',
            'USER': 'postgres',
            'PASSWORD': 'postgres',
            'HOST': 'db',
            'PORT': 5432,
          }
    # 'default': env.dj_db_url("DATABASE_URL", default="postgres://postgres@db/postgres")

}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

# LANGUAGE_CODE = 'en-us'
LANGUAGE_CODE = 'ru'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = '/staticfiles/'
# STATICFILES_DIRS = (str(BASE_DIR.joinpath('static')),)
STATICFILES_DIRS = (BASE_DIR.joinpath('static'),)
# STATIC_ROOT = str(BASE_DIR.joinpath('staticfiles'))
STATIC_ROOT = BASE_DIR.joinpath('staticfiles')
STATICFILES_FINDERS = [
        "django.contrib.staticfiles.finders.FileSystemFinder",
        "django.contrib.staticfiles.finders.AppDirectoriesFinder",
        ]

MEDIA_URL = '/media/'
# MEDIA_ROOT = str(BASE_DIR.joinpath("media"))
MEDIA_ROOT = BASE_DIR.joinpath("media")

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'users.CustomUser'

LOGIN_REDIRECT_URL = "home"

CRISPY_TEMPLATE_PACK = 'bootstrap4'

## django-allauth config
SITE_ID = 1
AUTHENTICATION_BACKENDS = (
        # 'django.contrib.auth.backends.ModelBackend',
        'allauth.account.auth_backends.AuthenticationBackend',
        )
# за перенаправление при логоуте теперь отвечает allauth, перенаправление при логине - по умолчанию
ACCOUNT_LOGOUT_REDIRECT = "home"
# автозапоминание входа без простановки чекбоксов
ACCOUNT_SESSION_REMEMBER = True
# не требуется два раза вводить пароль при регистрации
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = False
# настройки для аутентификации по email
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True

# почтовый адрес сайта
DEFAULT_FROM_EMAIL = "admin@some_django_site.com"

# временный вывод писем в консоль
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
# теперь нормальная регистрация по почте
# EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
# EMAIL_HOST = "smtp.gmail.com"
# EMAIL_PORT = 587
# EMAIL_HOST_USER = env("DJANGO_EMAIL_HOST_USER")
# EMAIL_HOST_PASSWORD = env("DJANGO_EMAIL_HOST_PASSWORD")
# EMAIL_USE_TLS = True


# django-debug-toolbar, ip to network Docker
import socket
hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
INTERNAL_IPS = [ip[:-1] + "1" for ip in ips]


# settings cache
# CACHE_MIDDLEWARE_ALIAS = 'default'
# CACHE_MIDDLEWARE_SECONDS = 6000
# CACHE_MIDDLEWARE_SECONDS = 5
# CACHE_MIDDLEWARE_KEY_PREFIX = ''
