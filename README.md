JodoCoders
==========

Esta es una aplicación web desarrollada durante el **Jacathon** 2014 organizado por [Aragón Open Data](http://opendata.aragon.es).

Los datos de los CRA han sido extraídos de <http://opendata.aragon.es/catalogo/tablas-resumen-centros-rurales-agrupados-por-municipios> y <http://opendata.aragon.es/catalogo/centros-rurales-agrupados-cra>.

Para instalar las dependencias de las librerías python:

pip install -r requirements.txt

Después, hay que importar la base de datos a MySQL, en este caso con el original nombre de 'Datos'. 

mysql -utuusuario -p Datos < data/datos.sql
