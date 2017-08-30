import requests
import time
import json
import config as configuracion

db = configuracion.conexion()




url_centros = 	'

# params = {
#         'api_key': my_key,
#         '_page': 4
#         }

def fetch_centros(url):
    print url
    # r = requests.get(url, params=params)
    r = requests.get(url)
    print r.status_code
    print r.text
    f = open('centros.json', 'w')
    # json = r.json()
    f.write(r.text.encode('utf-8'))
    f.close()

def load_centros():	
    cursor = db.cursor()
    f = open('centros.json')
    j = json.loads(f.read())
    for feature in j['features']:
        cra_id = int(feature['properties']['IDCENTRORC'])
        name = feature['properties']['NOMBRE_CEN']
        lon = feature['geometry']['coordinates'][0]
        lat = feature['geometry']['coordinates'][1]
        stmt = 'update Educ_cra set Lat=%s, Lon=%s where Cod_educacion=%s'
        cursor.execute(stmt, (lat, lon, cra_id))
    db.commit()
    cursor.close()
    f.close()

if __name__ == '__main__':
    # fetch_centros(url_centros)
    load_centros()
    db.close()




