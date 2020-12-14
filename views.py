# -*- coding: utf-8 -*-

from flask import Flask
from flask import render_template
import config as configuracion
from flask import request
import json
import sys  
import os.path
from app import app
from urllib import url2pathname
from urllib import urlopen
from decimal import Decimal

def _load_settings(path):  
	print "Loading configuration from %s" % (path)  
	settings = {}  
	execfile(path, globals(), settings)  
	for setting in settings:  
		globals()[setting] = settings[setting]  
  
#mysql = MySQL()
#_load_settings("app/config.py")  
#mysql.init_app(app)


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

def __total_centers_by_year(year, cursor):
	query = 'select count(DISTINCT id_CRA) FROM Educ_cra_evol where Año=%s'
	cursor.execute(query, (year,))
	total_centers = int(cursor.fetchone()[0])
	return total_centers
	
def __total_students_cra_by_year(cra, year, cursor):
	query = "SELECT SUM(tres_años), SUM(cuatro_años), SUM(cinco_años), SUM(primero), SUM(segundo), SUM(tercero), SUM(cuarto), SUM(quinto), SUM(sexto), SUM(primero_eso), SUM(segundo_eso), SUM(total) FROM public.educ_cra_evol WHERE id_cra ='"+str(cra)+"' AND año ='"+str(year.strip())+ "' GROUP BY nombre_del_cra, año ORDER BY nombre_del_cra, año ASC;"
	cursor.execute(query)
	resp = []
	for row in cursor:
		resp.append(
			{
				'3_años': int(row[0]),
				'4_años': int(row[1]),
				'5_años': int(row[2]),
				'primaria1': int(row[3]),
				'primaria2': int(row[4]),
				'primaria3': int(row[5]),
				'primaria4': int(row[6]),
				'primaria5': int(row[7]),
				'primaria6': int(row[8]),
				'secundaria1': int(row[9]),
				'secundaria2': int(row[10]),
				'total': int(row[11])
				})
	return resp
	



@app.route("/")
def index():
	#hacer las cosas que quieras
	year = request.args.get('year', '2018')
	year = year + '/' + str(int(year) + 1)
	cursor = configuracion.conexion().cursor()
	total_students = __total_students_by_year(year, cursor), 
	total_centers = __total_centers_by_year(year, cursor), 
	total_places = __total_places_by_year(year, cursor)
	
	total_students_aragon = totalAlumnosAragon(cursor)
	
	total_datos_CRAS = totalDatosTrayectosCRAS(175, total_students[0], cursor)
	
	print 'Total datos Cras'+str(total_datos_CRAS)

	estimaciones_dias=deDiasAEstimaciones(total_datos_CRAS['tiempoTotal'])
	estimaciones_kms=deKMaEspacio(total_datos_CRAS['distanciaTotal'])


	cursor.close()

	return render_template('index.html', total_students=total_students[0], total_centers=total_centers[0], total_places=total_places, total_students_aragon=total_students_aragon, total_datos_CRAS=total_datos_CRAS, estimaciones_dias=estimaciones_dias, estimaciones_kms=estimaciones_kms, course=year)





@app.route("/evolucion-alumnos")
def evolucionAlumnos():
	cursor = configuracion.conexion().cursor()
	
	year = '2018/2019'
	return render_template('evolucion.html', total_students=__total_students_by_year(year, cursor), total_centers=__total_centers_by_year(year, cursor), total_places=__total_places_by_year(year, cursor))

@app.route("/statistics")
def statistics():
	year = request.args.get('year', '2018')
	year = year + '/' + str(int(year) + 1)
	cursor = configuracion.conexion().cursor()
	statistics = { 'total_students': __total_students_by_year(year, cursor), 
		'total_centers': __total_centers_by_year(year, cursor), 
		'total_places': __total_places_by_year(year, cursor)
	}
	
	cursor.close()
	return json.dumps(statistics)

@app.route("/team")
def team():
	return render_template('team.html')

@app.route("/cras")
def cras():
	year = request.args.get('year', '2018')
	year = year + '/' + str(int(year) + 1)
	cursor = configuracion.conexion().cursor()
	query = 'select c.Id_cra, c.CRA, c.Lat, c.Lon, c.Id_mun, c.Municipio, e.Id_mun, e.municipio_sede_del_CRA, m.Lat, m.Lon, e.Total from Educ_cra c join Educ_cra_evol e on c.Id_cra=e.Id_cra join A_municipios m on e.Id_mun=m.Id_mun where Año=%s;'
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
	cursor.close()
	return json.dumps(cras)

