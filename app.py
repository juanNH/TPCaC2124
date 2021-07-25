
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session, flash
from flaskext.mysql import MySQL
import MySQLdb.cursors
import re
from datetime import datetime
import os
from functools import wraps

app = Flask(__name__)

app.secret_key = 'Luego remplazar'
#os.environ.get('SECRET')


#conexion a la base de datos        
mysql = MySQL()
#bd heroku
#app.config['MYSQL_DATABASE_HOST'] = 'us-cdbr-east-04.cleardb.com'
#app.config['MYSQL_DATABASE_USER'] = 'b3dfc31564e837'
#app.config['MYSQL_DATABASE_PASSWORD'] = 'c35271f0'
#app.config['MYSQL_DATABASE_DB'] = 'heroku_b18c9020801b5ab'
#local 
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'blog_cac2124'

mysql.init_app(app)

CARPETA = os.path.join('uploads') # al path del proyecto le adjunto ‘upload’
app.config['CARPETA']=CARPETA

# clase nav para pedir las categorias a las vistas
class nav:
    def nav_categorias():
        sql= "SELECT * FROM `categoria`"
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



# vista index
@app.route('/,<string:palabra>')
@app.route('/,<int:id_categoria>')
@app.route('/')
def index(id_categoria = None,palabra = None):
    conn=mysql.connect()
    print(conn)
    print(mysql)
    cursor=conn.cursor()  
    cursor.execute("Show tables;")
    
    myresult = cursor.fetchall()
    
    print('tablas')
    for x in myresult:
        print(x)
    print('.')
    if palabra != None:
        palabra = "%"+palabra+"%"
        sql= "SELECT a.id_articulo,a.titulo,a.contenido,a.id_categoria,a.id_autor, DATE(a.fecha), CONCAT(au.nombre,' ',au.apellido), a.imagen FROM `articulo` a INNER JOIN `categoria` c ON (a.id_categoria = c.id_categoria) INNER JOIN `autor` au ON (a.id_autor = au.id_autor) WHERE a.titulo LIKE   %s   Order by a.fecha DESC;"
        datos = (palabra)
        cursor.execute(sql,datos)
    elif id_categoria != None :
        sql= "SELECT a.id_articulo,a.titulo,a.contenido,a.id_categoria,a.id_autor, DATE(a.fecha), CONCAT(au.nombre,' ',au.apellido), a.imagen FROM `articulo` a INNER JOIN `categoria` c ON (a.id_categoria = c.id_categoria) INNER JOIN `autor` au ON (a.id_autor = au.id_autor) WHERE a.id_categoria = %s Order by a.fecha DESC;"
        datos = (id_categoria)
        cursor.execute(sql,datos) 
    else:
        sql= "SELECT a.id_articulo,a.titulo,a.contenido,a.id_categoria,a.id_autor, DATE(a.fecha), CONCAT(au.nombre,' ',au.apellido), a.imagen FROM `articulo` a INNER JOIN `autor` au ON (a.id_autor = au.id_autor) ORDER BY fecha DESC"
        cursor.execute(sql) 
    
   
    articulos = cursor.fetchall()  
    conn.commit()

    categorias = nav.nav_categorias()
    catDict = {}
    for ind, val in categorias:
        catDict[ind]=val

    return render_template('index.html',
                            articulos = articulos,
                            categorias=categorias,
                            catDict=catDict
                            )

# vista registro
@app.route('/registro')
@login_required
def registro():
    autor= "SELECT id_autor, CONCAT(nombre,' ',apellido) FROM `autor`"
    conn=mysql.connect()
    cursor=conn.cursor()
    cursor.execute(autor) 
    autores = cursor.fetchall()  
    conn.commit()
    


    categorias = nav.nav_categorias()
    return render_template('registro.html', autores = autores,categorias=categorias)
# funcion crear publicacion

@app.route('/crear', methods = ['POST'])
@login_required
def crear():
    _titulo = request.form['titulo']
    _contenido = request.form['contenido']
    _id_categoria = request.form['id_categoria']
    _imagen = request.files['imagen']
    _id_autor = request.form['id_autor']
    now = datetime.now()
    tiempo = now.strftime("%Y/%m/%d %H:%M:%S")   
    if _imagen.filename !='':
        id_img = now.strftime("%Y-%m-%d-%H-%M-%S") 
        nuevoNombreFoto = id_img+_imagen.filename
        _imagen.save("uploads/"+nuevoNombreFoto)
    sql = "INSERT INTO `articulo` (`titulo`,`contenido`,`fecha`,`id_categoria`,`id_autor`,`imagen`) VALUES  (%s,%s,%s,%s,%s,%s);"

    datos=(_titulo,_contenido,tiempo,_id_categoria,_id_autor,nuevoNombreFoto)

    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql, datos)
    conn.commit()

    categorias = nav.nav_categorias()
    return redirect(url_for('index'))

