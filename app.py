
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session
from flaskext.mysql import MySQL
import MySQLdb.cursors
import re
from datetime import datetime
import os
from functools import wraps

app = Flask(__name__)

app.secret_key = 'pepe'

#conexion a la base de datos
mysql = MySQL()
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'blog_cac2124'
mysql.init_app(app)

# clase nav para pedir las categorias a las vistas
class nav:
    def nav_categorias():
        sql= "SELECT * FROM `blog_cac2124`.`categoria`"
        conn=mysql.connect()
        cursor=conn.cursor()
        cursor.execute(sql) 
        nav_categorias = cursor.fetchall()  
        conn.commit()

        return nav_categorias

def login_required(test):
    @wraps(test)
    def wrap(*args,**kwargs):
        if 'loggedin' in session:
            return test(*args, **kwargs)
        else:
            return redirect(url_for('index'))
    return wrap
 #   insert into blog_cac2124.autor (nobmre,apellido, correo,password) VALUES ('pepe','pepe','pepe@pepe.com','asdasd'); 
 #insertar usuarios luego para crear


# vista index
@app.route('/,<string:msg>')
@app.route('/,<int:id_categoria>')
@app.route('/')
def index(id_categoria = None, msg=None):
    conn=mysql.connect()
    cursor=conn.cursor()
    if id_categoria != None :
        sql= "SELECT a.id_articulo,a.titulo,a.contenido,a.id_categoria,a.id_autor, DATE(a.fecha) FROM `blog_cac2124`.`articulo` a INNER JOIN `blog_cac2124`.`categoria` c ON (a.id_categoria = c.id_categoria) WHERE a.id_categoria = %s;"
        datos = (id_categoria)
        cursor.execute(sql,datos) 
    else:
        sql= "SELECT id_articulo,titulo,contenido,id_categoria,id_autor, DATE(fecha) FROM `blog_cac2124`.`articulo`"
        cursor.execute(sql) 
    
   
    articulos = cursor.fetchall()  
    conn.commit()

    categorias = nav.nav_categorias()

    return render_template('index.html',articulos = articulos,categorias=categorias, msg=msg)

# vista registro
@app.route('/registro')
@login_required
def registro():
    autor= "SELECT id_autor, CONCAT(nombre,' ',apellido) FROM `blog_cac2124`.`autor`"
    conn=mysql.connect()
    cursor=conn.cursor()
    cursor.execute(autor) 
    autores = cursor.fetchall()  
    conn.commit()


    categorias = nav.nav_categorias()
    return render_template('registro.html',autores = autores,categorias=categorias)
# funcion crear publicacion
@app.route('/crear', methods = ['POST'])
def crear():
    _titulo = request.form['titulo']
    _contenido = request.form['contenido']
    _id_categoria = request.form['id_categoria']
    _id_autor = request.form['id_autor']
    now = datetime.now()
    tiempo = now.strftime("%Y/%m/%d %H:%M:%S")   
    sql = "INSERT INTO `articulo` (`titulo`,`contenido`,`fecha`,`id_categoria`,`id_autor`) VALUES  (%s, %s,%s,%s,%s);"

    datos=(_titulo,_contenido,tiempo,_id_categoria,_id_autor)

    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql, datos)
    conn.commit()

    categorias = nav.nav_categorias()
    return redirect(url_for('index'))
# vistas de cada articulo de manera individual
@app.route('/articulo/<id_articulo>')
def articulo(id_articulo):

    sql= "SELECT id_articulo,titulo,contenido,id_categoria,id_autor, DATE(fecha) FROM `blog_cac2124`.`articulo` WHERE id_articulo = %s;"
    datos = (id_articulo)
    conn=mysql.connect()
    cursor=conn.cursor()
    cursor.execute(sql,datos) 
    articulo = cursor.fetchall()  
    conn.commit()

    categorias = nav.nav_categorias()
    return render_template('articulo.html',articulo = articulo[0],categorias=categorias)
# vista panel de control
@app.route('/panel/<id_autor>')
@login_required
def panel(id_autor):
    sql= "SELECT ar.id_articulo, ar.titulo, ar.contenido, ar.id_categoria, ar.id_autor, ar.fecha, CONCAT(au.nombre,' ',au.apellido), c.categoria FROM `blog_cac2124`.`articulo`ar INNER JOIN `blog_cac2124`.`autor` au ON(ar.id_autor = au.id_autor) INNER JOIN `blog_cac2124`.`categoria` c ON (ar.id_categoria = c.id_categoria) WHERE ar.id_autor =%s ;"
    datos = (id_autor)
    conn=mysql.connect()
    cursor=conn.cursor()
    cursor.execute(sql,datos) 
    articulos = cursor.fetchall()  
    conn.commit()

    categorias = nav.nav_categorias()
    return render_template('panel.html',articulos = articulos,categorias=categorias)
