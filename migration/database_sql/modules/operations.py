'''
dati sensori:
    0 : IdSensore
    1 : Data
    2 : Valore
    -   3 : validità
    -   4 : operatore

dati stazioni:
    0 : IdSensore
    1 : Tipologia
    2 : Unità di misura
    3 : IdStazione
    -   4 : NomeStazione
    5 : Quota
    6 : Provincia
    7 : Comune
    -   8 : Storico
    -   9 : DataStart
    -   10 : DataStop
    -   11 : Utm_Nord
    -   12 : Utm_Est
    13 : lat
    14 : lng
    -   15 : location

Elementi chiave per assicurare efficienza nell'inserimento:
    1) Pulizia dei dati
    2) Uso dataframe pandas divisi in chunks gestibili (circa 1M)
    3) divido i dati in array numpy di tuple con list comprehensions


import pandas as pd
data = pd.read_csv('large_data.csv', chunksize=1000)
for chunk in data:
    # Process each chunk (e.g., filter, transform, analyze)
    # ...

 '''

import pandas as pd
import numpy as np
import modules.queries
import modules.connect
import csv

def clean_csv_stazioni(path, new_file_name='dataset_pulito_stazioni.csv', execute=False):
    if execute:
        # creo path per nuovo file
        new_path = path.split('\\')
        new_path[-1] = new_file_name
        new_path = "/".join(new_path)
        
        #tolgo sensori che hanno smesso di funzionare e seleziono righe
        df = pd.read_csv(path)
        df = df[df['DataStop'].isnull()]
        df = df.iloc[:, [0, 1, 2, 3, 5, 6, 7, 13, 14]]
        df.to_csv(new_path, index=False)

        return new_path

def clean_csv_rilevazioni(path, path_csv_stazioni, new_file_name='dataset_pulito_rilevazioni.csv', execute=False):
     if execute:
        #creo path per nuovo file
        new_path = path.split('\\')
        new_path[-1] = new_file_name
        new_path = "/".join(new_path)

        df_rilevazioni = pd.read_csv(path)
        df_stazioni = pd.read_csv(path_csv_stazioni)

        # tolgo sensori senza corrispondenze nella tabella stazioni, seleziono colonne e solo righe con rilevamenti validi
        df = df_rilevazioni[df_rilevazioni['IdSensore'].isin(df_stazioni['IdSensore'])]
        df = df.iloc[:,[0,1,2]]
        df = df[df['Valore'] != -9999]

        df.to_csv(new_path, index=False)


def inserimento_stazioni(path_csv_stazioni, execute=False):
    if execute:
        df = pd.read_csv(path_csv_stazioni)
        
        df = df.to_numpy()
        
        # provincia
        lista_tuple = [tuple(i[6]) for i in df]
        query = modules.queries.insert_provincia()
        modules.connect.execute_many(query, lista_tuple)

        # comune
        lista_tuple = [tuple(i[7], ) for i in df]
        query = modules.queries.insert_comune()
        modules.connect.execute_many(query, lista_tuple)

        # stazione - no auto increment
        lista_tuple = [tuple(i[1]) for i in df]
        query = modules.queries.insert_stazione()
        modules.connect.execute_many(query, lista_tuple)

        # tipologia1
        lista_tuple = [tuple(i[1]) for i in df]
        query = modules.queries.insert_tipologia()
        modules.connect.execute_many(query, lista_tuple)

        # sensore - no auto_increment
        lista_tuple = [tuple(i[1]) for i in df]
        query = modules.queries.insert_sensore()
        modules.connect.execute_many(query, lista_tuple)


def test_province(path_csv_stazioni, execute=False):
    if execute:
        with open(path_csv_stazioni, "r") as file:
            lettore = csv.reader(file)
            next(lettore)

            c = 1
            diz_province = {}
            set_province = set()

            for elem in lettore:
                if elem[5] not in set_province:
                    set_province.add(elem[5])
                    diz_prova = {"id" : c, "lista_comuni" : [] }
                    diz_province[elem[5]] = diz_prova

                    c+=1
            
            print(diz_province)
        



def inserimento_rilevazioni():
     pass