@app.route("/students_by_year")
def students_by_year():
	cursor = configuracion.conexion().cursor()
	query = 'select sum(total), Año FROM Educ_cra_evol group by Año ORDER BY Año'
	cursor.execute(query)
	resp = []
	for row in cursor:
		resp.append({'students': int(row[0]),
				'year': row[1],
				})
	cursor.close()
	return json.dumps(resp)

@app.route('/show_municipality/<id>')
def show_municipality(id):
	cursor = configuracion.conexion().cursor()
	#query = 'select sum(total), Año, `Municipio sede del CRA` FROM Educ_cra_evol where Id_mun =%s group by Año'
	query = 'select sum(total), Año, municipio_sede_del_CRA FROM Educ_cra_evol where Id_mun =%s group by Año, municipio_sede_del_CRA ORDER BY Año'
	cursor.execute(query, (id,))
	resp = []
	for row in cursor:
		resp.append({'students': int(row[0]),
				'year': row[1],
				'name': row[2],
				})
	cursor.close()
	return json.dumps(resp)
	
	
	
#método que devuelve las coordenadas de un CRAs en concreto y las coordenadas referentes a las poblaciones a las que pertenecen
#Para acceder a este método tendremos la url /trayectos_cras_anio/25&filtroAnio=2008/2009
@app.route('/trayectos_cras_anio/<cras_id>', methods=['GET', 'POST'])
def coordenadas_cras_anio(cras_id):
	print 'Entro en las coordenadas'
	filtroAnio = ''	
	#Capturamos los diferentes filtros
	if request.args.get('filtroAnio'):
		filtroAnio			= url2pathname(request.args.get('filtroAnio')).encode('utf-8')
	cursor = configuracion.conexion().cursor()
	query = "SELECT cra, lat, lon FROM public.educ_cra WHERE id_cra ='"+str(cras_id)+"';"
	cursor.execute(query)
	resultado = cursor.fetchone()
	if resultado is not None:
		cra={
			'name': resultado[0], #cra name
			'latlng': [resultado[1], resultado[2]], #cra lat lon
		}
	
		query = "SELECT a_municipios.municipio, a_municipios.lat , a_municipios.lon FROM public.a_municipios, public.educ_cra, public.educ_cra_evol WHERE   educ_cra.id_cra = educ_cra_evol.id_cra AND educ_cra_evol.id_mun = a_municipios.id_mun AND educ_cra.id_cra ='"+str(cras_id)+"' AND educ_cra_evol.año ='"+str(filtroAnio.strip())+ "' ORDER BY educ_cra.cra,educ_cra_evol.año;"
		print 'la query es '+ query
		cursor.execute(query)
		rutas=[]
		for row in cursor:
			municipality_cras = {
				'name_municipity': row[0],
				'latlng': [row[1], row[2]]
			}
			rutas.append(municipality_cras)
		cursor.close()
		devolver = {
			'cra':cra,
			'trayectos':rutas,
			'year':filtroAnio.strip()
		}
		return json.dumps(devolver)
	else:
		return ''
	

#Método que nos da el total de alumnos por curso de cras
#Para acceder a este método tendremos la url /show_cras/25?filtroAnio=2008/2009
@app.route('/show_cras/<cras_id>', methods=['GET', 'POST'])
def show_cras(cras_id):
	filtroAnio = ''
	if request.args.get('filtroAnio'):
		filtroAnio			= url2pathname(request.args.get('filtroAnio')).encode('utf-8')
	
	cursor = configuracion.conexion().cursor()
	query = "SELECT nombre_del_cra, SUM(tres_años), SUM(cuatro_años), SUM(cinco_años), SUM(primero), SUM(segundo), SUM(tercero), SUM(cuarto), SUM(quinto), SUM(sexto), SUM(primero_eso), SUM(segundo_eso), SUM(total), año FROM public.educ_cra_evol WHERE id_cra ='"+str(cras_id)+"' AND año ='"+str(filtroAnio.strip())+ "' GROUP BY nombre_del_cra, año ORDER BY nombre_del_cra, año ASC;"
	cursor.execute(query)
	resp = []
	for row in cursor:
		resp.append(
			{
				'cras_name': row[0],
				'3_años': int(row[1]),
				'4_años': int(row[2]),
				'5_años': int(row[3]),
				'primaria1': int(row[4]),
				'primaria2': int(row[5]),
				'primaria3': int(row[6]),
				'primaria4': int(row[7]),
				'primaria5': int(row[8]),
				'primaria6': int(row[9]),
				'secundaria1': int(row[10]),
				'secundaria2': int(row[11]),
				'total': int(row[12]),
				'year': row[13]	
				})
	cursor.close()
	return json.dumps(resp)
	
