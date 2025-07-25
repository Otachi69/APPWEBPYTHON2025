from mongoengine import Document, StringField

class Regional(Document):
    nombre_regional = StringField(required=True, unique=True)
    meta = {'collection': 'regionales'}

class ProgramaFormacion(Document):
    nombre_programa = StringField(required=True, unique=True)
    meta = {'collection': 'programas_formacion'}
