
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from flaskext.mysql import MySQL
from datetime import datetime
import os
app = Flask(__name__)

#conexion a la base de datos
mysql = MySQL()
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'blog_cac2124'
mysql.init_app(app)
class nav:
    def nav_categorias():
        sql= "SELECT * FROM `blog_cac2124`.`categoria`"
        conn=mysql.connect()
        cursor=conn.cursor()
        cursor.execute(sql) 
        nav_categorias = cursor.fetchall()  
        conn.commit()

        return nav_categorias


# vista index
@app.route('/,<id_categoria>')
@app.route('/')
def index(id_categoria = None):
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

    return render_template('index.html',articulos = articulos,categorias=categorias)

# vista registro
@app.route('/registro')
def registro():
    autor= "SELECT id_autor, CONCAT(nombre,' ',apellido) FROM `blog_cac2124`.`autor`"
    conn=mysql.connect()
    cursor=conn.cursor()
    cursor.execute(autor) 
    autores = cursor.fetchall()  
    conn.commit()


    categorias = nav.nav_categorias()
    return render_template('registro.html',autores = autores,categorias=categorias)
#crear publicacion
@app.route('/store', methods = ['POST'])
def storage():
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

@app.route('/panel')
def panel():
    sql= "SELECT * FROM `blog_cac2124`.`articulo`"

    conn=mysql.connect()
    cursor=conn.cursor()
    cursor.execute(sql) 
    articulos = cursor.fetchall()  
    conn.commit()

    categorias = nav.nav_categorias()
    return render_template('panel.html',articulos = articulos,categorias=categorias)

@app.route('/eliminar/<id_articulo>')
def eliminar(id_articulo):
    
    sql = "DELETE FROM `blog_cac2124`.`articulo` WHERE id_articulo = %s;"
    conn = mysql.connect()
    cursor = conn.cursor()
    datos = (id_articulo)
    cursor.execute(sql,(datos))

    cursor.execute(sql,(id))
    conn.commit()
    return redirect(url_for('panel'))

@app.route('/editar/<id_articulo>')
def editar(id_articulo):
    categorias = nav.nav_categorias()
    return redirect(url_for('panel'),categorias=categorias)

if __name__ == '__main__':
    app.run(debug=True)