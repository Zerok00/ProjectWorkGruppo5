#Funzione per la creazione della lista dei comuni accettabili
import csv
# importing geopy library
#from geopy.geocoders import Nominatim
# Importing the geodesic module from the library
#from geopy.distance import geodesic

with open('comuni_accettabili.txt', mode='r') as tsv_file:
    tsv_reader = csv.reader(tsv_file, delimiter='\t')
    next(tsv_reader)
    lista_comuni = list(tsv_reader)

with open('comuni_search_bar.csv', mode='w', newline="") as file:
    writer = csv.writer(file)
    for riga in lista_comuni:
        print(riga[0])
        writer.writerow([riga[0] + ", " + riga[1],])

# print(lista_comuni)
# print(len(lista_comuni))

'''
# calling the Nominatim tool
loc = Nominatim(user_agent="GetLoc")

lista_problemi = []
for elem in lista_comuni:
    getLoc = loc.geocode(elem[0], timeout=10)
    indirizzo = getLoc.address
    if "Lombardia" not in indirizzo or indirizzo == "":
        lista_problemi.append((indirizzo, elem))
    print(indirizzo)
    print(lista_problemi)

print(lista_problemi)'''


