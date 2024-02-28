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

def clean_csv_stazioni(path, new_file_name=f'data_clean/dataset_pulito_stazioni.csv', i="", execute=False):
    # creo path per nuovo file
    new_path = path.split('\\')
    new_path[-1] = new_file_name
    new_path = "/".join(new_path)
    new_path = new_path.split(".")
    new_path = new_path[-2] + i + "." + new_path[-1]
    
    if execute:
        #tolgo sensori che hanno smesso di funzionare e seleziono righe
        df = pd.read_csv(path)

        df.loc[df["Quota"].isnull(), "Quota"] = 0 #correzione per quota schivenoglia malpasso........

        # se ho campo NomeTipoSensore, unico delle stazioni inquinamento
        if 'NomeTipoSensore' in df:
            df.rename(columns={'Idstazione': 'IdStazione'}, inplace=True)
            df = df[df['DataStop'].isnull()]
            df = df.loc[:, [
                'IdSensore',
                'NomeTipoSensore',
                'UnitaMisura',
                'IdStazione',
                'Quota',
                'Provincia',
                'Comune',
                'lat',
                'lng'
            ]]

        if 'Tipologia' in df:
            df.rename(columns={
                'Unità DiMisura' : 'UnitaMisura', 
                'Tipologia' : 'NomeTipoSensore', 
                'NomeStazione' : 'Comune'}, 
                inplace=True)
            
            lista_descrizioni = [
                " v.", " via", " Via", " viale", " P.zza", " p.zza", " SS", " SP", " campo", " Campo", 
                " cascina", " Passo", " Parco", " Monte",  " Case", " rifugio", " Piani", 
                " ponte", " -", " ENEL", " tetto", " eliporto", " Cav", " Poggio", 
                " centro", "Cascina", " Ist.", " Lago", " Acquedotto", " JRC", " SMR"
            ]
            
            for i, row in df.iterrows():
                for elem in lista_descrizioni:
                    comune = row['Comune'].split(elem)
                    if len(comune) >= 2:
                        comune = comune[0]
                        break
                    else:
                        comune = str(comune).strip("[]'\" ")

                df.loc[i, "Comune"] = comune
            
            df = df[df['Comune'] != ""]

            df = df.loc[:, [
                'IdSensore',
                'NomeTipoSensore',
                'UnitaMisura',
                'IdStazione',
                'Quota',
                'Provincia',
                'Comune',
                'lat',
                'lng'
            ]]

        df.to_csv(new_path, index=False)

    return new_path


def clean_csv_rilevazioni(path, path_csv_stazioni, new_file_name='data_clean/dataset_pulito_rilevazioni.csv', i="", execute=False):
    new_path = path.split('\\')
    new_path[-1] = new_file_name
    new_path = "/".join(new_path)
    new_path = new_path.split(".")
    new_path = new_path[-2] + i + "." + new_path[-1]

    if execute:    
        df_stazioni = pd.read_csv(path_csv_stazioni)
        df_rilevazioni_tot = pd.read_csv(path, dtype={
            'IdSensore':'int32', 
            'Data': 'object', 
            'Valore':'float32', 
            'Stato':'str', 
            'IdOperatore':'int8'}, chunksize=4000000)

        # svuoto csv per permettere di eseguire append alla fine di ognuno dei successivi for 
        df = pd.DataFrame()
        df_concat = pd.DataFrame()
        df.to_csv(new_path, index=False)

        # garantisco presenza di solo un header mettendolo false al primo ciclo
        header = True
        for df_rilevazioni in df_rilevazioni_tot:
            # tolgo sensori senza corrispondenze nella tabella stazioni, seleziono colonne e solo righe con rilevamenti validi
            df = df_rilevazioni[df_rilevazioni['IdSensore'].isin(df_stazioni['IdSensore'])]

            df = df[(df['idOperatore'] != 3) & (df['idOperatore'] != 4)]

            df = df.loc[:, [
                'IdSensore',
                'Data',
                'Valore'
            ]]

            df = df[(df['Valore'] != -9999) & (df['Valore'] != -999)]

            df_concat = pd.concat([df_concat, df])

        filtro_frequenze = df_concat.copy()
        # ottengo una serie che raggruppa la somma delle rilevazioni per sensore
        filtro_frequenze = filtro_frequenze.groupby(['IdSensore'])['IdSensore'].count()
        # ritrasformo la serie in dataframe
        filtro_frequenze= pd.DataFrame({'IdSensore':filtro_frequenze.index, 'NumeroRilevazioni':filtro_frequenze.values})
        tipo_sensore = df_stazioni.copy()
        tipo_sensore = tipo_sensore.loc[:, [
            'NomeTipoSensore',
            'IdSensore'
        ]]

        filtro_sequenze = pd.merge(filtro_frequenze, tipo_sensore, on='IdSensore', how='left')
        # filtro database togliendo sensori funzionanti ma con rilevazioni parziali
        filtro_sequenze = filtro_sequenze[
            (((filtro_sequenze['NomeTipoSensore'] == 'Biossido di Azoto') 
            | (filtro_sequenze['NomeTipoSensore'] == 'Biossido di Zolfo') 
            | (filtro_sequenze['NomeTipoSensore'] == 'Ozono') 
            | (filtro_sequenze['NomeTipoSensore'] == 'Monossido di Carbonio')) 
            & (filtro_sequenze['NumeroRilevazioni'] > 7000
            ))
            |
            (((filtro_sequenze['NomeTipoSensore'] == 'PM10 (SM2005)') 
            | (filtro_sequenze['NomeTipoSensore'] == 'Particelle sospese PM2.5')) 
            & (filtro_sequenze['NumeroRilevazioni'] > 200
            ))
            |
            (((filtro_sequenze['NomeTipoSensore'] == 'Umidità Relativa')
            | (filtro_sequenze['NomeTipoSensore'] == 'Direzione Vento')
            | (filtro_sequenze['NomeTipoSensore'] == 'Temperatura')
            | (filtro_sequenze['NomeTipoSensore'] == 'Velocità Vento')
            | (filtro_sequenze['NomeTipoSensore'] == 'Precipitazione')
            | (filtro_sequenze['NomeTipoSensore'] == 'Radiazione Globale'))
            & (filtro_sequenze['NumeroRilevazioni'] > 29000
            ))
        ]
        
        df_concat = df_concat[df_concat['IdSensore'].isin(filtro_sequenze['IdSensore'])]

        df_split = np.array_split(df_concat, 16)
        for split in df_split:
            split.to_csv(new_path, header=header, index=False, mode='a')
            header = False

        # df_concat.to_csv(new_path, header=header, index=False)

    return new_path


