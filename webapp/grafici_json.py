import json
import csv

with open('prova_json.csv', mode='r') as file:
    reader = csv.reader(file, delimiter=',')
    next(reader)
    lista = list(reader)

print(lista)

# Read JSON data from a file
with open('plot.json', 'r') as file:
    data = json.load(file)

y = []
x = []

for i in range(len(lista)):
    x.append(lista[i][0])
    y.append(lista[i][1])

# Modify the JSON
data['data'][0]['x'] = x
data['data'][0]['y'] = y

# Write the modified JSON data back to the file
with open('json_grafici/plot_dati.json', 'w') as file:
    json.dump(data, file, indent=4)