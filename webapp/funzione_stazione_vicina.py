# importing geopy library
import pandas as pd
import numpy
#from geopy.geocoders import Nominatim
# Importing the geodesic module from the library
#from geopy.distance import geodesic

def calcolo_distanza(tupla):
    var = pd.read_csv("../migration/database_sql/data/data_clean/dataset_pulito_stazioni.csv", encoding='latin-1')
    minima = 1000
    id_stazione = 0
    comune = ""
    for i,elem in var.iterrows():
        latitudine = elem["lat"]
        longitudine = elem["lng"]
        dist = numpy.sqrt((latitudine - float(tupla[0]))**2 + (longitudine - float(tupla[1]))**2)
        if dist < minima:
            minima = dist
            id_stazione = elem["Idstazione"]
            comune = elem["Comune"]
    #print(minima, id_stazione, comune)
    return id_stazione
#
# df = var.loc[var['denominazione'] == comune]
# # print(ciao)
# latitudine = df['latitudine'].values[0]
# longitudine = df['longitudine'].values[0]
# tupla = (str(latitudine), str(longitudine))
# print(tupla)
# #Valore preso dalla pagina html
# location = " "
#
# location_stazioni = " "
#
# # SELECT id_stazione, latitudine, longitudine FROM `stazione`;
# # calling the Nominatim tool
# loc = Nominatim(user_agent="GetLoc")
#
# #Individuo la stazione piú vicina alla location inserita
#
# # entering the location name
# getLoc1 = loc.geocode(location)
# print(getLoc1.address)
# getLoc2 = loc.geocode(location2)
# print(getLoc2.address)
#
# # # printing address
# # print(getLoc.address)
#
# # Print the distance calculated in km
# print(geodesic((getLoc1.latitude,getLoc1.longitude), (getLoc2.latitude, getLoc2.longitude) ).km)
# #
# # # printing latitude and longitude
# # print("Latitude = ", getLoc.latitude, "\n")
# # print("Longitude = ", getLoc.longitude)