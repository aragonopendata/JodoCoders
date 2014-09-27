CRAs de Aragón
==============

Esta es una aplicación web desarrollada durante el **Jacathon 2014** organizado por [Aragón Open Data](http://opendata.aragon.es), que permite visualizar detalladamente los Colegios Rurales Agrupados (CRA) de Aragón.

Los datos de los CRA han sido extraídos de <http://opendata.aragon.es/catalogo/tablas-resumen-centros-rurales-agrupados-por-municipios> y <http://opendata.aragon.es/catalogo/centros-rurales-agrupados-cra>.


### Información Técnica
Nuestra app es una aplicación web Python usando el framework [Flask](http://flask.pocoo.org/), y MySQL como base de datos. Para gestionar las depencias, usamos el gestor de dependencias `pip`, que puedes instalar en Linux/MacOsX con:

```
curl https://bootstrap.pypa.io/get-pip.py > get-pip.py
sudo python get-pip.py
```

Recomendamos aislar el entorno de desarrollo Python con `virtualenvwrapper`:

```
sudo pip install virtualenvwrapper
mkdir $HOME/.virtualenvs
export WORKON_HOME=$HOME/.virtualenvs
export PROJECT_HOME=$HOME/jodocoders
source /usr/local/bin/virtualenvwrapper.sh
mkvirtualenv jodocoders
```
En caso de duda consultar la documentación oficial de [pip](https://pip.readthedocs.org/en/latest/) y de [virtualenvwrapper](http://virtualenvwrapper.readthedocs.org/en/latest/).

Antes de instalar las librerías Python requeridas, necesitas instalar MySQL en tu sistema:

Ejemplo Ubuntu: `sudo apt-get install mysql-server mysql-client libmysqlclient-dev`

Ejemplo MacOSX, con [Homebrew](http://brew.sh/): `brew install mysql`

Después, hay que crear e importar la base de datos a MySQL, en este caso con el original nombre de 'Datos':

```
echo "CREATE DATABASE Datos" | mysql -uTuUsuario -pTuPassword
mysql -uTuUsuario -p Datos < data/datos.sql
```
No olvides copiar el fichero `settings.py.example`a `settings.py`con tus datos de conexión a base de datos.

Para instalar las dependencias de las librerías Python:

`pip install -r requirements.txt`


### Notas
El script `import_geodata.py` se usó para añadir las coordenadas (Latitud y Longitud) de los CRA al fichero SQL (`data/datos.sql`), puesto que las fuentes de datos no lo incluían (una fuente incluye los datos detallados de alumnos anuales de los CRA, y la otra las direcciones postales de los CRA).
