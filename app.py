import os
import random
import string
import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_mail import Mail, Message
from flask_mongoengine import MongoEngine
from config import Config

# Importar modelos desde models/
from models import Instructor, GuiaAprendizaje, Regional, ProgramaFormacion

# --- Configuración Inicial ---
app = Flask(__name__)
app.config.from_object(Config)

UPLOAD_FOLDER = './uploads/'
ALLOWED_EXTENSIONS = {'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

mail = Mail(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

db = MongoEngine(app)

# --- Callbacks de Login ---
@login_manager.user_loader
def load_user(user_id):
    return Instructor.objects(id=user_id).first()

# --- Funciones de Utilidad ---
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def precargar_datos_iniciales():
    print("Precargando datos iniciales...")
    regionales = [
        "Cauca", "Huila", "Antioquia", "Valle", "Nariño", "Cundinamarca",
        "Atlántico", "Santander", "Boyacá", "Risaralda"
    ]
    for nombre in regionales:
        if not Regional.objects(nombre_regional=nombre).first():
            Regional(nombre_regional=nombre).save()
            print(f"Regional '{nombre}' agregada.")

    programas = [
        "Desarrollo de Software", "Multimedia", "Inteligencia Artificial",
        "Analítica de Datos", "Construcción", "Contabilidad", "Diseño Gráfico",
        "Electrónica", "Mecánica Industrial"
    ]
    for nombre in programas:
        if not ProgramaFormacion.objects(nombre_programa=nombre).first():
            ProgramaFormacion(nombre_programa=nombre).save()
            print(f"Programa '{nombre}' agregado.")
    print("Datos precargados.")

with app.app_context():
    precargar_datos_iniciales()

# --- Rutas ---
@app.route('/')
def index():
    return redirect(url_for('dashboard') if current_user.is_authenticated else url_for('login'))

@app.route('/registro_instructor')
def mostrar_registro_instructor():
    regionales = Regional.objects()
    return render_template('registro_instructor.html', regionales=regionales)

@app.route('/registrar_instructor', methods=['POST'])
def registrar_instructor():
    nombre_completo = request.form['nombre_completo']
    correo_electronico = request.form['correo_electronico']
    regional_id = request.form['regional']

    if Instructor.objects(correo_electronico=correo_electronico).first():
        flash('Correo ya registrado.', 'error')
        return render_template('registro_instructor.html', regionales=Regional.objects())

    usuario = correo_electronico.split('@')[0] + str(random.randint(100, 999))
    contrasena = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    contrasena_hash = generate_password_hash(contrasena)

    regional_obj = Regional.objects.get(id=regional_id)

    nuevo = Instructor(
        nombre_completo=nombre_completo,
        correo_electronico=correo_electronico,
        regional=regional_obj,
        usuario=usuario,
        contrasena=contrasena_hash
    )
    nuevo.save()

    try:
        msg = Message(
            'Datos de Acceso',
            sender=app.config['MAIL_DEFAULT_SENDER'],
            recipients=[correo_electronico]
        )
        msg.body = f"""Hola {nombre_completo},
Tus datos de acceso:
Usuario: {usuario}
Contraseña: {contrasena}
Inicia sesión: {url_for('login', _external=True)}
"""
        mail.send(msg)
        flash('Instructor registrado y correo enviado.', 'success')
    except Exception as e:
        flash(f'Instructor creado, pero error al enviar correo: {e}', 'warning')

    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        usuario = request.form['usuario']
        contrasena = request.form['contrasena']
        instructor = Instructor.objects(usuario=usuario).first()
        if instructor and check_password_hash(instructor.contrasena, contrasena):
            login_user(instructor)
            flash('Inicio de sesión exitoso.', 'success')
            return redirect(url_for('dashboard'))
        flash('Credenciales inválidas.', 'error')
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', current_user=current_user)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sesión cerrada.', 'success')
    return redirect(url_for('login'))

@app.route('/subir_guia', methods=['GET', 'POST'])
@login_required
def subir_guia():
    if request.method == 'POST':
        nombre_guia = request.form['nombre_guia']
        descripcion = request.form['descripcion']
        programa_id = request.form['programa_formacion']
        archivo = request.files.get('documento_pdf')

        if not archivo or archivo.filename == '' or not allowed_file(archivo.filename):
            flash('Archivo inválido. Solo se permiten PDFs.', 'error')
            return redirect(request.url)

        filename = secure_filename(archivo.filename)
        archivo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        programa = ProgramaFormacion.objects.get(id=programa_id)

        GuiaAprendizaje(
            nombre_guia=nombre_guia,
            descripcion=descripcion,
            programa_formacion=programa,
            nombre_documento_pdf=filename,
            instructor=current_user
        ).save()

        flash('Guía subida con éxito.', 'success')
        return redirect(url_for('dashboard'))

    programas = ProgramaFormacion.objects()
    return render_template('subir_guia.html', programas=programas)

@app.route('/listar_guias')
@login_required
def listar_guias():
    try:
        guias_validas = []
        guias = GuiaAprendizaje.objects().order_by('-fecha_publicacion')

        print("\n--- Guías recuperadas de la DB ---")
        for guia in guias:
            try:
                # Validar que instructor exista antes de usarlo
                if guia.instructor is not None:
                    _ = guia.instructor.id  # Forzamos la validación del documento

                # Si pasa, añadimos la guía a la lista final
                guias_validas.append(guia)

                # Depuración
                print(f"✅ Guía válida: {guia.nombre_guia}")
                print(f"  Instructor: {guia.instructor.nombre_completo}")
                print(f"  Programa: {guia.programa_formacion.nombre_programa if guia.programa_formacion else 'N/A'}")
                print(f"  Regional: {guia.instructor.regional.nombre_regional if guia.instructor.regional else 'N/A'}")
                print(f"  PDF: {guia.nombre_documento_pdf}")
            except Exception as err:
                print(f"⚠️ Guía ignorada (instructor inválido): {guia.nombre_guia} - {err}")

        print("-----------------------------------\n")
        return render_template('listar_guias.html', guias=guias_validas)

    except Exception as e:
        print(f"❌ Error en la ruta /listar_guias: {e}")
        flash(f"Ocurrió un error al cargar las guías: {e}", 'error')
        return redirect(url_for('dashboard'))


@app.route('/uploads/<filename>')
@login_required
def descargar_pdf(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# --- Ejecutar ---
if __name__ == '__main__':
    app.run(debug=True)
