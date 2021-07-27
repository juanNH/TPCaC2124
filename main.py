from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session, flash
from flaskext.mysql import MySQL
from datetime import datetime
import os
import hashlib
from functools import wraps

app = Flask(__name__)

secret_key = os.environ['SECRET']

#secret_key = 'Remplazar en produccion'

app.secret_key = secret_key
db = os.environ['DB']
host = os.environ['HOST']
password = os.environ['PASSWORD']
user = os.environ['USER']




#conexion a la base de datos        
mysql = MySQL()
#Produccion
app.config['MYSQL_DATABASE_HOST'] = host
app.config['MYSQL_DATABASE_USER'] = user
app.config['MYSQL_DATABASE_PASSWORD'] = password
app.config['MYSQL_DATABASE_DB'] = db

#local 
#app.config['MYSQL_DATABASE_HOST'] = 'localhost'
#app.config['MYSQL_DATABASE_USER'] = 'root'
#app.config['MYSQL_DATABASE_PASSWORD'] = ''
#app.config['MYSQL_DATABASE_DB'] = 'blog_cac2124'

mysql.init_app(app)

CARPETA = os.path.join('uploads') # al path del proyecto le adjunto ‘upload’
app.config['CARPETA']=CARPETA

# clase nav para pedir las categorias a las vistas

class nav:
    def nav_categorias():
        sql= "SELECT c.id_categoria, c.categoria, COUNT(DISTINCT(a.id_categoria)) FROM `categoria` c LEFT JOIN `articulo` a ON (c.id_categoria = a.id_categoria) GROUP BY c.categoria;"
        conn=mysql.connect()
        cursor=conn.cursor()
        cursor.execute(sql) 
        nav_categorias = cursor.fetchall()  
        conn.commit()

        return nav_categorias

class contacto:
    def mensajes():
        sql= "SELECT * FROM `contacto`"
        conn=mysql.connect()
        cursor=conn.cursor()
        cursor.execute(sql) 
        mensajes = cursor.fetchall()  
        conn.commit()

        return mensajes

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
    cursor=conn.cursor()  
    cursor.execute("Show tables;")
    
    myresult = cursor.fetchall()
    
    if palabra != None:
        palabra = "%"+palabra+"%"
        sql= "SELECT a.id_articulo,a.titulo,a.contenido,a.id_categoria,a.id_autor, DATE(a.fecha), CONCAT(au.nombre,' ',au.apellido), a.imagen,c.categoria FROM `articulo` a INNER JOIN `categoria` c ON (a.id_categoria = c.id_categoria) INNER JOIN `autor` au ON (a.id_autor = au.id_autor) WHERE a.titulo LIKE   %s   Order by a.fecha DESC;"
        datos = (palabra)
        cursor.execute(sql,datos)
    elif id_categoria != None :
        sql= "SELECT a.id_articulo,a.titulo,a.contenido,a.id_categoria,a.id_autor, DATE(a.fecha), CONCAT(au.nombre,' ',au.apellido), a.imagen,c.categoria FROM `articulo` a INNER JOIN `categoria` c ON (a.id_categoria = c.id_categoria) INNER JOIN `autor` au ON (a.id_autor = au.id_autor) WHERE a.id_categoria = %s Order by a.fecha DESC;"
        datos = (id_categoria)
        cursor.execute(sql,datos) 
    else:
        sql= "SELECT a.id_articulo,a.titulo,a.contenido,c.categoria,a.id_autor, DATE(a.fecha), CONCAT(au.nombre,' ',au.apellido), a.imagen,c.categoria FROM `articulo` a INNER JOIN `autor` au ON (a.id_autor = au.id_autor) INNER JOIN `categoria` c ON(c.id_categoria = a.id_categoria) ORDER BY fecha DESC;"
        cursor.execute(sql) 
    
   
    articulos = cursor.fetchall()  
    conn.commit()

    categorias = nav.nav_categorias()


    return render_template('index.html',
                            articulos = articulos,
                            categorias=categorias,

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

#vista contacto
@app.route('/contactate')
def contactate():
    conn=mysql.connect()
    conn.commit()

    categorias = nav.nav_categorias()
    return render_template('contacto.html',categorias=categorias)

@app.route("/contacto_validacion", methods = ['POST'])
def contacto_validacion():
    _email = request.form['contact-email']
    _asunto = request.form['contact-asunto']
    _text = request.form['contact-text']

    sql = "INSERT INTO `contacto` (`email`,`asunto`,`mensaje`) VALUES  (%s,%s,%s);"

    datos=(_email,_asunto,_text)

    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql, datos)
    conn.commit()

    categorias = nav.nav_categorias()
    return render_template('index.html',categorias=categorias)