@app.route('/uploads/<nombreFoto>')
@app.route('/articulo/uploads/<nombreFoto>')

def uploads(nombreFoto):
    return send_from_directory(app.config['CARPETA'], nombreFoto)
# vistas de cada articulo de manera individual

@app.route('/articulo/<id_articulo>')
def articulo(id_articulo):
    
    sql= "SELECT a.id_articulo,a.titulo,a.contenido,a.id_categoria,a.id_autor, DATE(a.fecha),a.imagen, CONCAT(au.nombre,' ',au.apellido) FROM `articulo` a INNER JOIN `autor` au ON (a.id_autor = au.id_autor) WHERE id_articulo = %s;"

    datos = (id_articulo)
    conn=mysql.connect()
    cursor=conn.cursor()
    cursor.execute(sql,datos) 
    articulo = cursor.fetchall()  
    conn.commit()

    categorias = nav.nav_categorias()
    catDict = {}
    for ind, val in categorias:
        catDict[ind]=val
    return render_template('articulo.html',
                                        articulo = articulo[0],
                                        categorias=categorias,
                                        catDict=catDict
                                        )
# vista panel de control
@app.route('/panel/<id_autor>')
@login_required
def panel(id_autor):
    sql= "SELECT ar.id_articulo, ar.titulo, ar.contenido, ar.id_categoria, ar.id_autor, ar.fecha, CONCAT(au.nombre,' ',au.apellido), c.categoria, ar.fecha_edicion FROM `articulo` ar INNER JOIN `autor` au ON(ar.id_autor = au.id_autor) INNER JOIN `categoria` c ON (ar.id_categoria = c.id_categoria) WHERE ar.id_autor =%s ;"
    datos = (id_autor)
    conn=mysql.connect()
    cursor=conn.cursor()
    cursor.execute(sql,datos) 
    articulos = cursor.fetchall()  
    conn.commit()

    categorias = nav.nav_categorias()
    return render_template('panel.html',
                                    articulos = articulos,
                                    categorias=categorias
                                    )
# funcion de eliminar articulo
@app.route('/eliminar/<id_articulo>/<id_autor>')
@login_required
def eliminar(id_articulo,id_autor):
    
    sql = "DELETE FROM `articulo` WHERE id_articulo = %s;"
    conn = mysql.connect()
    cursor = conn.cursor()

    cursor.execute("SELECT imagen FROM `articulo` WHERE id_articulo=%s",(id_articulo))
    fila=cursor.fetchall()   # fila va a tener un solo registro y 1 solo campo
    os.remove(os.path.join(app.config['CARPETA'],fila[0][0])) #remuevo la foto
    

    datos = (id_articulo)
    cursor.execute(sql,(datos))
    conn.commit()
    return redirect(url_for('panel',
                                id_autor = id_autor
                                ))
# vista/funcion de editar registro
@app.route('/editar/<id_articulo>/<id_autor>')
@login_required
def editar(id_articulo, id_autor):

    sql = "SELECT ar.id_articulo, ar.titulo, ar.contenido, ar.id_categoria, ar.id_autor, CONCAT(au.nombre,' ',au.apellido), c.categoria, ar.imagen FROM `articulo` ar INNER JOIN `autor` au ON(ar.id_autor = au.id_autor) INNER JOIN `categoria` c ON (ar.id_categoria = c.id_categoria) WHERE ar.id_articulo = %s;"
    datos = (id_articulo)
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql,(datos))
    id_articulo = cursor.fetchall()
    conn.commit()

    categorias = nav.nav_categorias()
    return render_template('editar.html',
                                    categorias = categorias,
                                    id_articulo = id_articulo[0],
                                    id_autor = id_autor
                                    )

