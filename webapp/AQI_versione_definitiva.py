import calcolo_sensori_stazioni
import folium
epa_tables = [
    {"AQI Range": [0.0, 50.0], "PM10 (SM2005)": [0.0, 54.], "Particelle sospese PM2.5": [0.0, 9.0], "Ozono": [0.0, 54.],
     "Monossido di Carbonio": [0.0, 4.4],
     "Biossido di Zolfo": [0.0, 35.0], "Biossido di Azoto": [0.0, 53.0], "Description": "Good"},

    {"AQI Range": [51.0, 100.0], "PM10 (SM2005)": [55., 154.], "Particelle sospese PM2.5": [9.1, 35.4],
     "Ozono": [55.0, 70.], "Monossido di Carbonio": [4.5, 9.4],
     "Biossido di Zolfo": [36.0, 75.0], "Biossido di Azoto": [54.0, 100.0], "Description": "Moderate"},

    {"AQI Range": [101.0, 150.0], "PM10 (SM2005)": [155.0, 254.0], "Particelle sospese PM2.5": [35.5, 55.4],
     "Ozono": [125.0, 164.0],
     "Monossido di Carbonio": [9.5, 12.4], "Biossido di Zolfo": [76.0, 185.0], "Biossido di Azoto": [101.0, 360.0],
     "Description": "Unhealthy for Sensitive Groups"},

    {"AQI Range": [151., 200.0], "PM10 (SM2005)": [255.0, 354.0], "Particelle sospese PM2.5": [55.5, 125.4],
     "Ozono": [165.0, 204.0],
     "Monossido di Carbonio": [12.5, 15.4], "Biossido di Zolfo": [186.0, 304.0], "Biossido di Azoto": [361.0, 649.0],
     "Description": "Unhealthy"},

    {"AQI Range": [201., 300.0], "PM10 (SM2005)": [355.0, 424.0], "Particelle sospese PM2.5": [125.5, 225.4],
     "Ozono": [205.0, 404.0],
     "Monossido di Carbonio": [15.5, 30.4], "Biossido di Zolfo": [305.0, 604.0], "Biossido di Azoto": [650.0, 1249.0],
     "Description": "Very Unhealthy"},

    {"AQI Range": [301., 500.], "PM10 (SM2005)": [425., 604.0], "Particelle sospese PM2.5": [225.5, 325.4],
     "Ozono": [405., 604.0], "Monossido di Carbonio": [30.5, 50.4],
     "Biossido di Zolfo": [605., 1004.0], "Biossido di Azoto": [1250.0, 2049.0], "Description": "Hazardous"}
]

# Conversione O3 da ppb a µg/m³
for i in range(len(epa_tables)):
    if "Ozono" in epa_tables[i]:
        if epa_tables[i]["Ozono"] != "-":
            epa_tables[i]["Ozono"][0] *= 2.030
            epa_tables[i]["Ozono"][1] *= 2.030

# Conversione CO da ppb a µg/m³ (milligrammi)
for i in range(len(epa_tables)):
    if "Monossido di Carbonio" in epa_tables[i]:
        if epa_tables[i]["Monossido di Carbonio"] != "-":
            epa_tables[i]["Monossido di Carbonio"][0] *= 1.185
            epa_tables[i]["Monossido di Carbonio"][1] *= 1.185

# Conversione NO2 da ppb a µg/m³
for i in range(len(epa_tables)):
    if "Biossido di Azoto" in epa_tables[i]:
        if epa_tables[i]["Biossido di Azoto"] != "-":
            epa_tables[i]["Biossido di Azoto"][0] *= 1.946
            epa_tables[i]["Biossido di Azoto"][1] *= 1.946

# Conversione SO2 da ppb a µg/m³
for i in range(len(epa_tables)):
    if "Biossido di Zolfo" in epa_tables[i]:
        if epa_tables[i]["Biossido di Zolfo"] != "-":
            epa_tables[i]["Biossido di Zolfo"][0] *= 2.710
            epa_tables[i]["Biossido di Zolfo"][1] *= 2.710


def aqi_function(conc:dict):

    aqi = {}
    for elem in conc.keys():
        for i in range(len(epa_tables)):
            if conc[elem] >= epa_tables[i][elem][0] and conc[elem] <= epa_tables[i][elem][1]:
                i_high, i_low = epa_tables[i]["AQI Range"][1], epa_tables[i]["AQI Range"][0]
                c_high, c_low = epa_tables[i][elem][1], epa_tables[i][elem][0]
                break
        index = (( i_high - i_low)/(c_high - c_low))*conc[elem] + i_low
        aqi[elem] = index
        aqi["massimo"] = max(aqi.values())

    return aqi

