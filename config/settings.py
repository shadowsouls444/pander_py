"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PROYECTO PANDER — Configuración SQL Server + Migraciones
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 
ESTRUCTURA DE APPS:
  pander/
  ├── manage.py
  ├── pander/
  │   ├── settings.py
  │   └── urls.py
  ├── empresa/        models.py  → compania, unidad_org
  ├── acceso/         models.py  → rol, modulo, rol_modulo, analista, usuario
  ├── vacantes/       models.py  → estado_vacante, tipo_contrato, vacante
  ├── candidatos/     models.py  → tipo_documento, candidato, datos_candidato,
  │                                 anexo_candidato, estado_postulacion,
  │                                 postulacion, postulacion_token
  └── evaluacion/     models.py  → habilidad, pregunta, respuesta, control_uso,
                                    evaluacion, evaluacion_habilidad,
                                    evaluacion_vacante, estado_intento,
                                    intento, respuesta_candidato,
                                    historial_habilidad_estim
"""

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-1ac%t3mp=d43@w5z_jbu(x%!drjg1x(ykqz()mf!6712we@_mg'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'apps.acceso',
    'apps.empresa',
    'apps.vacantes',
    'apps.candidatos',
    'apps.evaluacion',
    'corsheaders',
    'rest_framework'
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

DATABASES = {
    
    ## SQLite
    #'default': {
    #    'ENGINE': 'django.db.backends.sqlite3',
    #    'NAME': BASE_DIR / 'db.sqlite3'
    #}
    
    ## SQL Server
    #'default': {
    #    'ENGINE': 'mssql',
    #    'NAME': 'pander_db',
    #    'HOST': 'JOHANPORTA01\SQLEXPRESS',
    #    'PORT': '',
    #    'OPTIONS': {
    #        'driver': 'ODBC Driver 18 for SQL Server',
    #        'trusted_connection': 'yes',
    #        'extra_params': 'TrustServerCertificate=yes'
    #    }
    #}

    ## PostgreSQL
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'pander_db',
        'USER': 'postgres',
        'PASSWORD': 'Admin1234*',
        'HOST': 'localhost',
        'PORT': '5433',
    }
    
}

# ── URL base del frontend (para generar enlaces de evaluación) ─
FRONTEND_URL = 'http://localhost:5173'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ── Archivos subidos (CV candidatos) ──────────────────────────
MEDIA_URL  = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ── CORS ──────────────────────────────────────────────────────
CORS_ALLOW_ALL_ORIGINS = True   # Solo desarrollo. En producción usar CORS_ALLOWED_ORIGINS

EMAIL_BACKEND      = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST         = 'smtp.gmail.com'
EMAIL_PORT         = 587
EMAIL_USE_TLS      = True
EMAIL_USE_SSL      = False
EMAIL_HOST_USER    = 'johan.ramirez.beltran@gmail.com'
EMAIL_HOST_PASSWORD = 'dbdc ejgg mmzu uggl'
DEFAULT_FROM_EMAIL = 'Pander Notificaciones <johan.ramirez.beltran@gmail.com>'

# ── DRF ───────────────────────────────────────────────────────
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.MultiPartParser',   # ← para subida de archivos
        'rest_framework.parsers.FormParser',
    ],
}

# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = 'static/'
