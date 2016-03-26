import os

basedir = os.path.abspath(os.path.dirname(__file__))

CSRF_ENABLED = True
SECRET_KEY = 'XWj7m6I6AY3DaMaPWHUnwtjK3NCz48Vqv8AKCGZra12F9TnSACBaRgPZ7vG40dru'

PASSWORD_LENGTH = 8

if os.environ.get('DATABASE_URL') is not None: #Production environment
    ENVIRONMENT_TYPE = 'PRODUCTION'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
else: #Local environemtn
    ENVIRONMENT_TYPE = 'DEBUG'
    SQLALCHEMY_DATABASE_URI = 'postgresql://bgame:bgame@localhost/bgame'

