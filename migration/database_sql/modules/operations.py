'''
dati sensori:
    0 : IdSensore
    1 : Data
    2 : Valore
    -   3 : validità
    3   + : data_24
    -   4 : operatore

dati stazioni:
    0 : IdSensore
    1 : NomeTipoSensore
    2 : UnitaMisura
    3 : IdStazione
    -       4 : NomeStazione
    4   5 : Quota
    5   6 : Provincia
    6   7 : ComuneI
    -       8 : Storico
    -       9 : DataStart
    -       10 : DataStop
    -       11 : Utm_Nord
    -       12 : Utm_Est
    7   13 : lat
    8   14 : lng
    -       15 : location

Elementi chiave per assicurare efficienza nell'inserimento:
    1) Pulizia dei dati
    2) Uso dataframe pandas divisi in chunks gestibili (circa 1M)
    3) divido i dati in array numpy di tuple con list comprehensions,
    4) una sola select per recuperare dati foreign key
    
    ottimizzazione inserimento rilevazioni e date (circa 3M di records da dividere):
    386 secondi - base, batch 40000 (err. 50000)
    276 secondi - base, batch 40000 (err. 50000), conversione array numpy
    274 secondi - una sola connessione per tutte le operazioni, batch 40000 (err. 50000)
    264 secondi - max_allowed_package=1GB, batch 500000 (err. 1000000)
    121 secondi - drop valori ripetuti, batch 2000000

 '''

import pandas as pd
import numpy as np
import modules.queries
import modules.connect
import mysql.connector
import time

def clean_csv_stazioni(path, new_file_name='data_clean/dataset_pulito_stazioni.csv', execute=False):
    if execute:
        # creo path per nuovo file
        new_path = path.split('\\')
        new_path[-1] = new_file_name
        new_path = "/".join(new_path)
        
        #tolgo sensori che hanno smesso di funzionare e seleziono righe
        df = pd.read_csv(path)

        df.loc[df["Quota"].isnull(), "Quota"] = 0 #correzione per schivenoglia malpasso........

        df = df[df['DataStop'].isnull()]
        df = df.loc[:, [
            'IdSensore',
            'NomeTipoSensore',
            'UnitaMisura',
            'Idstazione',
            'Quota',
            'Provincia',
            'Comune',
            'lat',
            'lng'
        ]]
        df.to_csv(new_path, index=False)

        return new_path

def clean_csv_rilevazioni(path, path_csv_stazioni, new_file_name='data_clean/dataset_pulito_rilevazioni.csv', execute=False):
     if execute:
        #creo path per nuovo file
        new_path = path.split('\\')
        new_path[-1] = new_file_name
        new_path = "/".join(new_path)

        df_rilevazioni = pd.read_csv(path)
        df_stazioni = pd.read_csv(path_csv_stazioni)

        # tolgo sensori senza corrispondenze nella tabella stazioni, seleziono colonne e solo righe con rilevamenti validi
        df = df_rilevazioni[df_rilevazioni['IdSensore'].isin(df_stazioni['IdSensore'])]
        df = df.loc[:,[
            'IdSensore',
            'NomeTipoSensore',
            'UnitaMisura'
        ]]
        df = df[df['Valore'] != -9999]

        df.to_csv(new_path, index=False)

def diz_chiavi(query):
    connection = modules.connect.create_db_connection()
    cursor = connection.cursor()

    cursor.execute(query)
    rows = cursor.fetchall()
    result = {line[1] : line[0] for line in rows}

    cursor.close()
    connection.close()

    return result


def diz_chiavi_batch(query, connection, cursor):

    cursor.execute(query)
    rows = cursor.fetchall()
    result = {line[1] : line[0] for line in rows}
    return result

def get_freq(NomeTipoSensore):

    pass


