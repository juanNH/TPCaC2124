
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

# vista index
@app.route('/')
def index():

    sql= "select * from `blog_cac2124`.`autor`"

    conn=mysql.connect()
    cursor=conn.cursor()
    cursor.execute(sql) 
    autores = cursor.fetchall()  
    conn.commit()

    return render_template('index.html',autores = autores)

# vista registro
@app.route('/registro')
def registro():
    autor= "select id_autor, CONCAT(nombre,' ',apellido) from `blog_cac2124`.`autor`"
    conn=mysql.connect()
    cursor=conn.cursor()
    cursor.execute(autor) 
    autores = cursor.fetchall()  
    conn.commit()

    categorias= "select * from `blog_cac2124`.`categoria`" 
    conn=mysql.connect()
    cursor=conn.cursor()
    cursor.execute(categorias) 
    categorias = cursor.fetchall()  
    conn.commit()


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
    return redirect('/')





if __name__ == '__main__':
    app.run(debug=True)