from flask import render_template, request, redirect, url_for, Blueprint, session, flash, jsonify
from werkzeug.security import check_password_hash
from .models import nombreAplicativos, obtener_titulos, agregarRegistro, leerRegistros, verificarUsuario, nominas, buscarIdTutor, graphics
from functools import wraps  # Importa wraps
from datetime import datetime
import pandas as pd
import plotly.express as px

main_routes = Blueprint('main_routes', __name__)

def role_required(allowed_roles):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            role = session.get('rol')
            if role not in allowed_roles:
                flash('No tienes permiso para acceder a esta página', 'error')
                return redirect(url_for('main_routes.login'))  # Redirigir si el rol no es permitido.
            return func(*args, **kwargs)
        return wrapper
    return decorator

@main_routes.route("/")
def index():
    return render_template('index.html')

@main_routes.route("/about")
def about():
    return render_template('about.html')

@main_routes.route("/contact")
def contact():
    return render_template('contact.html')

@main_routes.route("/registros", methods=['GET', 'POST'])
@role_required(['Tutor', 'Lider', 'manager'])
def registros():
    rol= session['rol']
    opcionesApp=nombreAplicativos()
    appSelect=request.args.get('appNombre')
    if appSelect:
        titulos=('Fecha',)+obtener_titulos(appSelect)
        print(titulos)
        registros=leerRegistros(appSelect, titulos)
    else:
        registros=[]
        titulos=[]
    return render_template("registros.html", registros=registros, appSelect=appSelect, opcionesApp=opcionesApp, titulos=titulos, rol=rol)

@main_routes.route("/ganancias", methods=['GET', 'POST'])
@role_required(['Tutor', 'Lider', 'manager'])
def ganancias():
    rol= session['rol']
    tabla=[]
    titulos=[]
    fecha=request.form.get('fecha')
    if request.method=='POST':
        fecha=request.form.get('fecha')
        (tabla, titulos)=nominas(fecha)
    return render_template('ganancias.html', fecha=fecha, tabla=tabla, titulos=titulos, rol=rol)

@main_routes.route('/nuevoRegistro', methods=['GET', 'POST'])
@role_required(['Tutor', 'Lider', 'manager'])
def nuevoRegistro():
    rol= session['rol']
    tablas=nombreAplicativos()
    appNombre = None  # Inicializar appNombre
    campos = []  # Inicializar campos
    datos={}
    for tabla in tablas:
        campos=obtener_titulos(tabla)
        datos[tabla]=campos
    if request.method == 'POST':
        appNombre = request.form.get('appNombre')
        campos = datos.get(appNombre, [])#campos = obtener_titulos(appNombre)
        valores = {campo: request.form.get(campo) for campo in campos}
        columnas = ', '.join(campos)
        valorList = list(valores.values())
        fecha=datetime.now().strftime('%Y-%m-%d')
        if rol=='Tutor':
            columnas += ", id_tutor, Fecha"
            idAdd=str(session['usuario_id'])
            valorList.append(idAdd)
            valorList.append(fecha)
            valorList=tuple(valorList)
        elif rol=='Lider':#Lider
            columnas += ", id_tutor, id_lider, Fecha"
            idAdd=str(session['usuario_id'])
            idTutor=buscarIdTutor(idAdd)
            valorList.append(idTutor)
            valorList.append(idAdd)
            valorList.append(fecha)
            valorList=tuple(valorList)

        agregarRegistro(appNombre, columnas, valorList)
        return redirect(url_for('main_routes.nuevoRegistro'))
    return render_template('nuevoRegistro.html', datos=datos, tablas=tablas, rol=rol)

@main_routes.route('/login', methods=['GET', 'POST'])
def login():
    if 'usuario_id' not in session:
        if request.method == 'POST':
            correo = request.form['correo']
            password = request.form['password']
        
            usuario = verificarUsuario(correo)
            if usuario and check_password_hash(usuario[3], password):
                session['usuario_id'] = usuario[0]
                session['nombre'] = usuario[1]
                session['rol'] = usuario[2]
                return redirect(url_for('main_routes.dashboard'))
            else:
                flash('Correo o contraseña incorrectos', 'error')
                return redirect(url_for('main_routes.login'))
        return render_template('login.html')
    else:
        return redirect(url_for('main_routes.dashboard'))

@main_routes.route('/dashboard')
@role_required(['Tutor', 'Lider', 'manager'])
def dashboard():
    idAdd=session['usuario_id']
    rol= session['rol']
    datos=graphics(idAdd, rol)
    df = pd.DataFrame(datos, columns=['Fecha', 'Streamer'])
    fig = px.line(df, x='Fecha', y='Streamer', title='Cantidad Streamer cobrando', markers=True)
    #fig.update_traces(marker=dict(size=8, color='red', symbol='circle'))
    fig.update_layout(
        yaxis=dict(range=[0, None])  # Asegura que el eje Y inicie en 0
    )
    graph_html = fig.to_html(full_html=False, config={'displayModeBar': False})
    return render_template('/dashboard.html', graph_html=graph_html, rol=rol)

@main_routes.route('/logout')
@role_required(['Tutor', 'Lider', 'manager'])
def logout():
    session.clear()
    flash('Sesión cerrada correctamente', 'success')
    return redirect(url_for('main_routes.login'))

@main_routes.route('/lideres')
@role_required(['Tutor'])
def lideres():
    rol= session['rol']
    return render_template('/lideres.html', rol=rol)

@main_routes.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Recurso no encontrado"}), 404