@app.route('/alertas/<id_mensaje>/')
def panelAlerta(id_mensaje):
    sql="SELECT email, asunto, mensaje FROM `contacto` WHERE `id_mensaje` = %s"

    datos = (int(id_mensaje))
    conn=mysql.connect()
    cursor=conn.cursor()
    cursor.execute(sql,datos) 
    mensaje = cursor.fetchall()

    return render_template('alertas.html', mensaje=mensaje[0])
    
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
    sql = "INSERT INTO `articulo` (`titulo`,`contenido`,`fecha`,`id_categoria`,`id_autor`,`imagen`,`fecha_edicion`) VALUES  (%s,%s,%s,%s,%s,%s,%s);"

    datos=(_titulo,_contenido,tiempo,_id_categoria,_id_autor,nuevoNombreFoto,tiempo)

    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql, datos)
    conn.commit()

    return redirect(url_for('index'))

@app.route('/uploads/<nombreFoto>')
@app.route('/articulo/uploads/<nombreFoto>')

def uploads(nombreFoto):
    return send_from_directory(app.config['CARPETA'], nombreFoto)
# vistas de cada articulo de manera individual

@app.route('/articulo/<id_articulo>')
def articulo(id_articulo):
    
    sql= "SELECT a.id_articulo,a.titulo,a.contenido,c.categoria,a.id_autor, DATE(a.fecha),a.imagen, CONCAT(au.nombre,' ',au.apellido) FROM `articulo` a INNER JOIN `autor` au ON (a.id_autor = au.id_autor) INNER JOIN `categoria` c ON (c.id_categoria = a.id_categoria) WHERE id_articulo = %s;"
    datos = (id_articulo)
    conn=mysql.connect()
    cursor=conn.cursor()
    cursor.execute(sql,datos) 
    articulo = cursor.fetchall()  
    conn.commit()

    categorias = nav.nav_categorias()
  
    return render_template('articulo.html',
                                        articulo = articulo[0],
                                        categorias=categorias,
                                       
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

#Comandos de administrador
@app.route('/panel_administrador')
@login_required
def panel_admin():

    if session['loggedin'] == True & session['id_administrador'] == 1 :
        categorias = nav.nav_categorias()
        mensajes = contacto.mensajes()
        sql= "SELECT ar.id_articulo, ar.titulo, ar.contenido, ar.id_categoria, ar.id_autor, ar.fecha, CONCAT(au.nombre,' ',au.apellido), c.categoria, ar.fecha_edicion FROM `articulo` ar INNER JOIN `autor` au ON(ar.id_autor = au.id_autor) INNER JOIN `categoria` c ON (ar.id_categoria = c.id_categoria);"
        conn=mysql.connect()
        cursor=conn.cursor()
        cursor.execute(sql) 
        articulos = cursor.fetchall()  
        conn.commit()
        return render_template('panel_admin.html',
                                        categorias = categorias,
                                        mensajes = mensajes,
                                        articulos = articulos
                                        )
    else:
        return redirect(url_for('index'))
@app.route('/eliminar_articulo_admin/<id_articulo>/')
@login_required
def eliminar_articulo_admin(id_articulo):
    
    sql = "DELETE FROM `articulo` WHERE id_articulo = %s;"
    conn = mysql.connect()
    cursor = conn.cursor()

    cursor.execute("SELECT imagen FROM `articulo` WHERE id_articulo=%s",(id_articulo))
    fila=cursor.fetchall()   # fila va a tener un solo registro y 1 solo campo
    os.remove(os.path.join(app.config['CARPETA'],fila[0][0])) #remuevo la foto


    datos = (id_articulo)
    cursor.execute(sql,(datos))
    conn.commit()
    return redirect(url_for('panel_admin'
                                ))
@app.route('/eliminar_mensaje/<id_mensaje>/')
@login_required
def eliminar_mensaje(id_mensaje):
    
    sql = "DELETE FROM `contacto` WHERE id_mensaje = %s;"
    conn = mysql.connect()
    cursor = conn.cursor()


    datos = (id_mensaje)
    cursor.execute(sql,(datos))
    conn.commit()
    return redirect(url_for('panel_admin'
                                ))
@app.route('/eliminar_categoria/<id_categoria>')
@login_required
def eliminar_categoria(id_categoria):
    if session['loggedin'] == True & session['id_administrador'] == 1 :
        datos = (id_categoria)
        sql="select a.imagen from articulo a INNER JOIN categoria c ON (a.id_categoria = c.id_categoria) WHERE c.id_categoria = %s"
        conn=mysql.connect()
        cursor=conn.cursor()
        cursor.execute(sql,datos) 
        nombres_img = cursor.fetchall()  
        conn.commit()

        for nombre in nombres_img:
            os.remove(os.path.join(app.config['CARPETA'],nombre[0])) #remuevo las fotos


        sql="delete from articulo where id_categoria = %s;"
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute(sql,(datos))
        conn.commit()

        sql="delete from categoria where id_categoria = %s;"

        cursor.execute(sql,(datos))
        conn.commit()

        return redirect(url_for('panel_admin'))
    else:
        return redirect(url_for('index'))
@app.route('/crear_categoria', methods =['GET', 'POST'])
@login_required
def crear_categoria():
    if session['loggedin'] == True & session['id_administrador'] == 1 :
        _categoria = request.form['categoria']

        sql = "INSERT INTO `categoria` (`categoria`) VALUES  (%s);"
        datos=(_categoria)
        
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute(sql, datos)
        conn.commit()

        return redirect(url_for('panel_admin',
                                            ))
    else:
        return redirect(url_for('index'))

# funcion de eliminar articulo
@app.route('/eliminar/<id_articulo>/<id_autor>')
@login_required
def eliminar(id_articulo,id_autor):
    
    sql = "DELETE FROM `articulo` WHERE id_articulo = %s AND id_autor = %s;"
    conn = mysql.connect()
    cursor = conn.cursor()

    cursor.execute("SELECT imagen FROM `articulo` WHERE id_articulo=%s",(id_articulo))
    fila=cursor.fetchall()   # fila va a tener un solo registro y 1 solo campo
    os.remove(os.path.join(app.config['CARPETA'],fila[0][0])) #remuevo la foto
    

    datos = (id_articulo, id_autor)
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

#login  y logout

@app.route('/verificar', methods =['GET', 'POST'])
def verificar():
    if (request.method == 'POST' and 'correo' in request.form and 'password' in request.form):
        _correo = request.form['correo']
        _password = request.form['password']

        _cifrado1 = hashlib.md5(_password.encode())

        conn=mysql.connect()
        cursor=conn.cursor()
        cursor.execute('SELECT * FROM `autor` WHERE correo = % s AND password = % s;', (_correo, _cifrado1.hexdigest()))
        cuenta = cursor.fetchone()  
        if cuenta:
            session['loggedin'] = True
            session['id_autor'] = cuenta[0] 
            session['correo'] = cuenta[3]
            session['id_administrador']  = cuenta[5] 
            flash(f'Bienvenido {_correo} !')
            return redirect(url_for('index'))
        else:
            flash(f'Por favor revisa el correo/contraseña !')

    return render_template('login.html', 

                                    )

@app.route('/login')
def login(msg=False):
    session.pop('loggedin', None)
    session.pop('id_autor', None)
    session.pop('correo', None)
    session.pop('id_administrador',None)
    categorias = nav.nav_categorias()
    return render_template('login.html',
                                    categorias=categorias
                                    )
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id_autor', None)
    session.pop('correo', None)
    session.pop('id_administrador',None)
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

        _cifrado1 = hashlib.md5(_password.encode())
        _cifrado2 = hashlib.md5(_password2.encode())




        conn=mysql.connect()
        cursor=conn.cursor()
        cursor.execute('SELECT * FROM `autor` WHERE correo = %s', (_correo, ))
        account = cursor.fetchone()
        if account:
            flash('Correo ya registrado en el sistema')
        elif _cifrado1.hexdigest() != _cifrado2.hexdigest():
            flash('Las contraseñas deben coincidir')
        else:
            
            cursor.execute('INSERT INTO `autor`(nombre,apellido,correo,password) VALUES (%s, %s, %s, %s)', (_nombre,_apellido,_correo,_cifrado1.hexdigest()))
            conn.commit()
            conn=mysql.connect()
            cursor=conn.cursor()
            cursor.execute('SELECT * FROM `autor` WHERE correo = % s AND password = % s;', (_correo, _cifrado1.hexdigest()))
            cuenta = cursor.fetchone()  
            if cuenta:
                session['loggedin'] = True
                session['id_autor'] = cuenta[0] 
                session['correo'] = cuenta[3]
                session['id_administrador']  = cuenta[5] 
                flash(f"""Registro exitoso!
                    Bienvenido {_correo} !""")
                return redirect(url_for('index'))


        
    return redirect(url_for('registrarse',
                                        ))


@app.route('/registrarse')
def registrarse():

    session.pop('loggedin', None)
    session.pop('id_autor', None)
    session.pop('correo', None)
    session.pop('id_administrador',None)
   
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

@app.route('/editar_categoria', methods =['GET', 'POST'])
@login_required
def editar_categoria():
    if session['loggedin'] == True & session['id_administrador'] == 1 :
        _nombre = request.form['nombre']
        _id_categoria = request.form['id_categoria']
        sql="UPDATE `categoria` SET `categoria`=%s  WHERE id_categoria=%s;"
        datos=(_nombre, _id_categoria)  # crea la sentencia sql
        conn=mysql.connect()
        cursor=conn.cursor()
        cursor.execute(sql,datos)               # ejecuta la sentencia sql 
        conn.commit()
        return redirect(url_for('panel_admin',
                                ))
    return redirect(url_for('index',
                                    ))
    
if __name__ == '__main__':
    #local
    #app.run(debug=True)
    #Produccion
    app.run(host='0.0.0.0', debug=True, port=8080)
        