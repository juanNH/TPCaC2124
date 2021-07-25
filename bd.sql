use blog_cac2124;
DROP TABLE IF EXISTS articulo;
DROP TABLE IF EXISTS autor;
DROP TABLE IF EXISTS contacto;
DROP TABLE IF EXISTS administrador;
DROP TABLE IF EXISTS categoria;

CREATE TABLE administrador (
id_administrador INT AUTO_INCREMENT NOT NULL PRIMARY KEY,
tipo VARCHAR(255) NOT NULL);

CREATE TABLE categoria (
id_categoria INT(255) AUTO_INCREMENT NOT NULL PRIMARY KEY,
categoria VARCHAR(255) NOT NULL UNIQUE);

CREATE TABLE autor (
id_autor INT(255) AUTO_INCREMENT NOT NULL PRIMARY KEY,
nombre  VARCHAR(255) NOT NULL,
apellido VARCHAR(255) NOT NULL,
correo VARCHAR(255) NOT NULL UNIQUE,
password VARCHAR(255) NOT NULL,
id_administrador INT(255) NOT NULL DEFAULT 0,
FOREIGN KEY(id_administrador) REFERENCES administrador(id_administrador));

CREATE TABLE contacto (
id_mensaje INT(255) AUTO_INCREMENT NOT NULL PRIMARY KEY,
email VARCHAR(255) NOT NULL,
asunto VARCHAR(255) NOT NULL,
mensaje VARCHAR(1000) NOT NULL,
id_administrador INT(255) NOT NULL DEFAULT 1,
FOREIGN KEY(id_administrador) REFERENCES administrador(id_administrador));

CREATE TABLE articulo (
id_articulo INT(255) AUTO_INCREMENT NOT NULL PRIMARY KEY,
titulo VARCHAR(255) NOT NULL UNIQUE,
contenido VARCHAR(10000) NOT NULL,
fecha DATETIME NOT NULL,
imagen VARCHAR(1000) NOT NULL,
fecha_edicion DATETIME NOT NULL,
id_categoria INT(255) NOT NULL,
id_autor INT(255) NOT NULL,
FOREIGN KEY(id_categoria) REFERENCES categoria(id_categoria),
FOREIGN KEY(id_autor) REFERENCES autor(id_autor));