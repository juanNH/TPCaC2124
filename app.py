from flask import Flask,flash , redirect, url_for,render_template, request
from datetime import datetime
from flask_mysqldb import MySQL
app = Flask(__name__)

@app.route('/')
def index():

    return render_template('index.html')



if __name__ == '__main__':
    app.run(debug=True)