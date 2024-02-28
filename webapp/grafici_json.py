import json
import csv

with open('prova_json.csv', mode='r') as file:
    reader = csv.reader(file, delimiter=',')
    next(reader)
    lista = list(reader)

print(lista)

# Read JSON data from a file
with open('Plot 4.json', 'r') as file:
    data = json.load(file)

x = []
y = []

for i in range(len(lista)):
    x.append(lista[i][0])
    y.append(lista[i][1])

# Modify the JSON
data['data']['x'] = x
data['data']['y'] = y

# Write the modified JSON data back to the file
with open('Plot_4_modificato.json', 'w') as file:
    json.dump(data, file, indent=4)