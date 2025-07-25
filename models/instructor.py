from mongoengine import Document, StringField, EmailField, ReferenceField
from flask_login import UserMixin
from .shared import Regional

class Instructor(UserMixin, Document):
    nombre_completo = StringField(required=True)
    correo_electronico = EmailField(required=True, unique=True)
    regional = ReferenceField(Regional, required=True)
    usuario = StringField(required=True, unique=True)
    contrasena = StringField(required=True)
    meta = {'collection': 'instructores'}

    def get_id(self):
        return str(self.id)
