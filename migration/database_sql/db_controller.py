from modules import queries, connect, operations
from mysql.connector import Error

# creazione db
try:
    connect.create_db(drop=True)

    queries.execute_create_tables()
    
except Error as e:
     print(e)
    # print("\nOperazioni fermate, è già presente un database! \nPer eliminarlo e caricarlo nuovamente utilizzare il parametro 'drop=True'\n")


path = 'data\lombardia_qa\Stazioni_qualit__dell_aria_20240220.csv'
operations.clean_csv_stazioni(path, execute=False)

path_stazioni = 'data\lombardia_qa\dataset_pulito_stazioni.csv'
path = 'data\lombardia_qa\Dati_sensori_aria_20240219.csv'
operations.clean_csv_rilevazioni(path, path_stazioni, execute=False)


operations.inserimento_stazioni(path_stazioni, execute=False)

operations.test_province(path_stazioni, execute=True)






