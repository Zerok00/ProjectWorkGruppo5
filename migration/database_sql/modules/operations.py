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

    
* Tabella per gestire stazioni
* Pandas con chunksize per gestire 1M record alla volta

Pulizia dati:
1) Pulisco stazioni
2) Creo dizionario da stazioni
3) ciclo file record, elimino NA e mancate corrispondeze con diz stazioni


import pandas as pd
data = pd.read_csv('large_data.csv', chunksize=1000)
for chunk in data:
    # Process each chunk (e.g., filter, transform, analyze)
    # ...

 '''

import pandas as pd

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

def clean_csv_rilevazioni(path_csv_rilevazioni, path_csv_stazioni, new_file_name= 'dataset_pulito_rilevazioni.csv', execute=False):
     if execute:
        #creo path per nuovo file
        new_path = path_csv_rilevazioni.split('\\')
        new_path[-1] = new_file_name
        new_path = "/".join(new_path)

        df_rilevazioni = pd.read_csv(path_csv_rilevazioni)
        df_stazioni = pd.read_csv(path_csv_stazioni)

        # tolgo sensori senza corrispondenze nella tabella stazioni, seleziono colonne e solo righe con rilevamenti validi
        df = df_rilevazioni[df_rilevazioni['IdSensore'].isin(df_stazioni['IdSensore'])]
        df = df.iloc[:,[0,1,2]]
        df = df[df['Valore'] != -9999]

        df.to_csv(new_path, index=False)


def inserimento_stazioni():
    #tabella per gestire stazioni
    #pandas per gestire sensori

    #1) pulisco stazioni. Creo dizionario da stazioni.

    pass

def inserimento_rilevazioni():
     pass