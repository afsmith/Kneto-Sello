import os

ADMINS = (
   ('Kneto Ooops', 'app@kneto.fi'),
)

MANAGERS = ADMINS

#
# Locale paths
#
LOCALE_PATHS = (
    os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'locale'),
)

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Helsinki'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '&g0g+yd74ynaz0%@3^amakt7jo-(4v*qovdadip4wz4=(y_&s)'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'plato_prod',
        'USER': 'plato_prod',
        'PASSWORD': 'XXXX',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

REPORTS_CONFIG='/opt/bls/plato/src/reports/engine/conf/engine.properties'
CKEDITOR_UPLOAD_WWW_PATH = 'http://192.168.0.109/media/uploaded-images/'
##############################################################################
# SELF REGISTRATION
##############################################################################

ACCOUNT_ACTIVATION_DAYS = 7
REGISTRATION_OPEN=False

##############################################################################
# SALES +
##############################################################################

SALES_PLUS = False 
ENABLE_MODULES_SIGNOFF = True 
STATUS_CHECKBOX=False

##############################################################################
# MAIL BOX (used in messages_custom.tasks.check_mailbox()) 
##############################################################################

EMAIL_BOX_TYPE = 'pop3'
EMAIL_BOX_HOST = 'mail1.sigmatic.fi'
EMAIL_BOX_PORT = 995
EMAIL_BOX_USER = ''
EMAIL_BOX_PASSWORD = 'gBQzrW1ULrFc'
EMAIL_BOX_SSL = True
EMAIL_BOX_IMAP_FOLDER = 'INBOX'
EMAIL_BOX_REMOVE_MESSAGES = True

##############################################################################
# SMTP Settings 
##############################################################################

EMAIL_BACKEND = 'djcelery_email.backends.CeleryEmailBackend'

EMAIL_HOST='mail1.sigmatic.fi'
EMAIL_HOST_USER=''
EMAIL_HOST_PASSWORD='gBQzrW1ULrFc'
DEFAULT_FROM_EMAIL=''
EMAIL_USE_TLS=True
EMAIL_CONTENT_SUBTYPE='html'
EMAIL_PORT = 587
