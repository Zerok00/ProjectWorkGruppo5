from modules import queries, connect, operations
from mysql.connector import Error

# creazione db
try:
    connect.create_db(drop=True)

    queries.execute_create_tables()
    
except Error as e:
     print(e)
    # print("\nOperazioni fermate, è già presente un database! \nPer eliminarlo e caricarlo nuovamente utilizzare il parametro 'drop=True'\n")


path = 'data\Stazioni_qualit__dell_aria_20240220.csv'
operations.clean_csv_stazioni(path, execute=False)

path_stazioni = 'data\data_clean\dataset_pulito_stazioni.csv'
path = 'data\Dati_sensori_aria_20240219.csv'
operations.clean_csv_rilevazioni(path, path_stazioni, execute=False)

path_rilevazioni = 'data\data_clean\dataset_pulito_rilevazioni.csv'

operations.inserimento_stazioni(path_stazioni, execute=True)

operations.inserimento_rilevazioni(path_rilevazioni, execute=True)








