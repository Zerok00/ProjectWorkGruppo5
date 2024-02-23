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
    -       4 : NomeStazione
    4   5 : Quota
    5   6 : Provincia
    6   7 : Comune
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
    3) divido i dati in array numpy di tuple con list comprehensions

Problema: come recupero foreign key mantenendo inserimenti efficienti ed interrogazioni al minimo?

    Soluzione 1) Non interrogo DB del tuto e uso un trigger per recuperare la chiave.
                Non possibile, le relazioni fra tabelle è arbitraria, mi serve info su csv
                e non posso fare affidamento sull'ordine per dati unique

    Soluzione 2) Una singola interrogazione dopo ogni inserimento per costruire un dizionario di chiavi primarie

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
        df = df.iloc[:, [0, 1, 2, 3, 5, 6, 7, 13, 14]]
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
        df = df.iloc[:,[0,1,2]]
        df = df[df['Valore'] != -9999]

        df.to_csv(new_path, index=False)


def diz_chiavi(query):
    connection = modules.connect.create_db_connection()
    cursor = connection.cursor()

    cursor.execute(query)
    rows = cursor.fetchall()
    result = {line[1] : line[0] for line in rows}

    return result


def inserimento_stazioni(path_csv_stazioni, execute=False):
    if execute:
        df = pd.read_csv(path_csv_stazioni) 
        df = df.to_numpy()
        
        # provincia
        lista_tuple = [(i[5],) for i in df]
        query = modules.queries.insert_provincia()
        modules.connect.execute_many(query, lista_tuple)

        # comune
        query = "SELECT id_provincia, nome FROM provincia;"
        chiavi = diz_chiavi(query)
        lista_tuple = [(i[6], chiavi[i[5]],) for i in df]
        query = modules.queries.insert_comune()
        modules.connect.execute_many(query, lista_tuple)

        # stazione - no auto_increment
        query = "SELECT id_comune, nome FROM comune;"
        chiavi = diz_chiavi(query)
        lista_tuple = [(i[3], i[4], chiavi[i[6]], i[7], i[8],) for i in df]
        query = modules.queries.insert_stazione()
        modules.connect.execute_many(query, lista_tuple)

        # tipologia
        lista_tuple = [(i[1], i[2],) for i in df]
        query = modules.queries.insert_tipologia()
        modules.connect.execute_many(query, lista_tuple)

        # sensore - no auto_increment | frequenza al momento è null
        query = "SELECT id_tipologia, nome FROM tipologia;"
        chiavi = diz_chiavi(query)
        lista_tuple = [(i[0], i[3], chiavi[i[1]],) for i in df]
        query = modules.queries.insert_sensore()
        modules.connect.execute_many(query, lista_tuple)

        print("Caricamento dati stazioni completato")


def inserimento_rilevazioni(path_csv_rilevazioni, execute=False):
    if execute:
        dim = 40000

        start = time.time()

        print("Caricamento dati rilevazioni in corso...")

        df = pd.read_csv(path_csv_rilevazioni, chunksize=dim) 

        for chunk in df:
            chunk = chunk.to_numpy()
            
            # data rilevazione
            lista_tuple = [(i[1],) for i in chunk]
            query = modules.queries.insert_data_rilevazione()
            modules.connect.execute_many(query, lista_tuple)

            # rilevazione
            query = "SELECT id_data_rilevazione, data FROM data_rilevazione;"
            chiavi = diz_chiavi(query)
            lista_tuple = [(i[0], chiavi[i[1]], i[2],) for i in chunk]
            query = modules.queries.insert_rilevazione()
            modules.connect.execute_many(query, lista_tuple)

        print("Caricamento dati rilevazioni completato")


        end = time.time()
        print(f"tempo impiegato: {end - start}")

     