def inserimento_stazioni(path_csv_stazioni, execute=False):
    if execute:
        df = pd.read_csv(path_csv_stazioni) 

        connection = modules.connect.create_db_connection()
        cursor = connection.cursor()
        
        # provincia
        lista_tuple = [(
            row['Provincia'],
            ) for i, row in df.iterrows()
        ]
        query = modules.queries.insert_provincia()
        modules.connect.execute_batch(query, lista_tuple, connection, cursor)

        # comune
        query = "SELECT id_provincia, nome FROM provincia;"
        chiavi = diz_chiavi_batch(query, connection, cursor)
        lista_tuple = [(
            row['Comune'],
            chiavi[row['Provincia']],
            ) for i, row in df.iterrows()
        ]
        query = modules.queries.insert_comune()
        modules.connect.execute_batch(query, lista_tuple, connection, cursor)

        # stazione - no auto_increment
        query = "SELECT id_comune, nome FROM comune;"
        chiavi = diz_chiavi_batch(query, connection, cursor)
        lista_tuple = [(
            row['Idstazione'],
            row['Quota'],
            chiavi[row['Comune']],
            row['lat'],
            row['lng'],
            ) for i, row in df.iterrows()
        ]
        query = modules.queries.insert_stazione()
        modules.connect.execute_batch(query, lista_tuple, connection, cursor)

        # tipologia
        lista_tuple = [(
            row['NomeTipoSensore'],
            row['UnitaMisura'],
            ) for i, row in df.iterrows()
        ]
        query = modules.queries.insert_tipologia()
        modules.connect.execute_batch(query, lista_tuple, connection, cursor)

        # sensore - no auto_increment | frequenza al momento è null
        query = "SELECT id_tipologia, nome FROM tipologia;"
        chiavi = diz_chiavi_batch(query, connection, cursor)
        lista_tuple = [(
            row['IdSensore'],
            row['Idstazione'],
            chiavi[row['NomeTipoSensore']],
            # frequenza
            # gruppo
            ) for i, row in df.iterrows()
        ]
        query = modules.queries.insert_sensore()
        modules.connect.execute_batch(query, lista_tuple, connection, cursor)


        cursor.close()
        connection.close()

        print("Caricamento dati stazioni completato")


def inserimento_rilevazioni(path_csv_rilevazioni, execute=False):
    if execute:
        start = time.time()

        connection = modules.connect.create_db_connection()
        cursor = connection.cursor()

        query = "SET GLOBAL max_allowed_packet=1073741824;"
        cursor.execute(query)

        dim = 2000000

        print("Caricamento dati rilevazioni in corso...")

        df = pd.read_csv(path_csv_rilevazioni, chunksize=dim) 

        query_select = "SELECT id_data_rilevazione, data FROM data_rilevazione;"

        for chunk in df:

            chunk_data = chunk.copy()
            chunk_data = chunk_data.drop_duplicates(subset=['Data'])

            chunk_data['Data_24'] = pd.to_datetime(chunk_data['Data'], format='%d/%m/%Y %I:%M:%S %p')
            chunk_data['Data_24'] = chunk_data['Data_24'].dt.strftime('%Y/%m/%d %H:%M:%S')

            # data rilevazione
            lista_tuple = list({(
                row['Data'],
                row['Data_24'],
                ) for i, row in chunk_data.iterrows()
            })
            query = modules.queries.insert_data_rilevazione()
            modules.connect.execute_batch(query, lista_tuple, connection, cursor)

            # rilevazione
            chunk = chunk.to_numpy()
            chiavi = diz_chiavi_batch(query_select, connection, cursor)
            lista_tuple = [(
                row[0], # IdSensore
                chiavi[row[1]], #row[1] = Data
                row[2], # Valore
                ) for row in chunk
            ]
            query = modules.queries.insert_rilevazione()
            modules.connect.execute_batch(query, lista_tuple, connection, cursor)

        cursor.close()
        connection.close()

        print("Caricamento dati rilevazioni completato")

        end = time.time()
        print(f"tempo impiegato: {end - start}")

     