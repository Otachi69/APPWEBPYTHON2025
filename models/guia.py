import datetime
from mongoengine import Document, StringField, DateTimeField, ReferenceField
from .instructor import Instructor
from .shared import ProgramaFormacion

class GuiaAprendizaje(Document):
    nombre_guia = StringField(required=True)
    descripcion = StringField(required=True)
    programa_formacion = ReferenceField(ProgramaFormacion, required=True)
    nombre_documento_pdf = StringField(required=True)
    fecha_publicacion = DateTimeField(default=datetime.datetime.now)
    instructor = ReferenceField(Instructor, required=True)
    meta = {'collection': 'guias_aprendizaje'}
