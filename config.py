import os

class Config:
    # Clave secreta para proteger sesiones y formularios
    SECRET_KEY = os.environ.get('SECRET_KEY')

    # Configuración de MongoDB Atlas para Flask-MongoEngine
    MONGODB_SETTINGS = {
        'host': os.environ.get('MONGO_URI')
    }

    # Configuración para Flask-Mail
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