#Método que nos da el total de alumnos por curso de cras
#Para acceder a este método tendremos la url /evolucion-alumnos/cra/25?filtroAnio=2008/2009
#Se modifica para que tan sólo ponga lo del ultimo anio
@app.route('/evolucion-alumnos/cra/<cras_id>')
def rutas(cras_id):
	filtroAnio = ''
	filtroAnio = '2018/2019'
	#if request.args.get('filtroAnio'):
		#filtroAnio			= url2pathname(request.args.get('filtroAnio')).encode('utf-8')
	cursor = configuracion.conexion().cursor()
	query = "SELECT cra, lat, lon, municipio FROM public.educ_cra WHERE id_cra ='"+str(cras_id)+"';"
	cursor.execute(query)
	resultado = cursor.fetchone()
	if resultado is not None:
		cra={
			'name': resultado[0].replace('á', 'aacute;').replace('é', 'eacute;').replace('í', 'iacute;').replace('ó', 'oacute;').replace('ú', 'uacute;').replace('Á', 'Aacute;').replace('É', 'Eacute;').replace('Í', 'Iacute;').replace('Ó', 'Oacute;').replace('Ú', 'Uacute;').replace('"', 'quot;').replace('<', 'lt;').replace('>', 'gt;').replace('¿', 'iquest;').replace('¡', 'iexcl;').replace('Ñ', 'Ntilde;').replace('ñ', 'ntilde;').replace('º', 'ordm;').replace('ª', 'ordf;').replace('#', 'almohadilla;').replace('ü', 'uuml;'), #cra name
			'latlng': [resultado[1], resultado[2]], #cra lat lon
			'municipio_sede_del_CRA': resultado[3].replace('á', 'aacute;').replace('é', 'eacute;').replace('í', 'iacute;').replace('ó', 'oacute;').replace('ú', 'uacute;').replace('Á', 'Aacute;').replace('É', 'Eacute;').replace('Í', 'Iacute;').replace('Ó', 'Oacute;').replace('Ú', 'Uacute;').replace('"', 'quot;').replace('<', 'lt;').replace('>', 'gt;').replace('¿', 'iquest;').replace('¡', 'iexcl;').replace('Ñ', 'Ntilde;').replace('ñ', 'ntilde;').replace('º', 'ordm;').replace('ª', 'ordf;').replace('#', 'almohadilla;').replace('ü', 'uuml;'), #sede del cra
		}
		query = "SELECT a_municipios.municipio, a_municipios.lat , a_municipios.lon, educ_cra_evol.año FROM public.a_municipios, public.educ_cra, public.educ_cra_evol WHERE   educ_cra.id_cra = educ_cra_evol.id_cra AND educ_cra_evol.id_mun = a_municipios.id_mun AND educ_cra.id_cra ='"+str(cras_id)+"' AND educ_cra_evol.año =(SELECT MAX(año) FROM educ_cra_evol) ORDER BY educ_cra.cra,educ_cra_evol.año;"
		#print 'la query es '+ query
		cursor.execute(query)
		rutas=[]
		for row in cursor:
			municipality_cras = {
				'name_municipity': row[0].replace('á', 'aacute;').replace('é', 'eacute;').replace('í', 'iacute;').replace('ó', 'oacute;').replace('ú', 'uacute;').replace('Á', 'Aacute;').replace('É', 'Eacute;').replace('Í', 'Iacute;').replace('Ó', 'Oacute;').replace('Ú', 'Uacute;').replace('"', 'quot;').replace('<', 'lt;').replace('>', 'gt;').replace('¿', 'iquest;').replace('¡', 'iexcl;').replace('Ñ', 'Ntilde;').replace('ñ', 'ntilde;').replace('º', 'ordm;').replace('ª', 'ordf;').replace('#', 'almohadilla;').replace('ü', 'uuml;'),
				'latlng': [row[1], row[2]]
			}
			rutas.append(municipality_cras)
		year=row[3]

		query = "SELECT municipios_padron.poblacion_total FROM municipios_padron, public.a_municipios, public.educ_cra, public.educ_cra_evol WHERE   educ_cra.id_cra = educ_cra_evol.id_cra AND educ_cra_evol.id_mun = a_municipios.id_mun AND educ_cra_evol.id_mun = municipios_padron.id_mun AND educ_cra.id_cra ='"+str(cras_id)+"' AND educ_cra_evol.año =(SELECT MAX(año) FROM educ_cra_evol) ORDER BY educ_cra.cra,educ_cra_evol.año;"
		cursor.execute(query)
		padrones=[]
		for row in cursor:
			padrones.append(row[0])
		query="SELECT SUM(total) FROM educ_cra_evol WHERE id_cra="+str(cras_id)+" AND año =(SELECT MAX(año) FROM educ_cra_evol)"
		resultado = cursor.fetchone()
		total_estudiantes_CRAS=row[0]
		cursor.close()
		devolver = {
			'cra':cra,
			'trayectos':rutas,			
			'padrones':padrones,
			'total_estudiantes_CRAS':total_estudiantes_CRAS,
			'year':year
		}
	return render_template('trayectos.html', data=devolver)

