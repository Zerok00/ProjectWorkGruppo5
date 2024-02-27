from flask import Flask, render_template, Response, stream_template
import calcolo_sensori_stazioni
import AQI_version2
import folium

app = Flask(__name__)

@app.route("/")
def homepage():             #calcolare i valori AQI
    dati_stazioni = calcolo_sensori_stazioni.calcolo_stazioni()
    mappa = folium.Map([45.51, 9.75], zoom_start=7)
    mappa.get_root().width = "100%"
    mappa.get_root().height = "100%"
    for elem in dati_stazioni:
        diz_per_funzione = {}
        for sensore in dati_stazioni[elem]["lista_sensori"]: #conversione nomi per funzione
            if sensore[1] == "PM10 (SM2005)":
                diz_per_funzione["PM10"] = sensore[2]
            elif sensore[1] == "Particelle sospese PM2.5":
                diz_per_funzione["PM2.5"] = sensore[2]
            elif sensore[1] == "Biossido di Azoto":
                diz_per_funzione["NO2"] = sensore[2]
            elif sensore[1] == "Monossido di Carbonio":
                diz_per_funzione["CO"] = sensore[2]
            elif sensore[1] == "Ozono":
                diz_per_funzione["O3 1-hr"] = sensore[2]
            elif sensore[1] == "Biossido di Zolfo":
                diz_per_funzione["PM2.5"] = sensore[2]
        aqi = AQI_version2.aqi_function(diz_per_funzione)
        aqi["massimo"] = round(aqi["massimo"])
        if aqi["massimo"] == "NULL":           #calcola markers
            folium.Marker(location=[dati_stazioni[elem]["coord"][0], dati_stazioni[elem]["coord"][1]],
                          icon=folium.Icon(color="lightgray", icon="xmark", prefix="fa"),
                          tooltip="Non rilevato").add_to(mappa)
        else:
            if aqi["massimo"]<=50:
                folium.Marker(location=[dati_stazioni[elem]["coord"][0], dati_stazioni[elem]["coord"][1]],
                              icon=folium.Icon(color="blue", icon="face-smile-beam", prefix="fa"),
                              tooltip=f"Good\nAQI:{aqi["massimo"]}").add_to(mappa)
            elif aqi["massimo"]>= 51 and aqi["massimo"]<= 100:
                folium.Marker(location=[dati_stazioni[elem]["coord"][0], dati_stazioni[elem]["coord"][1]],
                              icon=folium.Icon(color="green", icon="face-grin-wide", prefix="fa"),
                              tooltip=f"Moderate\nAQI:{aqi["massimo"]}").add_to(mappa)
            elif aqi["massimo"]>= 101 and aqi["massimo"]<= 150:
                folium.Marker(location=[dati_stazioni[elem]["coord"][0], dati_stazioni[elem]["coord"][1]],
                              icon=folium.Icon(color="orange", icon="face-meh", prefix="fa"),
                              tooltip=f"Unhealthy for Sensitive Groups\nAQI:{aqi["massimo"]}").add_to(mappa)
            elif aqi["massimo"]>= 151 and aqi["massimo"] <= 200:
                folium.Marker(location=[dati_stazioni[elem]["coord"][0], dati_stazioni[elem]["coord"][1]],
                              icon=folium.Icon(color="red", icon="face-frown-open", prefix="fa"),
                              tooltip=f"Unhealthy\nAQI:{aqi["massimo"]}").add_to(mappa)
            elif aqi["massimo"]>= 201 and aqi["massimo"]<= 300:
                folium.Marker(location=[dati_stazioni[elem]["coord"][0], dati_stazioni[elem]["coord"][1]],
                              icon=folium.Icon(color="purple", icon="face-frown", prefix="fa"),
                              tooltip=f"Very Unhealthy\nAQI:{aqi["massimo"]}").add_to(mappa)
            elif aqi["massimo"] >= 301:
                folium.Marker(location=[dati_stazioni[elem]["coord"][0], dati_stazioni[elem]["coord"][1]],
                              icon=folium.Icon(color="darkred", icon="face-sad-tear", prefix="fa"),
                              tooltip=f"Hazardous\nAQI:{aqi["massimo"]}").add_to(mappa)
    folium.GeoJson("../migration/database_sql/data/lombardy.geojson").add_to(mappa)
    iframe = mappa.get_root()._repr_html_()
    return render_template("index.html", iframe=iframe)

    #return Response(stream_template('index.html', iframe=iframe))
if __name__ == '__main__':
    app.run(debug=True)