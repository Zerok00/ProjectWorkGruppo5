import csv

with open("comuni_search_bar.csv", "r", encoding="utf-8") as file:
    lettore = csv.reader(file)
    lista1 = []
    for elem in lettore:
        comune = elem[0].split(",")[0]
        lista1.append(comune)

with open("coordinate_per_comune.CSV", "r", encoding="latin-1") as file2:
    lettore2 = csv.reader(file2)
    lista2 = []
    next(lettore2)
    for elem in lettore2:
        lista2.append(elem[0])

print("Mancanti:")
for elem in lista2:
    if elem not in lista1:
        print(elem)