#Esta vista será para scrapearla y sacar los datos del trayectos
#para acceder a este metodo tendremos que /scrapea_trayecto/?filtroCRA=1&filtroMuni=50199
@app.route('/scrapea_trayecto/', methods=['GET', 'POST'])
def rutas_para_scrapear():
	cursor = configuracion.conexion().cursor()
	filtroCRA = ''	
	#Capturamos los diferentes filtros
	if request.args.get('filtroCRA'):
		filtroCRA			= url2pathname(request.args.get('filtroCRA')).encode('utf-8')
	
	filtroMuni = ''	
	
	if request.args.get('filtroMuni'):
		filtroMuni			= url2pathname(request.args.get('filtroMuni')).encode('utf-8')

	query = "SELECT educ_cra.id_cra, educ_cra.cra, educ_cra.lat, educ_cra.lon,  a_municipios.id_mun, a_municipios.municipio, a_municipios.lat, a_municipios.lon, educ_cra_evol.año FROM public.educ_cra_evol, public.educ_cra, public.a_municipios WHERE educ_cra.id_cra = educ_cra_evol.id_cra AND a_municipios.id_mun = educ_cra_evol.id_mun  AND año = (SELECT MAX(año) FROM educ_cra_evol) AND educ_cra_evol.id_mun="+str(filtroMuni).strip()+" AND educ_cra_evol.id_cra="+str(filtroCRA).strip()+";"
	
	cursor.execute(query)
	resultado = cursor.fetchone()
	cursor.close()
	if resultado is not None:
		cra={
			'id': resultado[0],
			'name': resultado[1].replace('á', 'aacute;').replace('é', 'eacute;').replace('í', 'iacute;').replace('ó', 'oacute;').replace('ú', 'uacute;').replace('Á', 'Aacute;').replace('É', 'Eacute;').replace('Í', 'Iacute;').replace('Ó', 'Oacute;').replace('Ú', 'Uacute;').replace('"', 'quot;').replace('<', 'lt;').replace('>', 'gt;').replace('¿', 'iquest;').replace('¡', 'iexcl;').replace('Ñ', 'Ntilde;').replace('ñ', 'ntilde;').replace('º', 'ordm;').replace('ª', 'ordf;').replace('#', 'almohadilla;').replace('ü', 'uuml;'), 
			'latlng': [resultado[2], resultado[3]]
		}
		municipio={
			'id':resultado[4],
			'name': resultado[5].replace('á', 'aacute;').replace('é', 'eacute;').replace('í', 'iacute;').replace('ó', 'oacute;').replace('ú', 'uacute;').replace('Á', 'Aacute;').replace('É', 'Eacute;').replace('Í', 'Iacute;').replace('Ó', 'Oacute;').replace('Ú', 'Uacute;').replace('"', 'quot;').replace('<', 'lt;').replace('>', 'gt;').replace('¿', 'iquest;').replace('¡', 'iexcl;').replace('Ñ', 'Ntilde;').replace('ñ', 'ntilde;').replace('º', 'ordm;').replace('ª', 'ordf;').replace('#', 'almohadilla;').replace('ü', 'uuml;'), 
			'latlng': [resultado[6], resultado[7]]
		}
		datos={
			'origen':municipio,
			'destino':cra
		}
		return render_template('scrapeo.html', data=datos)
	else:
		return "No existe ese trayecto"
	

#Metodo que devuelve datos para un alumno en un cra desde un municipio
@app.route('/info_alumno_cra/', methods=['GET', 'POST'])
def info_alumno_cra():
	cursor = configuracion.conexion().cursor()
	filtroCRA = ''	
	#Capturamos los diferentes filtros
	if request.args.get('filtroCRA'):
		filtroCRA			= url2pathname(request.args.get('filtroCRA')).encode('utf-8')
	
	filtroMuni = ''	
	
	if request.args.get('filtroMuni'):
		filtroMuni			= url2pathname(request.args.get('filtroMuni')).encode('utf-8')

	query = "SELECT to_number(REPLACE(SUBSTRING(distancia from 1 for (char_length(distancia)-3)),',','.'), '99999.999'),\
	 to_number(REPLACE(SUBSTRING(tiempo_estimado from 1 for (char_length(tiempo_estimado)-19)),',','.'), '99999.999')/60,\
	  educ_cra_evol.año FROM public.educ_cra_evol, public.trayecto WHERE educ_cra_evol.id_mun = trayecto.id_mun AND \
	  educ_cra_evol.id_cra = trayecto.cra_id AND trayecto.año = (SELECT MAX(año) FROM public.trayecto) AND\
	   educ_cra_evol.año = (SELECT MAX(año) FROM public.educ_cra_evol) AND educ_cra_evol.id_cra="+str(filtroCRA).strip()+" AND  educ_cra_evol.id_mun="+str(filtroMuni).strip()+";"
	cursor.execute(query)
	resultado = cursor.fetchone()
	cursor.close()
	if resultado is not None:
		info_alumno_cra={
			'cra_id':str(filtroCRA).strip(),
			'id_mun':str(filtroMuni).strip(),
			'distancia':resultado[0],
			'tiempo_estimado':resultado[1]
		}
		return json.dumps(info_alumno_cra)
	else:
		return "No existe ese trayecto"

#Método que devuelve los datos de cada curso por municipio los estudiantes que han enviado a los cras
#Para acceder a este método tendremos la url /show_municipality_by_year/22054?filtroAnio=2008/2009
@app.route('/show_municipality_by_year/<municipality_id>', methods=['GET', 'POST'])
def show_municipality_year(municipality_id):
	filtroAnio = ''
	if request.args.get('filtroAnio'):
		filtroAnio			= url2pathname(request.args.get('filtroAnio')).encode('utf-8')
	cursor = configuracion.conexion().cursor()
	query = "SELECT municipio_sede_del_cra, nombre_del_cra, tres_años, cuatro_años, cinco_años, primero, segundo, tercero, cuarto, quinto, sexto, primero_eso, segundo_eso, total, año FROM public.educ_cra_evol WHERE id_mun ='"+str(municipality_id)+"' AND año ='"+str(filtroAnio.strip())+ "'  ORDER BY nombre_del_cra, año ASC;"
	cursor.execute(query)
	resp = []
	for row in cursor:
		resp.append(
			{
				'municipio': row[0],
				'cras_name': row[1],
				'3_años': int(row[2]),
				'4_años': int(row[3]),
				'5_años': int(row[4]),
				'primaria1': int(row[5]),
				'primaria2': int(row[6]),
				'primaria3': int(row[7]),
				'primaria4': int(row[8]),
				'primaria5': int(row[9]),
				'primaria6': int(row[10]),
				'secundaria1': int(row[11]),
				'secundaria2': int(row[12]),
				'total': int(row[13]),	
				'year': row[14]	
				})
	cursor.close()
	return json.dumps(resp)
	

