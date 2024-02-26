def aqi_function(conc:dict):
    epa_tables = [

        {"AQI Range": [0.0, 50.0], "PM10": [0.0, 54.], "PM2.5": [0.0, 9.0], "O3 1-hr":[0.0, 54.], "CO":[0.0, 4.4],
         "SO2": [0.0, 35.0], "NO2": [0.0, 53.0], "Description": "Good"},

        {"AQI Range": [51.0, 100.0], "PM10": [55., 154.], "PM2.5": [9.1, 35.4], "O3 1-hr":[55.0, 70.], "CO": [4.5, 9.4],
         "SO2": [36.0, 75.0], "NO2": [54.0, 100.0], "Description": "Moderate"},

        {"AQI Range": [101.0, 150.0], "PM10": [155.0, 254.0], "PM2.5": [35.5, 55.4], "O3 1-hr": [125.0, 164.0],
         "CO": [9.5, 12.4], "SO2": [76.0, 185.0], "NO2": [101.0, 360.0], "Description": "Unhealthy for Sensitive Groups"},

        {"AQI Range": [151., 200.0], "PM10": [255.0, 354.0], "PM2.5": [55.5, 125.4], "O3 1-hr": [165.0, 204.0],
         "CO": [12.5, 15.4], "SO2": [186.0, 304.0], "NO2": [361.0, 649.0], "Description": "Unhealthy"},

        {"AQI Range": [201., 300.0], "PM10": [355.0, 424.0], "PM2.5": [125.5, 225.4], "O3 1-hr": [205.0, 404.0],
         "CO": [15.5, 30.4], "SO2": [305.0, 604.0], "NO2": [650.0, 1249.0], "Description": "Very Unhealthy"},

        {"AQI Range": [301., 500.], "PM10": [425., 604.0], "PM2.5": [225.5, 325.4], "O3 1-hr": [405., 604.0], "CO": [30.5, 50.4],
         "SO2": [605., 1004.0], "NO2": [1250.0, 2049.0], "Description": "Hazardous"}

    ]

    pollutants = {
        "PM10": {"name": "PM10 (SM2005)", "description": "Particulate Matter (≤10µm)"},
        "PM2.5": {"name": "Particelle sospese PM2.5", "description": "Particulate Matter (≤2.5µm)"},
        "O3 1-hr": {"name": "Ozono", "description": "Ozone (1-hour)"},
        "CO": {"name": "CO", "Monossido di Carbonio": "Carbon Monoxide"},
        "SO2": {"name": "SO2", "Biossido di Zolfo": "Sulfur Dioxide"},
        "NO2": {"name": "NO2", "Biossido di Azoto": "Nitrogen Dioxide"}
    }


    #conversione O3 da ppb a mug/m3
    for i in range(len(epa_tables)):
        if epa_tables[i]["O3 1-hr"] != "-":
            epa_tables[i]["O3 1-hr"][0] = epa_tables[i]["O3 1-hr"][0]*2.030
            epa_tables[i]["O3 1-hr"][1] = epa_tables[i]["O3 1-hr"][1]*2.030
        #print(epa_tables[i]["O3 1-hr"])

    # conversione CO da ppb a mmg/m3    !!!!!!!!!!ATTENZIONE!!!!!!!!!! milligrammi
    for i in range(len(epa_tables)):
        if epa_tables[i]["CO"] != "-":
            epa_tables[i]["CO"][0] = epa_tables[i]["CO"][0] * 1.185
            epa_tables[i]["CO"][1] = epa_tables[i]["CO"][1] * 1.185

    # conversione NO2 ppb a mug/m3
    for i in range(len(epa_tables)):
        if epa_tables[i]["NO2"] != "-":
            epa_tables[i]["NO2"][0] = epa_tables[i]["NO2"][0] * 1.946
            epa_tables[i]["NO2"][1] = epa_tables[i]["NO2"][1] * 1.946

    # conversione SO2 da ppb a mug/m3
    for i in range(len(epa_tables)):
        if epa_tables[i]["SO2"] != "-":
            epa_tables[i]["SO2"][0] = epa_tables[i]["SO2"][0] * 2.710
            epa_tables[i]["SO2"][1] = epa_tables[i]["SO2"][1] * 2.710

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

"""        elif conc[elem] > epa_tables[1][elem] and conc[elem] < epa_tables[1][elem]:

        elif conc[elem] > epa_tables[2][elem] and conc[elem] < epa_tables[2][elem]:

        elif conc[elem] > epa_tables[3][elem] and conc[elem] < epa_tables[3][elem]:

        elif conc[elem] > epa_tables[4][elem] and conc[elem] < epa_tables[4][elem]:

        elif conc[elem] > epa_tables[5][elem] and conc[elem] < epa_tables[5][elem]:"""


# example = {"PM10": 0 , "PM2.5": 58., "O3 1-hr": 56., "CO": 12.,
#          "SO2": 35.0, "NO2": 5.0 }
#
# print(aqi_function(example))
#print(max(aqi_function(example)))
