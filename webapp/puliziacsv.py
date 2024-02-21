import csv

with open("../database/dati/lombardia_qa/dati_sensori_puliti.CSV", "r") as file:
    lettore = csv.reader(file)
    next(lettore)
    for elem in lettore:
