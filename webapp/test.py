import csv
from flask import Flask, jsonify, render_template, request, redirect, url_for
import folium

app = Flask(__name__)

@app.route("/")
def homepage():
    mappa = folium.Map([45.465, 9.185], zoom_start=7)
    mappa.get_root().width = "800px"
    set_stazioni = set()
    with open("../database/dati/lombardia_qa/Stazioni_qualit__dell_aria_20240220.csv", "r") as file:
        lettore = csv.reader(file)
        next(lettore)
        for elem in lettore:
            if elem[3] not in set_stazioni:
                folium.Marker(location=[elem[13], elem[14]], icon=folium.Icon(color="green", icon="square-check", prefix="fa")).add_to(mappa)
                set_stazioni.add(elem[3])
    folium.GeoJson("../database/dati/lombardy.geojson").add_to(mappa)
    iframe = mappa.get_root()._repr_html_()
    return render_template("homepage.html", iframe=iframe)

if __name__ == '__main__':
    app.run(debug=True)