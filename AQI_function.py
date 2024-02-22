def aqi_function(conc:dict):
    epa_tables = [

        {"AQI Range": [0.0, 50.0], "PM10": [0.0, 54.], "PM2.5": [0.0, 9.0], "O3 1-hr":[ "CO": [0.0, 4.4],
         "SO2": [0.0, 35.0], "NO2": [0.0, 53.0], "Description": "Good"},

        {"AQI Range": [51.0, 100.0], "PM10": [55., 154.], "PM2.5": [9.1, 35.4], "O3 1-hr": "-", "CO": [4.5, 9.4],
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

    #conversione O3 da ppb a mug/m3
    for i in range(len(epa_tables)):
        if epa_tables[i]["O3 1-hr"] != "-":
            epa_tables[i]["O3 1-hr"][0] = epa_tables[i]["O3 1-hr"][0]*2.030
            epa_tables[i]["O3 1-hr"][1] = epa_tables[i]["O3 1-hr"][1]*2.030
        print(epa_tables[i]["O3 1-hr"])

    for elem in conc.keys():
        if conc > epa_tables[0] and conc < epa_tables[1]
        elif conc > epa_tables[0] and conc < epa_tables[1]
        elif conc > epa_tables[0] and conc < epa_tables[1]
        elif conc > epa_tables[0] and conc < epa_tables[1]

example = {"PM10": 53.5 , "PM2.5": 588., "O3 1-hr": 656., "CO": 12.,
         "SO2": 35.0, "NO2": 53.0 }

aqi_function(example)