#Método que devuelve los datos de cada curso por municipio los estudiantes que han enviado a los cras
#Para acceder a este método tendremos la url /show_aragon_year/?filtroAnio=2008/2009
@app.route('/show_aragon_year/', methods=['GET', 'POST'])
def show_aragon_year():
	filtroAnio = ''
	if request.args.get('filtroAnio'):
		filtroAnio			= url2pathname(request.args.get('filtroAnio')).encode('utf-8')
	cursor = configuracion.conexion().cursor()
	
	query = "SELECT SUM(tres_años), SUM(cuatro_años) , SUM(cinco_años), SUM(primero), SUM(segundo) , SUM(tercero) , SUM(cuarto) , SUM(quinto) , SUM(sexto) , SUM(primero_eso) , SUM(segundo_eso) , SUM(total)  FROM public.educ_cra_evol WHERE  año ='"+str(filtroAnio.strip())+ "';"
	
	total_students=__total_students_by_year(filtroAnio, cursor)
	total_centers=__total_centers_by_year(filtroAnio, cursor)
	total_places=__total_places_by_year(filtroAnio, cursor)
	
	cursor.execute(query)
	resp = []
	for row in cursor:
		resp.append(
			{
				'total_estudiantes': total_students,
				'total_centros_cra': total_centers,
				'total_municipios_cra': total_places,
				'3_años': int(row[0]),
				'4_años': int(row[1]),
				'5_años': int(row[2]),
				'primaria1': int(row[3]),
				'primaria2': int(row[4]),
				'primaria3': int(row[5]),
				'primaria4': int(row[6]),
				'primaria5': int(row[7]),
				'primaria6': int(row[8]),
				'secundaria1': int(row[9]),
				'secundaria2': int(row[10]),
				'total': int(row[11]),
				'year': filtroAnio	
				})
	cursor.close()
	return json.dumps(resp)


#Método que devuelve la información de un CRA en concreto, y de los municipios que  envían a gente
# para acceder a eta funcion /info_cra/25?filtroAnio=2008/2009
@app.route('/info_cra/<id_CRA>', methods=['GET', 'POST'])
def info_cra(id_CRA):
	filtroAnio = ''
	if request.args.get('filtroAnio'):
		filtroAnio			= url2pathname(request.args.get('filtroAnio')).encode('utf-8')
	cursor = configuracion.conexion().cursor()
	estudiantes_totales=__total_students_cra_by_year(id_CRA, filtroAnio, cursor)
	
	
	query = "SELECT cra, lat, lon, direccion, municipio FROM public.educ_cra WHERE id_cra ='"+str(id_CRA)+"';"
	cursor.execute(query)
	resultado = cursor.fetchone()
	if resultado is not None:
		cra={
			'name': resultado[0], #cra name
			'latlng': [resultado[1], resultado[2]], #cra lat lon
			'direccion':resultado[3],
			'municipio':resultado[4]
		}
		query = "SELECT a_municipios.municipio, a_municipios.lat , a_municipios.lon, tres_años, cuatro_años, cinco_años, primero, segundo, tercero, cuarto, quinto, sexto, primero_eso, segundo_eso, total FROM public.a_municipios, public.educ_cra, public.educ_cra_evol WHERE   educ_cra.id_cra = educ_cra_evol.id_cra AND educ_cra_evol.id_mun = a_municipios.id_mun AND educ_cra.id_cra ='"+str(id_CRA)+"' AND educ_cra_evol.año ='"+str(filtroAnio.strip())+ "' ORDER BY educ_cra.cra,educ_cra_evol.año;"
		print 'la query es '+ query
		cursor.execute(query)
		estudiantes_por_municipio=[]
		for row in cursor:
			estudiantes= {
				'3_años': int(row[3]),
				'4_años': int(row[4]),
				'5_años': int(row[5]),
				'primaria1': int(row[6]),
				'primaria2': int(row[7]),
				'primaria3': int(row[8]),
				'primaria4': int(row[9]),
				'primaria5': int(row[10]),
				'primaria6': int(row[11]),
				'secundaria1': int(row[12]),
				'secundaria2': int(row[13]),
				'total': int(row[14])
			}
			estudiantes_municipio = {
				'name_municipity': row[0],
				'latlng': [row[1], row[2]],
				'estudiantes':estudiantes
			}
			estudiantes_por_municipio.append(estudiantes_municipio)
		cursor.close()
		devolver = {
			'cra':cra,
			'estudiantes_totales': estudiantes_totales,
			'estudiantes_por_municipio':estudiantes_por_municipio,
			'year':filtroAnio.strip()
		}
		return json.dumps(devolver)
	

