from modules import connect, queries, operations
from mysql.connector import Error

try:
    connect.create_db(drop=False)

    queries.create_tables()
    
except Error as e:
     print(e)
    # print("\nOperazioni fermate, è già presente un database! \nPer eliminarlo e caricarlo nuovamente utilizzare il parametro 'drop=True'\n")

path = 'data\lombardia_qa\Stazioni_qualit__dell_aria_20240220.csv'
new_file_name = 'dataset_pulito_stazioni.csv'

new_path = operations.clean_csv_stazioni(path, new_file_name, execute=True)

operations.clean_csv_rilevazioni('data\lombardia_qa\Dati_sensori_aria_20240219.csv', 
                                 'data\lombardia_qa\dataset_pulito_stazioni.csv',
                                 execute=False
                                 )