# funcion de eliminar articulo
@app.route('/eliminar/<id_articulo>/<id_autor>')
def eliminar(id_articulo,id_autor):
    
    sql = "DELETE FROM `blog_cac2124`.`articulo` WHERE id_articulo = %s;"
    conn = mysql.connect()
    cursor = conn.cursor()
    datos = (id_articulo)
    cursor.execute(sql,(datos))

    cursor.execute(sql,(id))
    conn.commit()
    return redirect(url_for('panel',id_autor = id_autor))
# vista/funcion de editar registro
@app.route('/editar/<id_articulo>/<id_autor>')
def editar(id_articulo, id_autor):

    sql = "SELECT ar.id_articulo, ar.titulo, ar.contenido, ar.id_categoria, ar.id_autor, CONCAT(au.nombre,' ',au.apellido), c.categoria FROM `blog_cac2124`.`articulo`ar INNER JOIN `blog_cac2124`.`autor` au ON(ar.id_autor = au.id_autor) INNER JOIN `blog_cac2124`.`categoria` c ON (ar.id_categoria = c.id_categoria) WHERE ar.id_articulo = %s;"
    datos = (id_articulo)
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql,(datos))
    id_articulo = cursor.fetchall()
    conn.commit()

    categorias = nav.nav_categorias()
    return render_template('editar.html', categorias = categorias, id_articulo = id_articulo[0],id_autor = id_autor)

@app.route('/editar_articulo/<id_autor>', methods = ['POST'])
def editar_articulo(id_autor):
    _id_articulo = request.form['id_articulo']
    _titulo = request.form['titulo']
    _contenido = request.form['contenido']
    _id_categoria = request.form['id_categoria']

    sql="UPDATE `blog_cac2124`.`articulo` SET `titulo`=%s ,`contenido`=%s, `id_categoria`=%s WHERE id_articulo=%s;"
    datos=(_titulo,_contenido,_id_categoria,_id_articulo)  # crea la sentencia sql
    conn=mysql.connect()
    cursor=conn.cursor()
    cursor.execute(sql,datos)               # ejecuta la sentencia sql 
    conn.commit()
    return redirect(url_for('panel',id_autor = id_autor))


#login  y logout

@app.route('/verificar', methods =['GET', 'POST'])
def verificar():
    msg = ''
    if (request.method == 'POST' and 'correo' in request.form and 'password' in request.form):
        _correo = request.form['correo']
        _password = request.form['password']
        conn=mysql.connect()
        cursor=conn.cursor()
        cursor.execute('SELECT * FROM `blog_cac2124`.`autor` WHERE correo = % s AND password = % s;', (_correo, _password))
        cuenta = cursor.fetchone()  
        if cuenta:
            session['loggedin'] = True
            session['id_autor'] = cuenta[0] 
            session['correo'] = cuenta[3]
            msg = f'Logeo exitoso {_correo} !'
            return redirect(url_for('index', msg = msg))
        else:
            msg = 'Incorrect username / password !'

    return render_template('login.html', msg = msg)

@app.route('/login')
@app.route('/login,<msg>')
def login(msg=False):
    categorias = nav.nav_categorias()
    return render_template('login.html',categorias=categorias,msg=msg)
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id_autor', None)
    session.pop('correo', None)
    return redirect(url_for('login'))

#registrar usuario
@app.route('/registrarse_validacion', methods =['GET', 'POST'])
def registrarse_validacion():
    msg = ''
    
    if request.method == 'POST' and 'correo' in request.form and 'nombre' in request.form and 'apellido' in request.form and 'password' in request.form and 'password2' in request.form:
        _correo = request.form['correo']
        _nombre = request.form['nombre']
        _apellido = request.form['apellido']
        _password = request.form['password']
        _password2 = request.form['password2']

        conn=mysql.connect()
        cursor=conn.cursor()
        cursor.execute('SELECT * FROM `blog_cac2124`.`autor` WHERE correo = %s', (_correo, ))
        account = cursor.fetchone()
        if account:
            msg = 'Correo ya registrado!'
        elif _password != _password2:
            msg = 'Las password deben coincidir'
        else:
            cursor.execute('INSERT INTO `blog_cac2124`.`autor`(nombre,apellido,correo,password) VALUES (%s, %s, %s, %s)', (_nombre,_apellido,_correo,_password ))
            conn.commit()
            msg = ' Te has registrado correctamente !'
            return redirect(url_for('login', msg=msg))

        
    return redirect(url_for('registrarse', msg=msg))

@app.route('/registrarse/<msg>')
@app.route('/registrarse')
def registrarse(msg=None):
    categorias = nav.nav_categorias()
    return render_template('registrarse.html', msg=msg, categorias = categorias)
if __name__ == '__main__':
    app.run(debug=True)