def calcolo_markers():
    dati_stazioni = calcolo_sensori_stazioni.calcolo_stazioni()
    lista_marker = []
    for elem in dati_stazioni:
        diz_per_funzione = {}
        for sensore in dati_stazioni[elem]["lista_sensori"]:  # conversione nomi per funzione
            if sensore[1] == "PM10 (SM2005)":
                diz_per_funzione[sensore[1]] = sensore[2]
            elif sensore[1] == "Particelle sospese PM2.5":
                diz_per_funzione[sensore[1]] = sensore[2]
            elif sensore[1] == "Biossido di Azoto":
                diz_per_funzione[sensore[1]] = sensore[2]
            elif sensore[1] == "Monossido di Carbonio":
                diz_per_funzione[sensore[1]] = sensore[2]
            elif sensore[1] == "Ozono":
                diz_per_funzione[sensore[1]] = sensore[2]
            elif sensore[1] == "Biossido di Zolfo":
                diz_per_funzione[sensore[1]] = sensore[2]
        aqi = aqi_function(diz_per_funzione)
        aqi["massimo"] = round(aqi["massimo"])
        if aqi["massimo"] == "NULL":  # coord: 0-1 color:2 icon:3 prefix:4 tooltip:5
            lista_marker.append((dati_stazioni[elem]["coord"][0], dati_stazioni[elem]["coord"][1], "lightgray", "xmark", "fa", "Non rilevato"))
        else:
            if aqi["massimo"] <= 50:
                lista_marker.append((dati_stazioni[elem]["coord"][0], dati_stazioni[elem]["coord"][1], "blue", "face-smile-beam", "fa", f"Good\nAQI:{aqi["massimo"]}"))
            elif aqi["massimo"] >= 51 and aqi["massimo"] <= 100:
                lista_marker.append((dati_stazioni[elem]["coord"][0], dati_stazioni[elem]["coord"][1], "green", "face-grin-wide", "fa", f"Moderate\nAQI:{aqi["massimo"]}"))
            elif aqi["massimo"] >= 101 and aqi["massimo"] <= 150:
                lista_marker.append((dati_stazioni[elem]["coord"][0], dati_stazioni[elem]["coord"][1], "orange", "face-meh","fa", f"Unhealthy for Sensitive Groups\nAQI:{aqi["massimo"]}"))
            elif aqi["massimo"] >= 151 and aqi["massimo"] <= 200:
                lista_marker.append((dati_stazioni[elem]["coord"][0], dati_stazioni[elem]["coord"][1], "red", "face-frown-open","fa", f"Unhealthy\nAQI:{aqi["massimo"]}"))
            elif aqi["massimo"] >= 201 and aqi["massimo"] <= 300:
                lista_marker.append((dati_stazioni[elem]["coord"][0], dati_stazioni[elem]["coord"][1], "purple", "face-frown", "fa", f"Very Unhealthy\nAQI:{aqi["massimo"]}"))
            elif aqi["massimo"] >= 301:
                lista_marker.append((dati_stazioni[elem]["coord"][0], dati_stazioni[elem]["coord"][1], "darkred", "face-sad-tear", "fa", f"Hazardous\nAQI:{aqi["massimo"]}"))
    return lista_marker

def crea_mappa():
    mappa = folium.Map([45.51, 9.75], zoom_start=8, prefer_canvas=True)
    mappa.get_root().width = "100%"
    mappa.get_root().height = "100%"
    lista_marker = calcolo_markers()
    for elem in lista_marker:
        folium.Marker(location=[elem[0], elem[1]],
                      icon=folium.Icon(color=elem[2], icon=elem[3], prefix=elem[4]),
                      tooltip=elem[5]).add_to(mappa)
    folium.GeoJson("../migration/database_sql/data/lombardy.geojson").add_to(mappa)
    return mappa
# example = {"PM10 (SM2005)": 55.5, "Particelle sospese PM2.5": 58., "Ozono": 56., "Monossido di Carbonio": 12.,
#            "Biossido di Zolfo": 35.0, "Biossido di Azoto": 5.0}
#
#
# print(aqi_function(example))

