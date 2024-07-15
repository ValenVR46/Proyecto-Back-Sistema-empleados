from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from flask_mysqldb import MySQL
from datetime import datetime
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Configuración de la base de datos
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'bHz9FmpRi5iv8Yu$'
app.config['MYSQL_DB'] = 'it_shop'
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'uploads')

mysql = MySQL(app)

# Ruta para servir archivos subidos
@app.route('/uploads/<nombreFoto>')
def uploads(nombreFoto):
    return send_from_directory(app.config['UPLOAD_FOLDER'], nombreFoto)

# Ruta principal, lista todos los empleados
@app.route('/')
def index():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM empleados")
    empleados = cursor.fetchall()
    cursor.close()
    return render_template('empleados/index.html', empleados=empleados)

# Ruta para eliminar un empleado por ID
@app.route('/destroy/<int:id>')
def destroy(id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT foto FROM empleados WHERE id=%s", (id,))
    fila = cursor.fetchone()
    if fila and fila[0]:
        try:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], fila[0]))
        except FileNotFoundError:
            pass
    cursor.execute("DELETE FROM empleados WHERE id=%s", (id,))
    mysql.connection.commit()
    cursor.close()
    return redirect('/')

# Ruta para editar un empleado por ID
@app.route('/edit/<int:id>')
def edit(id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM empleados WHERE id=%s", (id,))
    empleado = cursor.fetchone()
    cursor.close()
    return render_template('empleados/edit.html', empleado=empleado)

# Ruta para actualizar los datos de un empleado
@app.route('/update', methods=['POST'])
def update():
    _nombre = request.form['txtNombre']
    _correo = request.form['txtCorreo']
    _foto = request.files['txtFoto']
    id = request.form['txtID']

    cursor = mysql.connection.cursor()
    sql = "UPDATE empleados SET apeynom=%s, email=%s WHERE id=%s"
    datos = (_nombre, _correo, id)

    now = datetime.now()
    tiempo = now.strftime("%Y%H%M%S")

    if _foto.filename != '':
        nuevoNombreFoto = secure_filename(tiempo + "_" + _foto.filename)
        _foto.save(os.path.join(app.config['UPLOAD_FOLDER'], nuevoNombreFoto))

        cursor.execute("SELECT foto FROM empleados WHERE id=%s", (id,))
        fila = cursor.fetchone()
        if fila and fila[0]:
            try:
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], fila[0]))
            except FileNotFoundError:
                pass

        cursor.execute("UPDATE empleados SET foto=%s WHERE id=%s", (nuevoNombreFoto, id))

    cursor.execute(sql, datos)
    mysql.connection.commit()
    cursor.close()

    return redirect('/')

# Ruta para mostrar el formulario de creación de empleados
@app.route('/create')
def create():
    return render_template('empleados/create.html')

# Ruta para almacenar los datos del nuevo empleado
@app.route('/store', methods=['POST'])
def storage():
    _nombre = request.form['txtNombre']
    _correo = request.form['txtCorreo']
    _foto = request.files['txtFoto']

    if _nombre == '' or _correo == '' or _foto == '':
        flash('Recuerda llenar todos los campos')
        return redirect(url_for('create'))

    now = datetime.now()
    tiempo = now.strftime("%Y%H%M%S")

    if _foto.filename != '':
        nuevoNombreFoto = secure_filename(tiempo + "_" + _foto.filename)
        _foto.save(os.path.join(app.config['UPLOAD_FOLDER'], nuevoNombreFoto))

    cursor = mysql.connection.cursor()
    sql = "INSERT INTO empleados (apeynom, email, foto) VALUES (%s, %s, %s)"
    datos = (_nombre, _correo, nuevoNombreFoto)
    cursor.execute(sql, datos)
    mysql.connection.commit()
    cursor.close()

    return redirect('/')

# Línea requerida para que se pueda empezar a ejecutar la app
if __name__ == '__main__':
    app.run(debug=True)



