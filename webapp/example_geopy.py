# importing geopy library
from geopy.geocoders import Nominatim
# Importing the geodesic module from the library
from geopy.distance import geodesic

location1 = "R"

location2 = "Ro"



# calling the Nominatim tool
loc = Nominatim(user_agent="GetLoc")

# entering the location name
getLoc1 = loc.geocode(location1, exactly_one=False)
for elem in getLoc1:
    print(elem.address)
getLoc2 = loc.geocode(location2)
print(getLoc2.address)

# # printing address
# print(getLoc.address)

# Print the distance calculated in km
#print(geodesic((getLoc1.latitude,getLoc1.longitude), (getLoc2.latitude, getLoc2.longitude) ).km)
#
# # printing latitude and longitude
# print("Latitude = ", getLoc.latitude, "\n")
# print("Longitude = ", getLoc.longitude)