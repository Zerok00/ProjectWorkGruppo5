from modules import queries, connect, operations
from mysql.connector import Error

# creazione db
try:
    connect.create_db(drop=True)

    queries.execute_create_tables()
    
except Error as e:
     print(e)
    # print("\nOperazioni fermate, è già presente un database! \nPer eliminarlo e caricarlo nuovamente utilizzare il parametro 'drop=True'\n")


path_qa = 'data\Stazioni_qualit__dell_aria_20240220.csv'
path_stazioni_qa = operations.clean_csv_stazioni(
    path_qa, 
    i="_qa", 
    execute=True
)

path_qa = 'data\Dati_sensori_aria_20240219.csv'
path_rilevazioni_qa = operations.clean_csv_rilevazioni(
    path_qa, 
    path_stazioni_qa, 
    i="_qa", 
    execute=True
)

operations.inserimento_stazioni(path_stazioni_qa, path_rilevazioni_qa, execute=True)
operations.inserimento_rilevazioni(path_rilevazioni_qa, execute=True)


path_meteo = 'data\stazioni_meteo.csv'
path_stazioni_meteo = operations.clean_csv_stazioni(
    path_meteo, 
    i="_meteo", 
    execute=False
)

path_meteo = 'data\Dati_sensori_meteo_20240220.csv'
path_rilevazioni_meteo = operations.clean_csv_rilevazioni(
    path_meteo, 
    path_stazioni_meteo, 
    i="_meteo", 
    execute=False
)

operations.inserimento_stazioni(path_stazioni_meteo, path_rilevazioni_meteo, execute=False)
operations.inserimento_rilevazioni(path_rilevazioni_meteo, execute=False)
