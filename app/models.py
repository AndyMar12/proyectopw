import os
import mysql.connector
from datetime import datetime
import json
from werkzeug.security import generate_password_hash

def conexionDatos():
    conn = mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME')
    )
    return conn

def verificarUsuario(correo):
    conn = conexionDatos()
    cursor = conn.cursor(dictionary=True) 
    cursor = conn.cursor()
    cursor.execute('SELECT Id, Nombre, rol, password FROM usuarios WHERE correo = %s;', (correo,))
    usuario = cursor.fetchone()
    conn.close()
    return (usuario)

def nombreAplicativos():
    #start_time = time.time()
    conn = conexionDatos()
    cursor = conn.cursor()
    cursor.execute("SELECT Nombre FROM aplicativos;")
    tablas = cursor.fetchall()
    conn.close()
    #end_time = time.time()  # Captura el tiempo al final
    # Calcula el tiempo de ejecución
    #execution_time = end_time - start_time
    #print(f"Tiempo de ejecución: {execution_time:.4f} segundos")
    return [tabla[0] for tabla in tablas]

def obtener_titulos(tabla):
    conn = conexionDatos()
    cursor = conn.cursor()
    try:
        cursor.execute(f"SELECT datosApp FROM Aplicativos WHERE Nombre = '{tabla}';")
        columnas_lista = cursor.fetchall()
        json_string = columnas_lista[0][0]
        titulos = tuple(json.loads(json_string))
    except mysql.connector.Error as e:
        print(f"Error al obtener los títulos: {e}")
        titulos = []
    finally:
        conn.close()
    return titulos

def agregarRegistro(appNombre, columnas, valorList):
    conn = conexionDatos()
    cursor = conn.cursor()
    cursor.execute(f"INSERT INTO {appNombre} ({columnas}) VALUES {valorList}")
    conn.commit()
    conn.close()
    return("registados")

def buscarIdTutor(idLider):
    conn = conexionDatos()
    cursor = conn.cursor()
    cursor.execute(f'SELECT id_tutor FROM Usuarios WHERE Id={idLider};')
    resul=cursor.fetchall()
    conn.close()
    if resul:
        idTutor=resul[0][0]
    return (idTutor)

def leerRegistros(appSelect, titulos):
    conn = conexionDatos()
    cursor = conn.cursor()
    try:
        if appSelect:
            titulo=', '.join(titulos)
            cursor.execute(f"SELECT {titulo} FROM {appSelect};")
            registros = cursor.fetchall()
        else:
            registros = []
    except mysql.connector.Error as e:
        print(f"Error al ejecutar la consulta: {e}")
        registros = []
    finally:
        conn.close()
    return registros

def nominas(fecha):
    conn = conexionDatos()
    cursor = conn.cursor()
    cursor.execute(f"SELECT Fecha, Aplicacion, id_tutor, id_streamer, Monedas FROM Nomina WHERE Fecha LIKE '{fecha}';")
    datos=cursor.fetchall()
    conn.close()
    titulos="('Fecha', 'Aplicacion', 'Tutor', 'IDStreamer', 'Monedas')"
    titulos=eval(titulos)
    return datos, titulos

def graphics(iD, rol):
    conn = conexionDatos()
    cursor = conn.cursor()
    datos=[]
    if rol=='Lider':
        iD=buscarIdTutor(iD)
        cursor.execute(f"SELECT Fecha, COUNT(*) AS Contador FROM Nomina WHERE id_lider={iD} GROUP BY Fecha ORDER BY Fecha;")
    else:
        cursor.execute(f"SELECT Fecha, COUNT(*) AS Contador FROM Nomina WHERE id_tutor={iD} GROUP BY Fecha ORDER BY Fecha;")
        datos=cursor.fetchall()
    conn.close()
    return datos

def search(dato):
    conn = conexionDatos()
    cursor = conn.cursor()
    cursor.execute(f"SELECT Nombre FROM Usuarios WHERE (Nombre LIKE CONCAT('%', {dato}, '%')) OR (Correo LIKE CONCAT('%', {dato}, '%'));")
    busqueda=cursor.fetchall()
    conn.close()
    return busqueda

def createUSer(valores, rol, password):
    conn = conexionDatos()
    cursor = conn.cursor()
    passW=generate_password_hash(password)
    id_tutor='NULL'
    if rol == 'Lider':
        id_tutor='Lider'
    cursor.execute(f"INSERT INTO Usuarios (Id, Nombre, Correo, Password, Dir, Rol, Estado, id_tutor) VALUES {valores, id_tutor};")
    conn.commit()
    conn.close()
    return("registados")