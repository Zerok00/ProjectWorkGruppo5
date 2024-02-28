# importing geopy library
from geopy.geocoders import Nominatim
# Importing the geodesic module from the library
from geopy.distance import geodesic


#Valore preso dalla pagina html
location = " "

location_stazioni = " "

# SELECT id_stazione, latitudine, longitudine FROM `stazione`;
# calling the Nominatim tool
loc = Nominatim(user_agent="GetLoc")

#Individuo la stazione piú vicina alla location inserita

# entering the location name
getLoc1 = loc.geocode(location)
print(getLoc1.address)
getLoc2 = loc.geocode(location2)
print(getLoc2.address)

# # printing address
# print(getLoc.address)

# Print the distance calculated in km
print(geodesic((getLoc1.latitude,getLoc1.longitude), (getLoc2.latitude, getLoc2.longitude) ).km)
#
# # printing latitude and longitude
# print("Latitude = ", getLoc.latitude, "\n")
# print("Longitude = ", getLoc.longitude)