@app.route('/editar_articulo/<id_autor>', methods = ['POST'])
@login_required
def editar_articulo(id_autor):
    _id_articulo = request.form['id_articulo']
    _titulo = request.form['titulo']
    _contenido = request.form['contenido']
    _id_categoria = request.form['id_categoria']
    _imagen = request.files['imagen']
    now = datetime.now()
    tiempo = now.strftime("%Y/%m/%d %H:%M:%S") 

    sql="UPDATE `articulo` SET `titulo`=%s ,`contenido`=%s, `id_categoria`=%s, `fecha_edicion` = %s WHERE id_articulo=%s;"
    datos=(_titulo, _contenido, _id_categoria, tiempo, _id_articulo)  # crea la sentencia sql
    conn=mysql.connect()
    cursor=conn.cursor()


  
    if _imagen.filename !='':
        id_img = now.strftime("%Y-%m-%d-%H-%M-%S") 
        nuevoNombreFoto = id_img+_imagen.filename
        _imagen.save("uploads/"+nuevoNombreFoto)

        cursor.execute("SELECT imagen FROM `articulo` WHERE id_articulo=%s",(_id_articulo))

        fila=cursor.fetchall()   # fila va a tener un solo registro y 1 solo campo
        os.remove(os.path.join(app.config['CARPETA'],fila[0][0]))
        cursor.execute("UPDATE `articulo` SET imagen=%s WHERE id_articulo=%s",(nuevoNombreFoto, _id_articulo))
        conn.commit()

    cursor.execute(sql,datos)               # ejecuta la sentencia sql 
    conn.commit()
    return redirect(url_for('panel',
                                id_autor = id_autor
                                ))

#archivo en sidebar


#login  y logout

@app.route('/verificar', methods =['GET', 'POST'])
def verificar():
    if (request.method == 'POST' and 'correo' in request.form and 'password' in request.form):
        _correo = request.form['correo']
        _password = request.form['password']
        conn=mysql.connect()
        cursor=conn.cursor()
        cursor.execute('SELECT * FROM `autor` WHERE correo = % s AND password = % s;', (_correo, _password))
        cuenta = cursor.fetchone()  
        if cuenta:
            session['loggedin'] = True
            session['id_autor'] = cuenta[0] 
            session['correo'] = cuenta[3]

            flash(f'Bienvenido {_correo} !')
            return redirect(url_for('index'))
        else:
            flash(f'Por favor revisa el correo/contraseña !')

    return render_template('login.html', 

                                    )

@app.route('/login')
@app.route('/login,<msg>')
def login(msg=False):
    categorias = nav.nav_categorias()
    return render_template('login.html',
                                    categorias=categorias,msg=msg
                                    )
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id_autor', None)
    session.pop('correo', None)
    return redirect(url_for('login'))

#registrar usuario
@app.route('/registrarse_validacion', methods =['GET', 'POST'])
def registrarse_validacion():
    
    if request.method == 'POST' and 'correo' in request.form and 'nombre' in request.form and 'apellido' in request.form and 'password' in request.form and 'password2' in request.form:
        _correo = request.form['correo']
        _nombre = request.form['nombre']
        _apellido = request.form['apellido']
        _password = request.form['password']
        _password2 = request.form['password2']
        _administrador = 1
        conn=mysql.connect()
        cursor=conn.cursor()
        cursor.execute('SELECT * FROM `autor` WHERE correo = %s', (_correo, ))
        account = cursor.fetchone()
        if account:
            flash('Correo ya registrado en el sistema')
        elif _password != _password2:
            flash('Las contraseñas deben coincidir')
        else:
            cursor.execute('INSERT INTO `autor`(nombre,apellido,correo,password,administrador) VALUES (%s, %s, %s, %s,%s)', (_nombre,_apellido,_correo,_password,_administrador))
            conn.commit()
            conn=mysql.connect()
            cursor=conn.cursor()
            cursor.execute('SELECT * FROM `autor` WHERE correo = % s AND password = % s;', (_correo, _password))
            cuenta = cursor.fetchone()  
            if cuenta:
                session['loggedin'] = True
                session['id_autor'] = cuenta[0] 
                session['correo'] = cuenta[3]
                session['administrador']  = cuenta[5] 
                flash(f"""Registro exitoso!
                    Bienvenido {_correo} !""")
                return redirect(url_for('index'))


        
    return redirect(url_for('registrarse',
                                        ))


@app.route('/registrarse')
def registrarse():
    categorias = nav.nav_categorias()
    return render_template('registrarse.html',
                                            categorias = categorias
                                            )

@app.route('/buscador', methods = ['POST'])
def buscador():
    _palabra = request.form['palabra']

    return redirect(url_for('index',
                                    palabra = _palabra
                                    ))
if __name__ == '__main__':
    app.run(debug=True)
        