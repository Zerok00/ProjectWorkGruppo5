import csv
from flask import Flask, jsonify, render_template, request, redirect, url_for
import folium

app = Flask(__name__)

@app.route("/")
def homepage():             #calcolare i valori AQI
    mappa = folium.Map([45.51, 9.75], zoom_start=8)
    mappa.get_root().width = "800px"
    set_stazioni = set()
    with open("../database/dati/lombardia_qa/accentra.CSV", "r") as file:
        lettore = csv.reader(file, delimiter=";")
        next(lettore)
        for elem in lettore:
            coord = elem[9].strip("()").split(",")
            if elem[3] not in set_stazioni:
                if elem[5] == "NULL":
                    folium.Marker(location=[float(coord[0]), float(coord[1])],
                                  icon=folium.Icon(color="lightgray", icon="xmark", prefix="fa"),
                                  popup="Non rilevato").add_to(mappa)
                    set_stazioni.add(elem[3])
                else:
                    if int(elem[5])<=50:
                        folium.Marker(location=[float(coord[0]), float(coord[1])],
                                      icon=folium.Icon(color="blue", icon="face-smile-beam", prefix="fa"),
                                      popup="Good").add_to(mappa)
                        set_stazioni.add(elem[3])
                    elif int(elem[5])>= 51 and int(elem[5])<= 100:
                        folium.Marker(location=[float(coord[0]), float(coord[1])],
                                      icon=folium.Icon(color="green", icon="face-grin-wide", prefix="fa"),
                                      popup="Moderate").add_to(mappa)
                        set_stazioni.add(elem[3])
                    elif int(elem[5])>= 101 and int(elem[5])<= 150:
                        folium.Marker(location=[float(coord[0]), float(coord[1])],
                                      icon=folium.Icon(color="orange", icon="face-meh", prefix="fa"),
                                      popup="Unhealthy for Sensitive Groups").add_to(mappa)
                        set_stazioni.add(elem[3])
                    elif int(elem[5]) >= 151 and int(elem[5]) <= 200:
                        folium.Marker(location=[float(coord[0]), float(coord[1])],
                                      icon=folium.Icon(color="red", icon="face-frown-open", prefix="fa"),
                                      popup="Unhealthy").add_to(mappa)
                        set_stazioni.add(elem[3])
                    elif int(elem[5])>= 201 and int(elem[5])<= 300:
                        folium.Marker(location=[float(coord[0]), float(coord[1])],
                                      icon=folium.Icon(color="purple", icon="face-frown", prefix="fa"),
                                      popup="Very Unhealthy").add_to(mappa)
                        set_stazioni.add(elem[3])
                    elif int(elem[5]) >= 301:
                        folium.Marker(location=[float(coord[0]), float(coord[1])],
                                      icon=folium.Icon(color="darkred", icon="face-sad-tear", prefix="fa"),
                                      popup="Hazardous").add_to(mappa)
                        set_stazioni.add(elem[3])
    folium.GeoJson("../database/dati/lombardy.geojson").add_to(mappa)
if __name__ == '__main__':
    app.run(debug=True)