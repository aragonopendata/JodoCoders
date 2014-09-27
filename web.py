# -*- coding: utf-8 -*-

from flask import Flask
from flask import render_template
from flaskext.mysql import MySQL
from flask import request
import json
import sys  
import os.path

app = Flask(__name__)

def _load_settings(path):  
    print "Loading configuration from %s" % (path)  
    settings = {}  
    execfile(path, globals(), settings)  
    for setting in settings:  
        globals()[setting] = settings[setting]  
  
mysql = MySQL()
_load_settings("settings.py")  
mysql.init_app(app)

def __total_students_by_year(year, cursor):
    query = 'select sum(total) FROM Educ_cra_evol where Año=%s'
    cursor.execute(query, (year,))
    total_students = int(cursor.fetchone()[0])
    return total_students

def __total_places_by_year(year, cursor):
    query = 'select count(*) FROM Educ_cra_evol where Año=%s'
    cursor.execute(query, (year,))
    total_places = int(cursor.fetchone()[0])
    return total_places

@app.route("/")
def index():
    cursor = mysql.connect().cursor()
    query = 'select count(*) FROM Educ_cra'
    cursor.execute(query)
    total_centers = int(cursor.fetchone()[0])
    year = '2013/2014'
    return render_template('index.html', total_students=__total_students_by_year(year, cursor), total_centers=total_centers, total_places=__total_places_by_year(year, cursor))

@app.route("/statistics")
def statistics():
    year = request.args.get('year', '2013')
    year = year + '/' + str(int(year) + 1)
    cursor = mysql.connect().cursor()
    query = 'select count(*) FROM Educ_cra'
    cursor.execute(query)
    total_centers = int(cursor.fetchone()[0])
    statistics = { 'total_students': __total_students_by_year(year, cursor), 
        'total_centers': total_centers, 
        'total_places': __total_places_by_year(year, cursor)
    }
    return json.dumps(statistics)

@app.route("/team")
def team():
    return render_template('team.html')

@app.route("/cras")
def cras():
    year = request.args.get('year', '2013')
    year = year + '/' + str(int(year) + 1)
    cursor = mysql.connect().cursor()
    query = 'select c.Id_cra, c.CRA, c.Lat, c.Lon, c.Id_mun, c.Municipio, e.Id_mun, e.`Municipio sede del CRA`, m.Lat, m.Lon, e.Total from Educ_cra c join Educ_cra_evol e on c.Id_cra=e.Id_cra join A_municipios m on e.Id_mun=m.Id_mun where Año=%s;'
    cursor.execute(query, (year,))
    cras_dict = {}
    for row in cursor:
        cra_id = row[0]
        if not cras_dict.has_key(cra_id):
            cra = {'id': row[0], #cra id
                'name': row[1], #cra name
                'latlng': [row[2], row[3]], #cra lat lon
                'place_id': int(row[4]), #cra municipality id
                'place': row[5], #cra municipality name
                'municipalities': []
               }
            cras_dict[cra_id] = cra
        cra = cras_dict[cra_id]
        municipality = {
                'id': int(row[6]), #mun id
                'name': row[7], #mun name
                'latlng': [row[8], row[9]], #mun lat lon
                'students': int(row[10])
                }
        cra['municipalities'].append(municipality)

    #convert dict into array and calculate total cra students
    cras = []
    for cra in cras_dict.values():
        cra['students'] = reduce(lambda total, mun:  total+mun['students'], cra['municipalities'], 0)
        cras.append(cra)
    return json.dumps(cras)

@app.route("/students_by_year")
def students_by_year():
    cursor = mysql.connect().cursor()
    query = 'select sum(total), Año FROM Educ_cra_evol group by Año'
    cursor.execute(query)
    resp = []
    for row in cursor:
        resp.append({'students': row[0],
                'year': row[1],
                })
    return json.dumps(resp)

@app.route('/show_municipality/<id>')
def show_municipality(id):
    cursor = mysql.connect().cursor()
    query = 'select sum(total), Año, `Municipio sede del CRA` FROM Educ_cra_evol where Id_mun =%s group by Año'
    cursor.execute(query, (id,))
    resp = []
    for row in cursor:
        resp.append({'students': row[0],
                'year': row[1],
                'name': row[2],
                })
    return json.dumps(resp)
    
    


if __name__ == "__main__":
    app.debug = True
    app.run()
