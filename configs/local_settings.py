import os

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
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

##############################################################################
# SELF REGISTRATION
##############################################################################

ACCOUNT_ACTIVATION_DAYS = 7
REGISTRATION_OPEN=True


