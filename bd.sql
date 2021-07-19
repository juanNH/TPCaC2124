# Creacion de tablas de la bd

CREATE TABLE articulo (
id_articulo INT(255) NOT NULL PRIMARY KEY,
titulo VARCHAR(255) NOT NULL UNIQUE,
contenido VARCHAR(1000) NOT NULL,
fecha DATETIME NOT NULL,
id_categoria INT(255) NOT NULL,
id_autor INT(255) NOT NULL,
FOREIGN KEY(id_categoria) REFERENCES categoria(id_categoria),
FOREIGN KEY(id_autor) REFERENCES autor(id_autor));

CREATE TABLE categoria (
id_categoria INT(255) NOT NULL PRIMARY KEY,
categoria VARCHAR(255) NOT NULL UNIQUE);

CREATE TABLE autor (
id_autor INT(255) NOT NULL PRIMARY KEY,
nombre  VARCHAR(255) NOT NULL,
apellido VARCHAR(255) NOT NULL,
correo VARCHAR(255) NOT NULL UNIQUE,
password VARCHAR(255) NOT NULL);
