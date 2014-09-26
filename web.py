from flask import Flask
from flask import render_template

import json

app = Flask(__name__)


@app.route("/")
def hello():
    return render_template('index.html')

@app.route("/team")
def team():
    return render_template('team.html')

@app.route("/cras")
def cras():
    cursor = mysql.connect().cursor()
    query = 'select Id_cra, CRA, Id_mun, Municipio from Educ_cra'
    cursor.execute(query)
    cras = []
    for row in cursor:
        cra = {'cra_id': row[0],
                'cra_name': row[1],
                'mun_id': int(row[2]),
                'mun_name': row[3]
                }
        cras.append(cra)
    return json.dumps(cras)


if __name__ == "__main__":
    app.debug = True
    app.run()