#Método que devuelve la información de un CRA con el total de sus estudiantes en los años
@app.route('/students_by_year_and_CRA/<id_CRA>')
def students_by_year_and_CRA(id_CRA):
	cursor = configuracion.conexion().cursor()
	query = 'SELECT Año, sum (total) FROM educ_cra_evol Where id_CRA='+str(id_CRA)+' GROUP BY año ORDER BY Año ASC'
	cursor.execute(query)
	resp = []
	for row in cursor:
		resp.append({'students': int(row[1]),
				'year': row[0],
				})
	cursor.close()
	return json.dumps(resp)
	
#Metodo que se le pasa por parametro de km a veces la distancia de tierra la luna o a marte en perihelio y afelio
#https://es.wikipedia.org/wiki/Luna
def deKMaEspacio(kilometros):
	devolver = {
		'luna':kilometros/384400,
		'toMadrid':kilometros/314, #Distancia Zaragoza - Madrid
		'marte_perihelio': kilometros/59000000 ,#Esto es cuando estan mas cerca que no ocurre muchas veces
		'marte_afelio':  kilometros/102000000 #Cuando estan lo mas lejos ambos planetas
	}

	return devolver

#Método que pasa de días a [tiempo_que_pasa_Para_que_daenerys_llegue_a_poniente, publicacion_del_sr_de_los_anillos, [anios, meses, días]] todo estimaciones
def deDiasAEstimaciones(dias):
	print'dias '+str(dias)+str(type(dias))

	toDaenerys = dias/7441
	toTolkien = dias/6155
	toTiempo= []
	anios = dias/365
	resto_dias=dias%365
	meses=resto_dias/30
	resto_dias=resto_dias%30
	tiempoExacto={
		'años':anios,
		'meses':meses,
		'dias':resto_dias
	}
	devolver= {
		'DaenerysToWesteros':toDaenerys, #Veces que pasa dividiendo por el tiempo que a Daenerys Targaryan  nacida de la Tormenta, La que no Arde, Rompedora de Cadenas, Madre de Dragones (que coñazo de mujer) tarda en llegar a poniente, si que llega, esperemos que se descacharre desde un dragon. En realidad se divide la fecha por el espacio de tiempo entre la publicación del primer libro 6/8/96 a una fecha estimada de que salga vientos de invierno (si llega) 20/12/2016
		'OneRingToDestroy':toTolkien, #Similar al anterior, veces que tardo en viajar el anillo unico desde la comarca a la montaña del destino. En realidad es similar  al anterior la fecha para dividir es desde la publicacion del hobbit a la de el señor de los anillos
		'tiempoExacto':tiempoExacto
	}
	return devolver

#Método que nos da el tiempo que invierten el total de almumnos de cras, se le meten por parametro los días lectivos que seran 175 y los viajes que hacen al día al cra que seran el de ida y vuelta
def totalDatosTrayectosCRAS(diaLectivos, viajesAlumnoCRAS, cursor):
	query = "SELECT SUM(to_number(REPLACE(SUBSTRING(distancia from 1 for (char_length(distancia)-3)),',','.'), '99999.999')*"+str(viajesAlumnoCRAS)+"*"+str(diaLectivos)+"*educ_cra_evol.total), SUM(to_number(REPLACE(SUBSTRING(tiempo_estimado from 1 for (char_length(tiempo_estimado)-19)),',','.'), '99999.999')*"+str(viajesAlumnoCRAS)+"*"+str(diaLectivos)+"*educ_cra_evol.total/60),  educ_cra_evol.año FROM public.educ_cra_evol, public.trayecto WHERE educ_cra_evol.id_mun = trayecto.id_mun AND educ_cra_evol.id_cra = trayecto.cra_id AND trayecto.año = (SELECT MAX(año) FROM public.trayecto) AND educ_cra_evol.año = (SELECT MAX(año) FROM public.educ_cra_evol) GROUP BY educ_cra_evol.año;"
	print 'La consulta para los totales es '+query
	cursor.execute(query)
	resultado = cursor.fetchone()
	if resultado is not None:
		devolver={
			'distanciaTotal': resultado[0], 
			'tiempoTotal': resultado[1]
		}
		return devolver
	else:
		return ''

#metodo que devuelveel total de los alumnos
def totalAlumnosAragon(cursor):
	query ="SELECT SUM(total_alumnos) FROM public.municipios_padron WHERE año=(SELECT MAX(año) FROM public.municipios_padron);"
	cursor.execute(query)
	totalAlumnos = int(cursor.fetchone()[0])
	return totalAlumnos

