# Django settings for detourmaps project.
import os
from os.path import dirname
import django.template
django.template.add_to_builtins('django.templatetags.future')
basedir = dirname(__file__)

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
# ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'dev_geo_detour', # Or path to database file if using sqlite3.
        'USER': 'postgres', # Not used with sqlite3.
        'PASSWORD': '04718802', # Not used with sqlite3.
        'HOST': 'localhost', # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '5432', # Set to empty string for default. Not used with sqlite3.
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = '%s/media/' % basedir

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = '/home/detourmaps/community/static/'

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
#ADMIN_MEDIA_PREFIX = '/static/admin/'

#admin tools set
#ADMIN_TOOLS_INDEX_DASHBOARD = 'detourmaps.dashboard.CustomIndexDashboard'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    '%s/community/static/' % basedir,
    '%s/web/static/' % basedir,
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    #    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'x(%f2%ul_*u=d9)kk76k295nrthos3pkg!bkt%yqah=del&ufh'

TEMPLATE_CONTEXT_PROCESSORS = (
    # default template context processors
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'community.context_processors.settings',

    # django 1.2 only
    #'django.contrib.messages.context_processors.messages',

    # required by django-admin-tools
    'django.core.context_processors.request',
)

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    #     'django.template.loaders.eggs.Loader',
)

THUMBNAIL_EXTENSION = 'png'
THUMBNAIL_TRANSPARENCY_EXTENSION = 'png'

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = ('%s/templates/' % basedir,)

INSTALLED_APPS = (
    'admin_tools',
    'admin_tools.theming',
    'admin_tools.menu',
    'admin_tools.dashboard',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',
    'easy_thumbnails',
    #'admin_tools.theming',
    #'admin_tools.menu',
    #'admin_tools.dashboard',
    'community',
    'web',
    'django.contrib.admin',
    'localflavor'
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

#AUTH_PROFILE_MODULE = 'web.UserProfile'

#only for a action in register business 'publisg register business'
GOOGLE_MAPS_API_KEY = 'ABQIAAAAMRdj9lILtQvXkiEUNZPsEBTVYn4XUlNVbaXmPTyyPkab5qqNZRQXIeTJetmIkh3Bi3s3lm0489i9hg'

GEOS_LIBRARY_PATH = '/usr/local/lib/libgeos_c.so'
#GEOS_LIBRARY_PATH='c:\Python27\DLLs\geos_c.dll'
GDAL_LIBRARY_PATH = '/usr/local/lib/libgdal.so'
#GDAL_DATA='C:\OSGeo4W\share\gdal'
#EMAIL_USE_TLS = True
#EMAIL_HOST = 'smtp.gmail.com'
#EMAIL_HOST_USER = 'cs.detourmaps@gmail.com'
#EMAIL_HOST_PASSWORD = 'detour6463'
#EMAIL_PORT = 587
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_HOST_USER = 'detourmaps'
EMAIL_HOST_PASSWORD = '04718802'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

FACEBOOK_APP_ID = "540480642657288"
FACEBOOK_APP_SECRET = "8b78af3f834230b2a40ad7dd6e981a14"
FACEBOOK_REDIRECT_URI = "http://detourmaps.com/communities/loginUser/"

#settings Twitter oAuth
CONSUMER_KEY = 'FgpSGwxZL1eapBqUNMmg'
CONSUMER_SECRET = 'bUFhudjFJaXhWYvhOA6Q2PpYqB5FSrXFxJ4yiXDyw'
REQUEST_TOKEN_URL = 'https://api.twitter.com/oauth/request_token'
AUTHENTICATE_URL = "https://api.twitter.com/oauth/authenticate?oauth_token="
ACCESS_TOKEN_URL = "https://api.twitter.com/oauth/access_token"

TWITTER_REDIRECT_URL = 'http://detourmaps.com/communities/loginUser/'
ACCESS_TOKEN = '102799398-NxV01tbTqfx8nXJbGTmBgSThyaRG0asAtZzYX2yj'
ACCESS_TOKEN_SECRET = 'VkdzWaq37X9a73Qs3MmwkOC84Uf8HlGD5uaj1zfGT8'

AUTHORIZE_URL = 'https://api.twitter.com/oauth/authorize'
OAUTH_TOKEN = '1301570935-EyodbGPYng21DIJTVRe5uIfX92IH5DwMCnaltRj'
OAUTH_SIGNATURE = 'H3RjEtsBaV8J30tvr2G0CbWoac8%3D'


#settings Google oauth
GOOGLE_CLIENT_ID = "532813113917-t1fpu1n46412c7bves9ompkgbucsejtm.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "MqwIM6VHlkYGwIOpLlkbiCYI"