def get_frequenza(NomeTipoSensore):
    freq_oraria = 24
    freq_giornaliera = 1
    intervallo_10_min = 144
    
    match NomeTipoSensore:
        case 'Biossido di Azoto':
            return freq_oraria
        case 'Biossido di Zolfo':
            return freq_oraria
        case 'Ozono':
            return freq_oraria
        case 'Monossido di Carbonio':
            return freq_oraria
        
        case 'PM10 (SM2005)':
            return freq_giornaliera
        case 'Particelle sospese PM2.5':
            return freq_giornaliera
        
        case 'Umidità Relativa':
            return intervallo_10_min
        case 'Direzione Vento':
            return intervallo_10_min
        case 'Temperatura':
            return intervallo_10_min
        case 'Velocità Vento':
            return intervallo_10_min
        case 'Precipitazione':
            return intervallo_10_min
        case 'Radiazione Globale':
            return intervallo_10_min

        
def get_ambito(NomeTipoSensore):
    inquinamento = 'Inquinamento'
    meteo = 'Meteo'

    match NomeTipoSensore:
        case 'Biossido di Azoto':
            return inquinamento
        case 'Biossido di Zolfo':
            return inquinamento
        case 'Ozono':
            return inquinamento
        case 'Monossido di Carbonio':
            return inquinamento
        case 'PM10 (SM2005)':
            return inquinamento
        case 'Particelle sospese PM2.5':
            return inquinamento

        case 'Umidità Relativa':
            return meteo
        case 'Direzione Vento':
            return meteo
        case 'Temperatura':
            return meteo
        case 'Velocità Vento':
            return meteo
        case 'Precipitazione':
            return meteo
        case 'Radiazione Globale':
            return meteo


def diz_chiavi_batch(query, connection, cursor):

    cursor.execute(query)
    rows = cursor.fetchall()
    result = {line[1] : line[0] for line in rows}
    return result

def inserimento_stazioni(path_csv_stazioni, path_csv_rilevazioni, execute=False):
    if execute:
        df = pd.read_csv(path_csv_stazioni) 

        connection = modules.connect.create_db_connection()
        cursor = connection.cursor()

        df_rilevazioni = pd.read_csv(path_csv_rilevazioni, chunksize=4000000)
        for chunk in df_rilevazioni:
            df = df[df['IdSensore'].isin(chunk['IdSensore'])]

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
            row['IdStazione'],
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

        # sensore - no auto_increment
        query = "SELECT id_tipologia, nome FROM tipologia;"
        chiavi = diz_chiavi_batch(query, connection, cursor)
        lista_tuple = [(
            row['IdSensore'],
            row['IdStazione'],
            chiavi[row['NomeTipoSensore']],
            get_frequenza(row['NomeTipoSensore']), 
            get_ambito(row['NomeTipoSensore'])
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

        print("Caricamento dati rilevazioni in corso...")

        query_select = "SELECT id_data_rilevazione, data FROM data_rilevazione;"


        query = "SET GLOBAL max_allowed_packet=1073741824;"
        cursor.execute(query)

        dim = 2000000

        df = pd.read_csv(path_csv_rilevazioni, chunksize=dim) 
        df_filtrato = pd.DataFrame()
        for chunk in df:
            chunk_data = chunk.copy()
            chunk_data = chunk_data.drop_duplicates(subset=['Data'])

            df_filtrato = pd.concat([df_filtrato, chunk_data])
            df_filtrato = df_filtrato.drop_duplicates(subset=['Data'])


        df_filtrato['Data_24'] = pd.to_datetime(df_filtrato['Data'], format='%d/%m/%Y %I:%M:%S %p')
        df_filtrato['Data_24'] = df_filtrato['Data_24'].dt.strftime('%Y/%m/%d %H:%M:%S')

        print(df_filtrato)

        # data rilevazione
        lista_tuple = list({(
            row['Data'],
            row['Data_24'],
            ) for i, row in df_filtrato.iterrows()
        })

        query = modules.queries.insert_data_rilevazione()
        modules.connect.execute_batch(query, lista_tuple, connection, cursor)

        df = pd.read_csv(path_csv_rilevazioni, chunksize=dim) 
        for chunk in df:
            # rilevazione
            chunk = chunk.to_numpy()
            chiavi = diz_chiavi_batch(query_select, connection, cursor)

            # print(chiavi)

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

     