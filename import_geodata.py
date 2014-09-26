import requests
import time
import json


url_centros = 'http://idearagon.aragon.es/GeoserverWFS?service=WFS&request=getFeature&typeName=IDEAragon:CARTO.V206_CENTROS_EDUCATIVOS&srsName=epsg:4326&outputFormat=json'

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
    f = open('centros.json')
    j = json.loads(f.read())
    for feature in j['features']:
        name = feature['properties']['NOMBRE_CEN']
        lon = feature['geometry']['coordinates'][0]
        lat = feature['geometry']['coordinates'][1]
        print name
        print lon, lat


if __name__ == '__main__':
    # fetch_centros(url_centros)
    load_centros()
